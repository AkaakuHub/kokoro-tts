#!/usr/bin/env python3
"""
Swagger API統合テスト
"""

import requests
import json
import time
import webbrowser
import subprocess
import signal
import sys
import os

def start_server():
    """APIサーバー起動"""
    print("Swagger APIサーバー起動中...")
    
    # Python仮想環境のPythonを使用
    if os.path.exists("venv/bin/python"):
        python_cmd = "venv/bin/python"
    else:
        python_cmd = "python3"
    
    process = subprocess.Popen([python_cmd, "swagger_tts.py"])
    
    # サーバー起動待機
    print("サーバー起動待機中...")
    for i in range(30):  # 30秒待機
        try:
            response = requests.get("http://localhost:8000/tts/health", timeout=1)
            if response.status_code == 200:
                print("✅ サーバー起動完了!")
                return process
        except:
            time.sleep(1)
            print(f"待機中... ({i+1}/30)")
    
    print("❌ サーバー起動に失敗しました")
    process.terminate()
    return None

def test_swagger_ui():
    """Swagger UIテスト"""
    print("\n🌐 Swagger UI開始...")
    
    try:
        # ブラウザでSwagger UI開く
        webbrowser.open("http://localhost:8000/")
        print("✅ ブラウザでSwagger UIを開きました")
        print("📖 URL: http://localhost:8000/")
        
        return True
    except Exception as e:
        print(f"❌ ブラウザ起動エラー: {e}")
        return False

def test_api_endpoints():
    """API エンドポイントテスト"""
    base_url = "http://localhost:8000"
    
    print("\n🧪 API エンドポイントテスト...")
    
    # ヘルスチェック
    try:
        response = requests.get(f"{base_url}/tts/health")
        print(f"✅ Health Check: {response.json()}")
    except Exception as e:
        print(f"❌ Health Check エラー: {e}")
        return False
    
    # 音声一覧
    try:
        response = requests.get(f"{base_url}/tts/voices")
        voices = response.json()
        print(f"✅ Voices: {voices['voices']}")
    except Exception as e:
        print(f"❌ Voices エラー: {e}")
        return False
    
    # TTS生成テスト
    test_requests = [
        {
            "text": "Hello, this is a Swagger test!",
            "voice": "af_heart",
            "speed": 1.0
        },
        {
            "text": "こんにちは、Swagger UIのテストです。",
            "voice": "af_sky",
            "speed": 1.2
        }
    ]
    
    for i, payload in enumerate(test_requests):
        try:
            print(f"\n🎵 TTS Test {i+1}: {payload['text'][:30]}...")
            
            start_time = time.time()
            response = requests.post(
                f"{base_url}/tts/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                # 音声ファイル保存
                filename = f"swagger_test_{i+1}.wav"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                elapsed = time.time() - start_time
                file_size = len(response.content)
                print(f"✅ 成功: {filename} ({elapsed:.2f}秒, {file_size}bytes)")
            else:
                print(f"❌ エラー: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ TTS Test {i+1} エラー: {e}")
    
    return True

def main():
    """メイン実行"""
    server_process = None
    
    try:
        print("🎤 Kokoro-82M Swagger API統合テスト")
        print("=" * 50)
        
        # サーバー起動
        server_process = start_server()
        if not server_process:
            return
        
        # Swagger UI開く
        test_swagger_ui()
        
        # API テスト
        test_api_endpoints()
        
        print("\n" + "=" * 50)
        print("🎉 テスト完了!")
        print("\n📖 Swagger UI で以下をテストできます:")
        print("1. http://localhost:8000/ にアクセス")
        print("2. 'tts' セクションを展開")
        print("3. '/tts/generate' の 'Try it out' をクリック")
        print("4. テキストと音声を入力して 'Execute'")
        print("5. 'Download file' で音声ファイルをダウンロード")
        
        print("\n⚠️  サーバーを停止するには Ctrl+C を押してください")
        
        # サーバー継続実行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 サーバー停止中...")
    
    finally:
        if server_process:
            server_process.terminate()
            server_process.wait()
            print("✅ サーバー停止完了")

if __name__ == "__main__":
    main()