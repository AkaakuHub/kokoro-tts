#!/bin/bash
# テスト実行スクリプト

source "$(dirname "$0")/common.sh"
run_python_script "test_swagger.py" "🧪 Kokoro-82M APIテスト実行中..."