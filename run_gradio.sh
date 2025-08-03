#!/bin/bash
# Gradio UIサーバー起動スクリプト

# MeCab環境変数設定（自動検出）
if command -v mecab &> /dev/null; then
    # MeCabが実際に使用している辞書パスを取得
    MECAB_INFO=$(mecab -D 2>/dev/null | grep "filename:" | head -1)
    if [ -n "$MECAB_INFO" ]; then
        # sys.dicのパスから辞書ディレクトリを抽出
        DICFILE=$(echo "$MECAB_INFO" | sed 's/filename:[[:space:]]*//')
        MECAB_DICDIR=$(dirname "$DICFILE")
        
        # 実際のIPADIC辞書ディレクトリを探す
        if [ -d "/var/lib/mecab/dic/ipadic-utf8" ]; then
            export MECAB_DICDIR="/var/lib/mecab/dic/ipadic-utf8"
        elif [ -d "/var/lib/mecab/dic/ipadic" ]; then
            export MECAB_DICDIR="/var/lib/mecab/dic/ipadic"
        elif [ -d "$MECAB_DICDIR" ]; then
            export MECAB_DICDIR="$MECAB_DICDIR"
        fi
        
        echo "MeCab辞書パス: $MECAB_DICDIR"
        
        # 辞書ディレクトリの内容確認
        if [ -d "$MECAB_DICDIR" ]; then
            echo "辞書ファイル確認:"
            ls -la "$MECAB_DICDIR"/*.dic 2>/dev/null | head -3 || echo "辞書ファイルが見つかりません"
        fi
    else
        echo "⚠️  MeCab辞書情報を取得できませんでした"
    fi
else
    echo "⚠️  MeCabが見つかりません"
fi

source "$(dirname "$0")/common.sh"
run_python_script "gradio_tts.py" "🎤 Kokoro-82M Gradio UI起動中..."