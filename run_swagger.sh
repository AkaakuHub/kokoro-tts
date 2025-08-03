#!/bin/bash
# Swagger UIサーバー起動スクリプト

# Python実行可能ファイル検出
if command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
elif command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Pythonが見つかりません"
    exit 1
fi

echo "🎤 Kokoro-82M Swagger TTS サーバー起動中..."
echo "Python: $PYTHON_CMD"

# 仮想環境確認
if [ -f "venv/bin/activate" ]; then
    echo "仮想環境をアクティベート中..."
    source venv/bin/activate
    python swagger_tts.py
else
    echo "仮想環境が見つかりません。システムPythonで実行中..."
    $PYTHON_CMD swagger_tts.py
fi