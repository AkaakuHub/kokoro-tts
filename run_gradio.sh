#!/bin/bash
# Gradio UIサーバー起動スクリプト

source "$(dirname "$0")/common.sh"
run_python_script "gradio_tts.py" "🎤 Kokoro-82M Gradio UI起動中..."