#!/usr/bin/env python3
"""
Kokoro-82M TTS コア機能
全UI共通で使用する多言語TTS機能
"""

import os
import gc
import threading
import multiprocessing
import tempfile
import numpy as np
import soundfile as sf

# CPUコア数を自動検出して最大活用
cpu_count = multiprocessing.cpu_count()
os.environ['OMP_NUM_THREADS'] = str(cpu_count)
os.environ['MKL_NUM_THREADS'] = str(cpu_count)

# MeCab環境変数を設定（日本語サポート用）
def setup_mecab_environment():
    """MeCab環境変数を自動設定"""
    import subprocess
    import shutil
    
    # MeCabがインストールされているかチェック
    if not shutil.which('mecab'):
        print("⚠️  MeCabがインストールされていません")
        return
    
    # IPADIC辞書ディレクトリを探す
    mecab_dicdir = None
    for path in ["/var/lib/mecab/dic/ipadic-utf8", "/var/lib/mecab/dic/ipadic"]:
        if os.path.isdir(path):
            mecab_dicdir = path
            break
    
    if mecab_dicdir:
        os.environ['MECAB_DICDIR'] = mecab_dicdir
        print(f"MeCab辞書パス設定: {mecab_dicdir}")
    
    # mecabrcファイルを探す
    mecabrc = None
    for path in ["/etc/mecabrc", "/usr/local/etc/mecabrc"]:
        if os.path.isfile(path):
            mecabrc = path
            break
    
    if mecabrc:
        os.environ['MECABRC'] = mecabrc
        print(f"MeCabrc設定: {mecabrc}")
    else:
        os.environ['MECABRC'] = '/dev/null'
        print("MeCabrc: 無効化")

# MeCab環境を初期化
setup_mecab_environment()

try:
    from kokoro import KPipeline
except ImportError:
    print("kokoroライブラリが必要です。pip install kokoro>=0.9.4")
    exit(1)

# 言語別パイプラインキャッシュ
_pipelines = {}
_pipeline_lock = threading.Lock()

# 言語と音声の定義
LANGUAGES = {
    'a': 'American English',
    'b': 'British English', 
    'j': 'Japanese',
    'z': 'Mandarin Chinese',
    'e': 'Spanish',
    'f': 'French',
    'h': 'Hindi',
    'i': 'Italian',
    'p': 'Brazilian Portuguese'
}

VOICES = {
    "🇺🇸 American English": [
        'af_heart', 'af_alloy', 'af_aoede', 'af_bella', 'af_jessica', 'af_kore', 
        'af_nicole', 'af_nova', 'af_river', 'af_sarah', 'af_sky',
        'am_adam', 'am_echo', 'am_eric', 'am_fenrir', 'am_liam', 
        'am_michael', 'am_onyx', 'am_puck', 'am_santa'
    ],
    "🇬🇧 British English": [
        'bf_alice', 'bf_emma', 'bf_isabella', 'bf_lily',
        'bm_daniel', 'bm_fable', 'bm_george', 'bm_lewis'
    ],
    "🇯🇵 Japanese": [
        'jf_alpha', 'jf_gongitsune', 'jf_nezumi', 'jf_tebukuro',
        'jm_kumo'
    ],
    "🇨🇳 Mandarin Chinese": [
        'zf_xiaobei', 'zf_xiaoni', 'zf_xiaoxiao', 'zf_xiaoyi',
        'zm_yunjian', 'zm_yunxi', 'zm_yunxia', 'zm_yunyang'
    ],
    "🇪🇸 Spanish": [
        'ef_dora', 'em_alex', 'em_santa'
    ],
    "🇫🇷 French": [
        'ff_siwis'
    ],
    "🇮🇳 Hindi": [
        'hf_alpha', 'hf_beta', 'hm_omega', 'hm_psi'
    ],
    "🇮🇹 Italian": [
        'if_sara', 'im_nicola'
    ],
    "🇧🇷 Brazilian Portuguese": [
        'pf_dora', 'pm_alex', 'pm_santa'
    ]
}

# フラットな音声リスト
ALL_VOICES = []
for voice_list in VOICES.values():
    ALL_VOICES.extend(voice_list)

