#!/bin/bash
# MeCabテスト実行スクリプト

# MeCab環境変数設定（run_gradio.shと同じ）
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
    echo ""
fi

source "$(dirname "$0")/common.sh"
run_python_script "mecab_test.py" "🧪 MeCab動作テスト実行中..."