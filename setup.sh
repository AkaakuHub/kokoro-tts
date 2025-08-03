#!/bin/bash
# Kokoro-TTS軽量セットアップスクリプト

echo "Kokoro-TTS軽量版セットアップ開始..."

# Python仮想環境作成（Python 3.12使用）
if [ ! -d "venv" ]; then
    echo "Python仮想環境作成中..."
    
    # Python 3.12の存在確認
    if command -v python3.12 &> /dev/null; then
        echo "Python 3.12使用（Kokoro互換性のため）"
        python3.12 -m venv venv
    elif command -v python3.11 &> /dev/null; then
        echo "Python 3.11使用（Kokoro互換性のため）"
        python3.11 -m venv venv
    elif command -v python3.10 &> /dev/null; then
        echo "Python 3.10使用（Kokoro互換性のため）"
        python3.10 -m venv venv
    else
        echo "⚠️  Python 3.10-3.12が必要です（現在のPython 3.13は非対応）"
        echo "以下でインストールしてください："
        echo "macOS: brew install python@3.12"
        echo "Ubuntu: sudo apt install python3.12 python3.12-venv"
        exit 1
    fi
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
echo "1. 🌟 Swagger UIサーバー: python swagger_tts.py"
echo "2. 開発用サーバー: python lightweight_tts.py" 
echo "3. 本番用サーバー: python server_prod.py"
echo "4. Swaggerテスト: python test_swagger.py"
echo ""
echo "🌐 Swagger UI アクセス:"
echo "- http://localhost:8000/swagger (推奨)"
echo "- http://localhost:8000/ (ホーム)"
echo ""
echo "API エンドポイント:"
echo "- GET  /tts/health    - ヘルスチェック"
echo "- GET  /tts/voices    - 音声一覧" 
echo "- POST /tts/generate  - 音声生成"