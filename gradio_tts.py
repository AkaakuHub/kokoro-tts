#!/usr/bin/env python3
"""
Gradio UI付きKokoro-82M TTS
音声テストが超簡単！
"""

import os
import gc
import threading
import multiprocessing
import tempfile
from functools import lru_cache
import numpy as np
import soundfile as sf
import gradio as gr

# CPUコア数を自動検出して最大活用
cpu_count = multiprocessing.cpu_count()
os.environ['OMP_NUM_THREADS'] = str(cpu_count)
os.environ['MKL_NUM_THREADS'] = str(cpu_count)

try:
    from kokoro import KPipeline
except ImportError:
    print("kokoroライブラリが必要です。pip install kokoro>=0.9.4")
    exit(1)

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

def generate_audio(text, voice, speed):
    """音声生成関数"""
    try:
        if not text.strip():
            return None, "テキストを入力してください"
        
        if len(text) > 1000:
            return None, "テキストが長すぎます（1000文字以下）"
        
        print(f"TTS生成中: {text[:50]}...")
        
        # パイプライン取得
        pipeline = get_pipeline()
        
        # 音声生成 - 正しいKokoro API使用
        try:
            # Kokoroの正しい使用方法
            audio_generator = pipeline(text, voice=voice, speed=speed)
            
            # 音声チャンクを収集
            audio_chunks = []
            for chunk in audio_generator:
                if chunk is not None:
                    # KPipeline.Resultオブジェクトから音声データを取得
                    if hasattr(chunk, 'audio'):
                        audio_data_chunk = chunk.audio
                    elif hasattr(chunk, 'data'):
                        audio_data_chunk = chunk.data
                    else:
                        audio_data_chunk = chunk
                    
                    # テンソルの場合はnumpy配列に変換
                    if hasattr(audio_data_chunk, 'numpy'):
                        audio_data_chunk = audio_data_chunk.numpy()
                    elif hasattr(audio_data_chunk, 'detach'):
                        audio_data_chunk = audio_data_chunk.detach().cpu().numpy()
                    
                    audio_chunks.append(audio_data_chunk)
            
            if not audio_chunks:
                return None, "音声生成に失敗しました"
            
            print(f"音声チャンク数: {len(audio_chunks)}")
            
            # 最初のチャンクの詳細情報を出力
            first_chunk = audio_chunks[0]
            print(f"最初のチャンク型: {type(first_chunk)}")
            print(f"最初のチャンク形状: {first_chunk.shape if hasattr(first_chunk, 'shape') else 'shape属性なし'}")
            print(f"最初のチャンクデータ型: {first_chunk.dtype if hasattr(first_chunk, 'dtype') else 'dtype属性なし'}")
            
            # Resultオブジェクトの場合、利用可能な属性を確認
            if hasattr(first_chunk, '__dict__'):
                print(f"利用可能な属性: {list(first_chunk.__dict__.keys())}")
            if hasattr(first_chunk, '__class__'):
                print(f"クラス: {first_chunk.__class__}")
                
            # ディレクトリ調査
            print(f"dir()の結果: {[attr for attr in dir(first_chunk) if not attr.startswith('_')]}")
            
            # チャンクを結合
            if len(audio_chunks) == 1:
                audio_data = audio_chunks[0]
            else:
                # 各チャンクが同じ次元か確認
                try:
                    audio_data = np.concatenate(audio_chunks, axis=0)
                except ValueError as e:
                    print(f"結合エラー: {e}")
                    # 1次元に変換してから結合
                    flattened_chunks = []
                    for chunk in audio_chunks:
                        if hasattr(chunk, 'flatten'):
                            flattened_chunks.append(chunk.flatten())
                        else:
                            flattened_chunks.append(np.array(chunk).flatten())
                    audio_data = np.concatenate(flattened_chunks)
                    
        except Exception as e:
            print(f"音声生成エラー: {e}")
            return None, f"音声生成エラー: {str(e)}"
        
        # numpy配列に正規化
        if not isinstance(audio_data, np.ndarray):
            try:
                audio_data = np.array(audio_data, dtype=np.float32)
            except ValueError as e:
                print(f"配列変換エラー: {e}")
                # より安全な変換
                if hasattr(audio_data, '__iter__'):
                    try:
                        # ネストされたリストを平坦化
                        flat_data = []
                        def flatten(lst):
                            for item in lst:
                                if hasattr(item, '__iter__') and not isinstance(item, (str, np.ndarray)):
                                    flatten(item)
                                else:
                                    flat_data.append(float(item))
                        flatten(audio_data)
                        audio_data = np.array(flat_data, dtype=np.float32)
                    except:
                        return None, f"音声データの変換に失敗: {e}"
                else:
                    return None, f"音声データが不正: {type(audio_data)}"
        
        # 1次元配列に変換
        if audio_data.ndim > 1:
            audio_data = audio_data.flatten()
        
        print(f"音声データ形状: {audio_data.shape}, データ型: {audio_data.dtype}")
        
        # 一時ファイルに保存
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            sf.write(tmp_file.name, audio_data, 24000)
            temp_path = tmp_file.name
        
        # メモリ解放
        del audio_data
        gc.collect()
        
        return temp_path, "✅ 音声生成完了！"
        
    except Exception as e:
        print(f"エラー: {str(e)}")
        return None, f"❌ エラー: {str(e)}"