# 多言語サンプルテキスト
SAMPLE_TEXTS = {
    "🇺🇸 English": [
        "Hello, this is Kokoro TTS!",
        "The quick brown fox jumps over the lazy dog.",
        "Kokoro is a lightweight TTS model with 82 million parameters."
    ],
    "🇯🇵 日本語": [
        "こんにちは、これはテストです。",
        "日本語の音声合成のテストを行っています。", 
        "吾輩は猫である。名前はまだ無い。",
        "美しい夕日が山の向こうに沈んでいく。"
    ],
    "🇨🇳 中文": [
        "你好，这是Kokoro TTS测试。",
        "今天天气很好，阳光明媚。",
        "人工智能技术发展迅速。"
    ],
    "🇪🇸 Español": [
        "Hola, esto es una prueba de Kokoro TTS.",
        "El clima está muy bueno hoy.",
        "La tecnología avanza rápidamente."
    ],
    "🇫🇷 Français": [
        "Bonjour, ceci est un test de Kokoro TTS.",
        "La technologie évolue rapidement.",
        "Il fait beau aujourd'hui."
    ],
    "🇮🇳 हिंदी": [
        "नमस्ते, यह Kokoro TTS का परीक्षण है।",
        "आज मौसम बहुत अच्छा है।",
        "तकनीक तेजी से विकसित हो रही है।"
    ],
    "🇮🇹 Italiano": [
        "Ciao, questo è un test di Kokoro TTS.",
        "Il tempo è molto bello oggi.",
        "La tecnologia si sviluppa rapidamente."
    ],
    "🇧🇷 Português": [
        "Olá, este é um teste do Kokoro TTS.",
        "O tempo está muito bom hoje.",
        "A tecnologia se desenvolve rapidamente."
    ]
}

def detect_language(text, voice):
    """テキストと音声から言語を自動検出"""
    # 音声名のプレフィックスから言語を検出
    voice_prefix = voice.split('_')[0]
    if voice_prefix.startswith('j'):
        return 'j'  # Japanese
    elif voice_prefix.startswith('z'):
        return 'z'  # Mandarin Chinese
    elif voice_prefix.startswith('b'):
        return 'b'  # British English
    elif voice_prefix.startswith('e'):
        return 'e'  # Spanish
    elif voice_prefix.startswith('f'):
        return 'f'  # French
    elif voice_prefix.startswith('h'):
        return 'h'  # Hindi
    elif voice_prefix.startswith('i'):
        return 'i'  # Italian
    elif voice_prefix.startswith('p'):
        return 'p'  # Brazilian Portuguese
    else:
        return 'a'  # American English (default)

def get_pipeline(lang_code='a'):
    """言語別パイプラインをキャッシュして再利用"""
    global _pipelines
    if lang_code not in _pipelines:
        with _pipeline_lock:
            if lang_code not in _pipelines:
                print(f"Kokoroパイプライン初期化中... (言語: {lang_code})")
                _pipelines[lang_code] = KPipeline(lang_code=lang_code)
                print(f"言語 {lang_code} の初期化完了")
    return _pipelines[lang_code]

