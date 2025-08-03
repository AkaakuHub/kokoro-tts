#!/bin/bash
# 共通関数ライブラリ

# Python実行可能ファイル検出関数
detect_python() {
    if command -v python3.12 &> /dev/null; then
        echo "python3.12"
    elif command -v python3.11 &> /dev/null; then
        echo "python3.11"
    elif command -v python3.10 &> /dev/null; then
        echo "python3.10"
    elif command -v python3 &> /dev/null; then
        echo "python3"
    elif command -v python &> /dev/null; then
        echo "python"
    else
        echo ""
    fi
}

# Pythonスクリプト実行関数
run_python_script() {
    local script_name="$1"
    local description="$2"
    
    # Python検出
    PYTHON_CMD=$(detect_python)
    if [ -z "$PYTHON_CMD" ]; then
        echo "❌ Pythonが見つかりません"
        exit 1
    fi
    
    echo "$description"
    echo "Python: $PYTHON_CMD"
    
    # 仮想環境確認と実行
    if [ -f "venv/bin/activate" ]; then
        echo "仮想環境をアクティベート中..."
        source venv/bin/activate
        python "$script_name"
    else
        echo "仮想環境が見つかりません。システムPythonで実行中..."
        $PYTHON_CMD "$script_name"
    fi
}