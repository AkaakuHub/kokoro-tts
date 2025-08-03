#!/bin/bash
# 本番用Waitressサーバー起動スクリプト

source "$(dirname "$0")/common.sh"
run_python_script "server_prod.py" "🏭 Kokoro-82M 本番サーバー起動中..."