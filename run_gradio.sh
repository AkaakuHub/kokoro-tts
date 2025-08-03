#!/bin/bash
# Gradio UIサーバー起動スクリプト

# MeCab環境変数設定（自動検出）
if command -v mecab &> /dev/null; then
    # IPADIC辞書ディレクトリを探す
    if [ -d "/var/lib/mecab/dic/ipadic-utf8" ]; then
        export MECAB_DICDIR="/var/lib/mecab/dic/ipadic-utf8"
    elif [ -d "/var/lib/mecab/dic/ipadic" ]; then
        export MECAB_DICDIR="/var/lib/mecab/dic/ipadic"
    fi
    
    # mecabrcファイルを正しく設定
    if [ -f "/etc/mecabrc" ]; then
        export MECABRC=/etc/mecabrc
    elif [ -f "/usr/local/etc/mecabrc" ]; then
        export MECABRC=/usr/local/etc/mecabrc
    else
        export MECABRC=/dev/null
    fi
    
    echo "MeCab設定:"
    echo "- 辞書パス: $MECAB_DICDIR"
    echo "- rcファイル: $MECABRC"
    
    # 辞書ディレクトリの内容確認
    if [ -d "$MECAB_DICDIR" ]; then
        echo "- 辞書ファイル数: $(ls "$MECAB_DICDIR"/*.dic 2>/dev/null | wc -l)"
    fi
else
    echo "⚠️  MeCabが見つかりません"
fi

source "$(dirname "$0")/common.sh"
run_python_script "gradio_tts.py" "🎤 Kokoro-82M Gradio UI起動中..."