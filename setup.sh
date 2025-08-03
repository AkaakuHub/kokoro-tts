#!/bin/bash
# Kokoro-TTS軽量セットアップスクリプト

echo "Kokoro-TTS軽量版セットアップ開始..."

# Python仮想環境作成
if [ ! -d "venv" ]; then
    echo "Python仮想環境作成中..."
    python3 -m venv venv
fi

# 仮想環境アクティベート
source venv/bin/activate

# 依存関係インストール
echo "依存関係インストール中..."
pip install --upgrade pip
pip install -r requirements.txt

# 実行権限付与
chmod +x lightweight_tts.py
chmod +x server_prod.py
chmod +x test_client.py

echo "セットアップ完了!"
echo ""
echo "使用方法:"
echo "1. 開発用サーバー起動: python lightweight_tts.py"
echo "2. 本番用サーバー起動: python server_prod.py"
echo "3. テスト実行: python test_client.py"
echo ""
echo "API エンドポイント:"
echo "- GET  /health  - ヘルスチェック"
echo "- GET  /voices  - 音声一覧"
echo "- POST /tts     - 音声生成"