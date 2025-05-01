import os
import sys
import webbrowser
from threading import Timer
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from audio_analyzer import analyze_audio, format_output
import librosa
import soundfile as sf
import logging
import traceback

# ロギングの設定
log_dir = os.path.join(os.path.expanduser('~'), 'MusicAnalyzer')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'app.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# PyInstallerでバンドルされた場合のパスを取得
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 環境変数の読み込み
try:
    load_dotenv()
except Exception as e:
    logger.error(f"Error loading .env file: {str(e)}")

app = Flask(__name__, template_folder=resource_path('templates'))
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.expanduser('~'), 'MusicAnalyzer', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB制限

# アップロードフォルダの作成
try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
except Exception as e:
    logger.error(f"Error creating upload folder: {str(e)}")

def preprocess_audio(input_path, output_path, target_sr=44100, max_duration=None):
    """
    音声ファイルを前処理する関数
    - サンプリングレートを44.1kHzに変換
    - モノラルに変換（必要な場合のみ）
    """
    try:
        # 音声ファイルの読み込み
        y, sr = librosa.load(input_path, sr=None)
        logger.info(f"Original audio loaded: {len(y)/sr:.1f} seconds, {sr}Hz")
        
        # 最大長の制限を解除
        if max_duration and len(y) > max_duration * sr:
            y = y[:int(max_duration * sr)]
            logger.info(f"Audio truncated to {max_duration} seconds")
        
        # サンプリングレートの変換（44.1kHz）
        y = librosa.resample(y=y, orig_sr=sr, target_sr=target_sr)
        
        # 出力ファイルの拡張子を.wavに設定
        output_path = os.path.splitext(output_path)[0] + '.wav'
        
        # ファイルの保存（44.1kHz）
        sf.write(output_path, y, target_sr)
        logger.info(f"Processed audio saved: {os.path.getsize(output_path)/1024/1024:.1f}MB")
        return output_path
    except Exception as e:
        logger.error(f"Error in preprocess_audio: {str(e)}")
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'ファイルがアップロードされていません'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'ファイルが選択されていません'}), 400
    
    if file:
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            processed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'processed_{os.path.splitext(filename)[0]}')
            
            # ファイルの保存
            file.save(filepath)
            file_size = os.path.getsize(filepath) / 1024 / 1024  # MB
            logger.info(f"File saved: {filename}, size: {file_size:.1f}MB")
            
            # 音声ファイルの前処理
            processed_filepath = preprocess_audio(filepath, processed_filepath)
            
            # 音声分析の実行
            results = analyze_audio(processed_filepath)
            analysis_output = format_output(results)
            
            # 一時ファイルの削除
            if os.path.exists(filepath):
                os.remove(filepath)
            if os.path.exists(processed_filepath):
                os.remove(processed_filepath)
            
            return jsonify({
                'technical_analysis': analysis_output
            })
            
        except Exception as e:
            logger.error(f"Error in analyze: {str(e)}")
            if os.path.exists(filepath):
                os.remove(filepath)
            if os.path.exists(processed_filepath):
                os.remove(processed_filepath)
            return jsonify({'error': f'分析中にエラーが発生しました: {str(e)}'}), 500

def open_browser():
    """
    デフォルトのWebブラウザでアプリケーションを開く
    """
    try:
        webbrowser.open('http://127.0.0.1:5001/')
        logger.info("Browser opened successfully")
    except Exception as e:
        logger.error(f"Error opening browser: {str(e)}")

if __name__ == '__main__':
    try:
        logger.info("Starting application...")
        # アプリケーション起動後にブラウザを開く
        Timer(1.5, open_browser).start()
        # デバッグモードをオフにし、ローカルホストのみでアクセス可能に
        app.run(host='127.0.0.1', port=5001, debug=False)
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        logger.error(traceback.format_exc())
        input("Press Enter to exit...")  # エラー時にウィンドウを保持 