def create_interface():
    """Gradio UIを作成"""
    
    # 利用可能な音声
    voices = [
        'af_heart', 'af_sky', 'af_grace', 'af_heaven',
        'am_adam', 'am_mike', 'bf_iris', 'bf_rose'
    ]
    
    # サンプルテキスト
    sample_texts = [
        "Hello, this is Kokoro TTS!",
        "こんにちは、これはテストです。",
        "The quick brown fox jumps over the lazy dog.",
        "日本語の音声合成のテストを行っています。",
        "Kokoro is a lightweight TTS model with 82 million parameters."
    ]
    
    with gr.Blocks(title="🎤 Kokoro-82M TTS", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🎤 Kokoro-82M TTS
        **軽量・高品質な音声合成システム**
        
        - 📊 **モデル**: Kokoro-82M (82M parameters)
        - 🚀 **CPU最適化**: 16コア使用
        - 💾 **メモリ効率**: パイプラインキャッシュ
        """)
        
        with gr.Row():
            with gr.Column():
                text_input = gr.Textbox(
                    label="📝 テキスト入力",
                    placeholder="音声化したいテキストを入力してください...",
                    lines=3,
                    value="Hello, this is Kokoro TTS!"
                )
                
                with gr.Row():
                    voice_select = gr.Dropdown(
                        choices=voices,
                        value="af_heart",
                        label="🎭 音声選択"
                    )
                    speed_slider = gr.Slider(
                        minimum=0.5,
                        maximum=2.0,
                        value=1.0,
                        step=0.1,
                        label="⚡ 速度"
                    )
                
                generate_btn = gr.Button("🎵 音声生成", variant="primary", size="lg")
                
                gr.Markdown("### 📋 サンプルテキスト")
                sample_buttons = []
                for sample in sample_texts:
                    btn = gr.Button(sample, size="sm")
                    sample_buttons.append(btn)
            
            with gr.Column():
                status_output = gr.Textbox(
                    label="📊 ステータス",
                    value="待機中...",
                    interactive=False
                )
                
                audio_output = gr.Audio(
                    label="🔊 生成音声",
                    type="filepath"
                )
        
        # イベントハンドラー
        generate_btn.click(
            fn=generate_audio,
            inputs=[text_input, voice_select, speed_slider],
            outputs=[audio_output, status_output]
        )
        
        # サンプルテキストボタン
        for btn, sample in zip(sample_buttons, sample_texts):
            btn.click(
                fn=lambda sample=sample: sample,
                outputs=text_input
            )
        
        gr.Markdown("""
        ### 💡 使用方法
        1. **テキスト入力**: 音声化したいテキストを入力
        2. **音声選択**: お好みの音声を選択  
        3. **速度調整**: 再生速度を調整（0.5〜2.0倍）
        4. **音声生成**: ボタンクリックで音声生成開始
        5. **再生**: 生成された音声を再生・ダウンロード
        
        ### 🎭 音声の種類
        - **af_heart, af_sky, af_grace, af_heaven**: 女性音声
        - **am_adam, am_mike**: 男性音声  
        - **bf_iris, bf_rose**: その他音声
        """)
    
    return demo

if __name__ == '__main__':
    print("🎤 Kokoro-82M Gradio UI起動中...")
    print("最適化設定:")
    print(f"- 検出CPUコア数: {cpu_count}")
    print(f"- 使用スレッド数: {os.environ.get('OMP_NUM_THREADS')}")
    print("- メモリ最適化: 有効")
    print("- パイプラインキャッシュ: 有効")
    print()
    
    # Gradio UI起動
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True
    )