#!/bin/bash
# Gradio UIサーバー起動スクリプト

# MeCab環境変数設定
if command -v mecab-config &> /dev/null; then
    export MECAB_DICDIR=$(mecab-config --dicdir)
    echo "MeCab辞書パス: $MECAB_DICDIR"
    
    # 辞書ディレクトリの内容確認
    echo "辞書内容:"
    ls -la $MECAB_DICDIR/ | head -5
fi

source "$(dirname "$0")/common.sh"
run_python_script "gradio_tts.py" "🎤 Kokoro-82M Gradio UI起動中..."