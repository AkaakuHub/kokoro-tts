#!/usr/bin/env python3
"""
Kokoro TTS APIテストクライアント
"""

import requests
import json
import time

def test_api(base_url="http://localhost:8000"):
    """API動作テスト"""
    
    print(f"APIテスト開始: {base_url}")
    
    # ヘルスチェック
    print("\n1. ヘルスチェック...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"ステータス: {response.status_code}")
        print(f"レスポンス: {response.json()}")
    except Exception as e:
        print(f"エラー: {e}")
        return
    
    # 音声一覧取得
    print("\n2. 音声一覧取得...")
    try:
        response = requests.get(f"{base_url}/voices")
        voices_data = response.json()
        print(f"利用可能音声: {voices_data['voices']}")
    except Exception as e:
        print(f"エラー: {e}")
        return
    
    # TTS生成テスト
    print("\n3. TTS生成テスト...")
    test_texts = [
        "Hello, this is a test.",
        "こんにちは、これはテストです。",
        "Testing Kokoro TTS with short text."
    ]
    
    for i, text in enumerate(test_texts):
        print(f"\nテスト {i+1}: {text}")
        
        payload = {
            "text": text,
            "voice": "af_heart",
            "speed": 1.0
        }
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{base_url}/tts",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                # 音声ファイル保存
                filename = f"test_output_{i+1}.wav"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                elapsed = time.time() - start_time
                print(f"成功: {filename} ({elapsed:.2f}秒)")
            else:
                print(f"エラー: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"リクエストエラー: {e}")
    
    print("\nテスト完了")

if __name__ == "__main__":
    test_api()