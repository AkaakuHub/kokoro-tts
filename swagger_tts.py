#!/usr/bin/env python3
"""
Swagger UI付きKokoro-82M TTS API
"""

import os
import io
import gc
import threading
import multiprocessing
from functools import lru_cache
from flask import Flask, request, send_file
from flask_restx import Api, Resource, fields
import soundfile as sf

# CPUコア数を自動検出して最大活用
cpu_count = multiprocessing.cpu_count()
os.environ['OMP_NUM_THREADS'] = str(cpu_count)
os.environ['MKL_NUM_THREADS'] = str(cpu_count)

try:
    from kokoro import KPipeline
except ImportError:
    print("kokoroライブラリが必要です。pip install kokoro>=0.9.4")
    exit(1)

app = Flask(__name__)
api = Api(
    app,
    version='1.0',
    title='Kokoro-82M TTS API',
    description='軽量音声合成API - Swagger UIから音声テスト可能',
    doc='/'  # ルートパスでSwagger UIを表示
)

# API名前空間
ns = api.namespace('tts', description='音声合成操作')

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

# APIモデル定義
tts_model = api.model('TTSRequest', {
    'text': fields.String(required=True, description='音声化するテキスト', example='こんにちは、これはテストです。'),
    'voice': fields.String(required=False, description='音声タイプ', default='af_heart', 
                          enum=['af_heart', 'af_sky', 'af_grace', 'af_heaven', 'am_adam', 'am_mike', 'bf_iris', 'bf_rose']),
    'speed': fields.Float(required=False, description='再生速度', default=1.0, min=0.5, max=2.0)
})

health_model = api.model('HealthResponse', {
    'status': fields.String(description='サービス状態'),
    'model': fields.String(description='使用モデル')
})

voices_model = api.model('VoicesResponse', {
    'voices': fields.List(fields.String, description='利用可能な音声一覧')
})

@ns.route('/health')
class Health(Resource):
    @api.doc('health_check')
    @api.marshal_with(health_model)
    def get(self):
        """ヘルスチェック"""
        return {"status": "ok", "model": "Kokoro-82M"}

@ns.route('/voices')
class Voices(Resource):
    @api.doc('list_voices')
    @api.marshal_with(voices_model)
    def get(self):
        """利用可能な音声一覧"""
        voices = [
            'af_heart', 'af_sky', 'af_grace', 'af_heaven',
            'am_adam', 'am_mike', 'bf_iris', 'bf_rose'
        ]
        return {"voices": voices}

@ns.route('/generate')
class TTSGenerate(Resource):
    @api.doc('text_to_speech')
    @api.expect(tts_model)
    @api.produces(['audio/wav'])
    def post(self):
        """テキストを音声に変換
        
        音声ファイル（WAV形式）を生成して返します。
        Swagger UIの「Try it out」ボタンでテスト可能です。
        """
        try:
            data = request.get_json()
            if not data or 'text' not in data:
                api.abort(400, "textフィールドが必要です")
            
            text = data['text']
            voice = data.get('voice', 'af_heart')
            speed = data.get('speed', 1.0)
            
            if len(text) > 1000:
                api.abort(400, "テキストが長すぎます（1000文字以下）")
            
            print(f"TTS生成中: {text[:50]}...")
            
            # パイプライン取得
            pipeline = get_pipeline()
            
            # 音声生成
            audio_generator = pipeline(text, voice=voice, speed=speed)
            audio_data = next(audio_generator)
            
            # メモリ上でWAVファイル作成
            buffer = io.BytesIO()
            sf.write(buffer, audio_data, 24000, format='WAV')
            buffer.seek(0)
            
            # メモリ解放
            del audio_data
            gc.collect()
            
            return send_file(
                buffer,
                mimetype='audio/wav',
                as_attachment=True,
                download_name=f'kokoro_output_{voice}.wav'
            )
            
        except Exception as e:
            print(f"エラー: {str(e)}")
            api.abort(500, str(e))

# ルートパスはSwagger UIが自動的に処理します

if __name__ == '__main__':
    print("Kokoro-82M Swagger TTS API起動中...")
    print("最適化設定:")
    print(f"- 検出CPUコア数: {cpu_count}")
    print(f"- 使用スレッド数: {os.environ.get('OMP_NUM_THREADS')}")
    print("- メモリ最適化: 有効")
    print("- パイプラインキャッシュ: 有効")
    print()
    print("🌐 アクセス URL:")
    print("- Swagger UI: http://localhost:8000/ (ルートパス)")
    print("- API Docs: http://localhost:8000/")
    
    app.run(host='0.0.0.0', port=8000, debug=False, threaded=True)