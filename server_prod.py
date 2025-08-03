#!/usr/bin/env python3
"""
本番用Waitressサーバー起動スクリプト
"""

import multiprocessing
from waitress import serve
from lightweight_tts import app

if __name__ == '__main__':
    print("Kokoro-82M本番サーバー起動中...")
    
    # CPU最大活用
    cpu_count = multiprocessing.cpu_count()
    print(f"CPU最適化設定: {cpu_count}コア使用")
    
    # Waitressで起動（CPU最大活用）
    serve(
        app, 
        host='0.0.0.0', 
        port=8000,
        threads=cpu_count,  # CPU最大活用
        connection_limit=50,  # 適度な同時接続制限
        cleanup_interval=30  # メモリクリーンアップ間隔
    )