#!/bin/bash
# Kokoro-TTS軽量セットアップスクリプト

echo "Kokoro-TTS軽量版セットアップ開始..."

# Ubuntu/Debian依存関係チェック
if [ -f "/etc/debian_version" ]; then
    echo "Ubuntu/Debian検出 - 必要なパッケージを確認中..."
    
    # python3-venvパッケージの確認とインストール
    if command -v python3.12 &> /dev/null; then
        PYTHON_VERSION="3.12"
        PYTHON_CMD="python3.12"
    elif command -v python3.11 &> /dev/null; then
        PYTHON_VERSION="3.11"
        PYTHON_CMD="python3.11"
    elif command -v python3.10 &> /dev/null; then
        PYTHON_VERSION="3.10"
        PYTHON_CMD="python3.10"
    else
        echo "⚠️  Python 3.10-3.12が必要です"
        echo "インストール: sudo apt install python3.11 python3.11-venv"
        exit 1
    fi
    
    echo "Python ${PYTHON_VERSION}使用（Kokoro互換性のため）"
    
    # venvパッケージの存在確認
    if ! dpkg -l | grep -q "python${PYTHON_VERSION}-venv"; then
        echo "python${PYTHON_VERSION}-venvパッケージをインストール中..."
        sudo apt update
        sudo apt install -y python${PYTHON_VERSION}-venv
    fi
else
    # macOS等の場合
    if command -v python3.12 &> /dev/null; then
        PYTHON_CMD="python3.12"
    elif command -v python3.11 &> /dev/null; then
        PYTHON_CMD="python3.11"
    elif command -v python3.10 &> /dev/null; then
        PYTHON_CMD="python3.10"
    else
        echo "⚠️  Python 3.10-3.12が必要です"
        echo "macOS: brew install python@3.12"
        exit 1
    fi
fi

# Python仮想環境作成
if [ ! -d "venv" ]; then
    echo "Python仮想環境作成中..."
    echo "使用コマンド: $PYTHON_CMD -m venv venv"
    $PYTHON_CMD -m venv venv
    
    if [ $? -ne 0 ]; then
        echo "❌ 仮想環境作成に失敗しました"
        echo "手動で実行してテスト: $PYTHON_CMD -m venv test_venv"
        exit 1
    fi
    echo "✅ 仮想環境作成完了"
else
    echo "既存の仮想環境を使用"
fi

# ファイル存在確認（デバッグ）
echo "仮想環境ファイル確認:"
ls -la venv/ 2>/dev/null || echo "venvディレクトリが存在しません"
ls -la venv/bin/ 2>/dev/null || echo "venv/binディレクトリが存在しません"

# 仮想環境アクティベート
if [ -f "venv/bin/activate" ]; then
    echo "✅ activate ファイル発見、仮想環境アクティベート中..."
    source venv/bin/activate
    echo "✅ 仮想環境アクティベート完了"
    echo "Python: $(which python)"
    echo "Pip: $(which pip)"
else
    echo "❌ 仮想環境のアクティベートに失敗しました"
    echo "詳細:"
    echo "- venvディレクトリ存在: $([ -d "venv" ] && echo "YES" || echo "NO")"
    echo "- activate ファイル存在: $([ -f "venv/bin/activate" ] && echo "YES" || echo "NO")"
    echo "- venv内容:"
    find venv -type f 2>/dev/null | head -10 || echo "venvディレクトリが空または存在しません"
    exit 1
fi

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