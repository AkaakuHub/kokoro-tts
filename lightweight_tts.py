#!/usr/bin/env python3
"""
軽量Kokoro-82M TTS実装
弱いCPU向けに最適化されたスタンドアロンサーバー
"""

import os
import io
import gc
import threading
from functools import lru_cache
from flask import Flask, request, jsonify, send_file
import soundfile as sf

# CPUコア数を自動検出して最大活用
import multiprocessing
cpu_count = multiprocessing.cpu_count()
os.environ['OMP_NUM_THREADS'] = str(cpu_count)
os.environ['MKL_NUM_THREADS'] = str(cpu_count)

try:
    from kokoro import KPipeline
except ImportError:
    print("kokoroライブラリが必要です。pip install kokoro>=0.9.4")
    exit(1)

app = Flask(__name__)

# グローバル変数でパイプラインをキャッシュ
_pipeline = None
_pipeline_lock = threading.Lock()

@lru_cache(maxsize=1)
def get_pipeline(lang_code='a'):
    """パイプラインをキャッシュして再利用"""
    global _pipeline
    if _pipeline is None:
        with _pipeline_lock:
            if _pipeline is None:
                print(f"Kokoroパイプライン初期化中... (言語: {lang_code})")
                _pipeline = KPipeline(lang_code=lang_code)
                print("初期化完了")
    return _pipeline

@app.route('/health', methods=['GET'])
def health_check():
    """ヘルスチェック"""
    return jsonify({"status": "ok", "model": "Kokoro-82M"})

@app.route('/tts', methods=['POST'])
def text_to_speech():
    """テキスト音声変換エンドポイント"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "textフィールドが必要です"}), 400
        
        text = data['text']
        voice = data.get('voice', 'af_heart')  # デフォルト音声
        speed = data.get('speed', 1.0)  # 速度調整
        
        if len(text) > 1000:  # 長いテキストを制限
            return jsonify({"error": "テキストが長すぎます（1000文字以下）"}), 400
        
        print(f"TTS生成中: {text[:50]}...")
        
        # パイプライン取得
        pipeline = get_pipeline()
        
        # 音声生成
        audio_generator = pipeline(text, voice=voice, speed=speed)
        
        # 音声チャンクを収集
        audio_chunks = []
        for chunk in audio_generator:
            if chunk is not None:
                audio_chunks.append(chunk)
        
        if not audio_chunks:
            return jsonify({"error": "音声生成に失敗しました"}), 500
        
        # 音声データを結合
        import numpy as np
        if len(audio_chunks) == 1:
            audio_data = audio_chunks[0]
        else:
            audio_data = np.concatenate(audio_chunks, axis=0)
        
        # numpy配列であることを確認
        if not isinstance(audio_data, np.ndarray):
            audio_data = np.array(audio_data, dtype=np.float32)
        
        # 1次元配列に変換（必要に応じて）
        if audio_data.ndim > 1:
            audio_data = audio_data.flatten()
        
        print(f"音声データ形状: {audio_data.shape}, データ型: {audio_data.dtype}")
        
        # メモリ上でWAVファイル作成
        buffer = io.BytesIO()
        sf.write(buffer, audio_data, 24000, format='WAV')
        buffer.seek(0)
        
        # メモリ解放
        del audio_data, audio_chunks
        gc.collect()
        
        return send_file(
            buffer,
            mimetype='audio/wav',
            as_attachment=True,
            download_name='output.wav'
        )
        
    except Exception as e:
        print(f"エラー: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/voices', methods=['GET'])
def list_voices():
    """利用可能な音声一覧"""
    voices = [
        'af_heart', 'af_sky', 'af_grace', 'af_heaven',
        'am_adam', 'am_mike', 'bf_iris', 'bf_rose'
    ]
    return jsonify({"voices": voices})

if __name__ == '__main__':
    print("Kokoro-82M軽量TTSサーバー起動中...")
    print("最適化設定:")
    print(f"- 検出CPUコア数: {cpu_count}")
    print(f"- 使用スレッド数: {os.environ.get('OMP_NUM_THREADS')}")
    print("- メモリ最適化: 有効")
    print("- パイプラインキャッシュ: 有効")
    
    # 開発用サーバー（本番ではwaitress使用推奨）
    app.run(host='0.0.0.0', port=8000, debug=False, threaded=True)