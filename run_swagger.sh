#!/bin/bash
# Swagger UIサーバー起動スクリプト

source "$(dirname "$0")/common.sh"
run_python_script "swagger_tts.py" "🎤 Kokoro-82M Swagger TTS サーバー起動中..."