def generate_audio_data(text, voice="af_heart", speed=1.0, language=None):
    """
    音声データを生成する（コア機能）
    
    Args:
        text (str): 音声化するテキスト
        voice (str): 使用する音声
        speed (float): 再生速度
        language (str): 言語コード（Noneの場合は自動検出）
    
    Returns:
        tuple: (audio_data: np.ndarray, success: bool, message: str)
    """
    try:
        if not text.strip():
            return None, False, "テキストを入力してください"
        
        if len(text) > 1000:
            return None, False, "テキストが長すぎます（1000文字以下）"
        
        # 言語自動検出または手動指定
        if language is None:
            lang_code = detect_language(text, voice)
        else:
            lang_code = language
            
        print(f"TTS生成中: {text[:50]}... (言語: {lang_code}, 音声: {voice})")
        
        # パイプライン取得
        pipeline = get_pipeline(lang_code)
        
        # 音声生成
        audio_generator = pipeline(text, voice=voice, speed=speed)
        
        # 音声チャンクを収集
        audio_chunks = []
        for chunk in audio_generator:
            if chunk is not None:
                # KPipeline.Resultオブジェクトから音声データを取得
                if hasattr(chunk, 'audio'):
                    audio_data_chunk = chunk.audio
                elif hasattr(chunk, 'data'):
                    audio_data_chunk = chunk.data
                else:
                    audio_data_chunk = chunk
                
                # テンソルの場合はnumpy配列に変換
                if hasattr(audio_data_chunk, 'numpy'):
                    audio_data_chunk = audio_data_chunk.numpy()
                elif hasattr(audio_data_chunk, 'detach'):
                    audio_data_chunk = audio_data_chunk.detach().cpu().numpy()
                
                audio_chunks.append(audio_data_chunk)
        
        if not audio_chunks:
            return None, False, "音声生成に失敗しました"
        
        print(f"音声チャンク数: {len(audio_chunks)}")
        
        # チャンクを結合
        if len(audio_chunks) == 1:
            audio_data = audio_chunks[0]
        else:
            # 各チャンクが同じ次元か確認
            try:
                audio_data = np.concatenate(audio_chunks, axis=0)
            except ValueError as e:
                print(f"結合エラー: {e}")
                # 1次元に変換してから結合
                flattened_chunks = []
                for chunk in audio_chunks:
                    if hasattr(chunk, 'flatten'):
                        flattened_chunks.append(chunk.flatten())
                    else:
                        flattened_chunks.append(np.array(chunk).flatten())
                audio_data = np.concatenate(flattened_chunks)
        
        # numpy配列に正規化
        if not isinstance(audio_data, np.ndarray):
            try:
                audio_data = np.array(audio_data, dtype=np.float32)
            except ValueError as e:
                print(f"配列変換エラー: {e}")
                # より安全な変換
                if hasattr(audio_data, '__iter__'):
                    try:
                        # ネストされたリストを平坦化
                        flat_data = []
                        def flatten(lst):
                            for item in lst:
                                if hasattr(item, '__iter__') and not isinstance(item, (str, np.ndarray)):
                                    flatten(item)
                                else:
                                    flat_data.append(float(item))
                        flatten(audio_data)
                        audio_data = np.array(flat_data, dtype=np.float32)
                    except:
                        return None, False, f"音声データの変換に失敗: {e}"
                else:
                    return None, False, f"音声データが不正: {type(audio_data)}"
        
        # 1次元配列に変換
        if audio_data.ndim > 1:
            audio_data = audio_data.flatten()
        
        print(f"音声データ形状: {audio_data.shape}, データ型: {audio_data.dtype}")
        
        # メモリ解放
        del audio_chunks
        gc.collect()
        
        return audio_data, True, "✅ 音声生成完了！"
        
    except Exception as e:
        print(f"エラー: {str(e)}")
        return None, False, f"❌ エラー: {str(e)}"

def generate_audio_file(text, voice="af_heart", speed=1.0, language=None, output_path=None):
    """
    音声ファイルを生成する
    
    Args:
        text (str): 音声化するテキスト
        voice (str): 使用する音声
        speed (float): 再生速度
        language (str): 言語コード（Noneの場合は自動検出）
        output_path (str): 出力ファイルパス（Noneの場合は一時ファイル）
    
    Returns:
        tuple: (file_path: str, success: bool, message: str)
    """
    # 音声データ生成
    audio_data, success, message = generate_audio_data(text, voice, speed, language)
    
    if not success:
        return None, False, message
    
    try:
        # ファイル保存
        if output_path is None:
            # 一時ファイル
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                sf.write(tmp_file.name, audio_data, 24000)
                file_path = tmp_file.name
        else:
            # 指定パス
            sf.write(output_path, audio_data, 24000)
            file_path = output_path
        
        # メモリ解放
        del audio_data
        gc.collect()
        
        return file_path, True, message
        
    except Exception as e:
        print(f"ファイル保存エラー: {str(e)}")
        return None, False, f"❌ ファイル保存エラー: {str(e)}"

def get_voice_info():
    """音声情報を取得"""
    return {
        "languages": LANGUAGES,
        "voices": VOICES,
        "all_voices": ALL_VOICES,
        "sample_texts": SAMPLE_TEXTS
    }

def get_system_info():
    """システム情報を取得"""
    return {
        "cpu_cores": cpu_count,
        "omp_threads": os.environ.get('OMP_NUM_THREADS'),
        "mkl_threads": os.environ.get('MKL_NUM_THREADS'),
        "loaded_languages": list(_pipelines.keys())
    }