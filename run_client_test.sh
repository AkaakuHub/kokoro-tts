#!/bin/bash
# シンプルAPIクライアントテスト実行スクリプト

source "$(dirname "$0")/common.sh"
run_python_script "test_client.py" "📞 Kokoro-82M APIクライアントテスト実行中..."