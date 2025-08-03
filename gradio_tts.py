#!/usr/bin/env python3
"""
Gradio UI付きKokoro-82M TTS
音声テストが超簡単！
"""

import gradio as gr
from kokoro_core import (
    generate_audio_file, 
    get_voice_info, 
    get_system_info,
    VOICES, 
    ALL_VOICES,
    SAMPLE_TEXTS
)

def generate_audio(text, voice, speed):
    """Gradio用音声生成関数"""
    file_path, success, message = generate_audio_file(text, voice, speed)
    return file_path if success else None, message

def create_interface():
    """Gradio UIを作成"""
    
    # システム情報取得
    system_info = get_system_info()
    
    with gr.Blocks(title="🎤 Kokoro-82M TTS", theme=gr.themes.Soft()) as demo:
        gr.Markdown(f"""
        # 🎤 Kokoro-82M TTS
        **軽量・高品質な音声合成システム**
        
        - 📊 **モデル**: Kokoro-82M (82M parameters)
        - 🚀 **CPU最適化**: {system_info['cpu_cores']}コア使用
        - 💾 **メモリ効率**: パイプラインキャッシュ
        - 🌍 **対応言語**: 9言語・54音声
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
                        choices=ALL_VOICES,
                        value="af_heart",
                        label="🎭 音声選択 (言語自動検出)"
                    )
                    speed_slider = gr.Slider(
                        minimum=0.5,
                        maximum=2.0,
                        value=1.0,
                        step=0.1,
                        label="⚡ 速度"
                    )
                
                generate_btn = gr.Button("🎵 音声生成", variant="primary", size="lg")
                
                # 言語別サンプルテキスト
                gr.Markdown("### 📋 多言語サンプルテキスト")
                sample_buttons = []
                for lang, texts in SAMPLE_TEXTS.items():
                    gr.Markdown(f"**{lang}**")
                    for text in texts:
                        btn = gr.Button(text, size="sm")
                        sample_buttons.append((btn, text))
            
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
        for btn, text in sample_buttons:
            btn.click(
                fn=lambda t=text: t,
                outputs=text_input
            )
        
        gr.Markdown("""
        ### 💡 使用方法
        1. **テキスト入力**: 音声化したいテキストを入力
        2. **音声選択**: お好みの音声を選択  
        3. **速度調整**: 再生速度を調整（0.5〜2.0倍）
        4. **音声生成**: ボタンクリックで音声生成開始
        5. **再生**: 生成された音声を再生・ダウンロード
        
        ### 🌍 対応言語と音声
        - **🇺🇸 American English**: 11F + 9M (af_heart, am_adam など)
        - **🇬🇧 British English**: 4F + 4M (bf_emma, bm_daniel など)
        - **🇯🇵 Japanese**: 4F + 1M (jf_alpha, jm_kumo など)
        - **🇨🇳 Mandarin Chinese**: 4F + 4M (zf_xiaobei, zm_yunjian など)
        - **🇪🇸 Spanish**: 1F + 2M (ef_dora, em_alex など)
        - **🇫🇷 French**: 1F (ff_siwis)
        - **🇮🇳 Hindi**: 2F + 2M (hf_alpha, hm_omega など)
        - **🇮🇹 Italian**: 1F + 1M (if_sara, im_nicola)
        - **🇧🇷 Brazilian Portuguese**: 1F + 2M (pf_dora, pm_alex など)
        
        ### 🎭 音声選択のコツ
        - **j** で始まる音声 → 日本語に最適
        - **z** で始まる音声 → 中国語に最適
        - **b** で始まる音声 → イギリス英語
        - 言語は音声選択で自動検出されます！
        """)
    
    return demo

if __name__ == '__main__':
    print("🎤 Kokoro-82M Gradio UI起動中...")
    
    # システム情報表示
    system_info = get_system_info()
    print("最適化設定:")
    print(f"- 検出CPUコア数: {system_info['cpu_cores']}")
    print(f"- 使用スレッド数: {system_info['omp_threads']}")
    print("- メモリ最適化: 有効")
    print("- パイプラインキャッシュ: 有効")
    print(f"- 対応言語: 9言語")
    print(f"- 対応音声: {len(ALL_VOICES)}種類")
    print()
    
    # Gradio UI起動
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True
    )