import librosa
import numpy as np
import soundfile as sf

def analyze_audio(file_path):
    """
    オーディオファイルを分析し、各種特徴量を抽出する関数
    
    Parameters:
    -----------
    file_path : str
        分析対象のオーディオファイルのパス
    
    Returns:
    --------
    dict
        分析結果を含む辞書
    """
    # オーディオファイルの読み込み
    y, sr = librosa.load(file_path)
    
    # テンポの推定
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr, start_bpm=180.0)
    
    # 音の質感に関する分析
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    spectral_flatness = librosa.feature.spectral_flatness(y=y)
    
    # 感情・抑揚に関する分析
    rms = librosa.feature.rms(y=y)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_diff = np.diff(mfcc, axis=1)
    
    # ジャンル推定に関する分析
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    tonnetz = librosa.feature.tonnetz(y=y, sr=sr)
    zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
    
    # 構成・展開に関する分析
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
    tempogram = librosa.feature.tempogram(y=y, sr=sr)
    y_harmonic, y_percussive = librosa.effects.hpss(y)
    
    # 結果を辞書形式で返す
    return {
        'tempo': float(tempo),
        'mfcc_mean': np.mean(mfcc, axis=1).tolist(),
        'spectral_centroid_mean': float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))),
        'zero_crossing_rate_mean': float(np.mean(zero_crossing_rate)),
        'f0_mean': float(np.mean(librosa.piptrack(y=y, sr=sr)[0][librosa.piptrack(y=y, sr=sr)[0] > 0])),
        'chroma_mean': np.mean(chroma, axis=1).tolist(),
        
        # 音の質感
        'spectral_bandwidth_mean': float(np.mean(spectral_bandwidth)),
        'spectral_contrast_mean': float(np.mean(spectral_contrast)),
        'spectral_flatness_mean': float(np.mean(spectral_flatness)),
        
        # 感情・抑揚
        'rms_mean': float(np.mean(rms)),
        'onset_strength_mean': float(np.mean(onset_env)),
        'mfcc_diff_mean': float(np.mean(np.abs(mfcc_diff))),
        
        # ジャンル推定
        'tonnetz_mean': np.mean(tonnetz, axis=1).tolist(),
        
        # 構成・展開
        'onset_count': len(onset_frames),
        'tempogram_mean': float(np.mean(tempogram)),
        'harmonic_percussive_ratio': float(np.mean(np.abs(y_harmonic)) / np.mean(np.abs(y_percussive)))
    }

def format_output(results):
    """
    分析結果を指定されたフォーマットで出力する関数
    
    Parameters:
    -----------
    results : dict
        分析結果を含む辞書
    """
    output = f"=== 基本情報 ===\n"
    output += f"tempo: {results['tempo']:.1f}\n"
    output += f"mfcc_mean: {str(results['mfcc_mean'])}\n"
    output += f"spectral_centroid_mean: {results['spectral_centroid_mean']:.1f}\n"
    output += f"zero_crossing_rate_mean: {results['zero_crossing_rate_mean']:.3f}\n"
    output += f"f0_mean: {results['f0_mean']:.1f}\n"
    output += f"chroma_mean: {str(results['chroma_mean'])}\n\n"
    
    output += f"=== 音の質感 ===\n"
    output += f"spectral_bandwidth_mean: {results['spectral_bandwidth_mean']:.1f}\n"
    output += f"spectral_contrast_mean: {results['spectral_contrast_mean']:.3f}\n"
    output += f"spectral_flatness_mean: {results['spectral_flatness_mean']:.3f}\n\n"
    
    output += f"=== 感情・抑揚 ===\n"
    output += f"rms_mean: {results['rms_mean']:.3f}\n"
    output += f"onset_strength_mean: {results['onset_strength_mean']:.3f}\n"
    output += f"mfcc_diff_mean: {results['mfcc_diff_mean']:.3f}\n\n"
    
    output += f"=== ジャンル推定 ===\n"
    output += f"tonnetz_mean: {str(results['tonnetz_mean'])}\n\n"
    
    output += f"=== 構成・展開 ===\n"
    output += f"onset_count: {results['onset_count']}\n"
    output += f"tempogram_mean: {results['tempogram_mean']:.3f}\n"
    output += f"harmonic_percussive_ratio: {results['harmonic_percussive_ratio']:.3f}"
    
    return output

def get_tempo(y, sr):
    # 複数のBPM候補を取得
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr, start_bpm=180.0)
    
    # 倍数関係のチェック
    tempo_candidates = [tempo/2, tempo, tempo*2]
    
    # 180 BPMに最も近い値を選択
    return min(tempo_candidates, key=lambda x: abs(x - 180))

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("使用方法: python audio_analyzer.py <オーディオファイルのパス>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    try:
        results = analyze_audio(file_path)
        print(format_output(results))
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        sys.exit(1) 