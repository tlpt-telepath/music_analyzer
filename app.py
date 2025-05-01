import os
import sys
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from audio_analyzer import analyze_audio, format_output
import librosa
import soundfile as sf
import logging

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PyInstallerでバンドルされた場合のパスを取得
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 環境変数の読み込み
load_dotenv()

app = Flask(__name__, template_folder=resource_path('templates'))
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB制限

# アップロードフォルダの作成
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def preprocess_audio(input_path, output_path, target_sr=16000, max_duration=180):
    """
    音声ファイルを前処理する関数
    - サンプリングレートを16000Hzに変換
    - 最大長を180秒に制限
    - モノラルに変換
    """
    try:
        # 音声ファイルの読み込み
        y, sr = librosa.load(input_path, sr=None)
        logger.info(f"Original audio loaded: {len(y)/sr:.1f} seconds, {sr}Hz")
        
        # 最大長を制限
        if len(y) > max_duration * sr:
            y = y[:int(max_duration * sr)]
            logger.info(f"Audio truncated to {max_duration} seconds")
        
        # サンプリングレートの変換とモノラル化
        y = librosa.resample(y=y, orig_sr=sr, target_sr=target_sr)
        if len(y.shape) > 1:
            y = librosa.to_mono(y)
        
        # ファイルの保存
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
            processed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'processed_{filename}')
            
            # ファイルの保存
            file.save(filepath)
            file_size = os.path.getsize(filepath) / 1024 / 1024  # MB
            logger.info(f"File saved: {filename}, size: {file_size:.1f}MB")
            
            if file_size > 5:
                os.remove(filepath)
                return jsonify({'error': 'ファイルサイズが大きすぎます。5MB以下のファイルをアップロードしてください。'}), 413
            
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
            error_message = str(e)
            if "413" in error_message:
                return jsonify({'error': 'ファイルサイズが大きすぎます。5MB以下のファイルをアップロードしてください。'}), 413
            return jsonify({'error': f'分析中にエラーが発生しました: {error_message}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 