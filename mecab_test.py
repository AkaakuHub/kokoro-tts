#!/usr/bin/env python3
"""
MeCab動作テストスクリプト
"""

def test_mecab():
    """MeCab/Fugashiの動作テスト"""
    print("🧪 MeCab動作テスト開始...")
    
    # MeCab-python3テスト
    try:
        import MeCab
        tagger = MeCab.Tagger()
        result = tagger.parse('テスト')
        print("✅ MeCab-python3: 動作OK")
        print(f"   結果: {result.strip()}")
    except Exception as e:
        print(f"❌ MeCab-python3: {e}")
    
    # Fugashiテスト
    try:
        import fugashi
        tagger = fugashi.GenericTagger()
        result = tagger.parse('テスト')
        print("✅ Fugashi GenericTagger: 動作OK")
        print(f"   結果: {result.strip()}")
    except Exception as e:
        print(f"❌ Fugashi GenericTagger: {e}")
    
    # Fugashi通常Taggerテスト
    try:
        import fugashi
        tagger = fugashi.Tagger()
        result = tagger.parse('テスト')
        print("✅ Fugashi Tagger: 動作OK")
        print(f"   結果: {result.strip()}")
    except Exception as e:
        print(f"❌ Fugashi Tagger: {e}")
    
    print("🧪 MeCabテスト完了")

if __name__ == "__main__":
    test_mecab()