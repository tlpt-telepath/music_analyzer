import os
import sys
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from audio_analyzer import analyze_audio, format_output

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
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB制限

# アップロードフォルダの作成
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
            file.save(filepath)
            
            # 音声分析の実行
            results = analyze_audio(filepath)
            analysis_output = format_output(results)
            
            # 一時ファイルの削除
            if os.path.exists(filepath):
                os.remove(filepath)
            
            return jsonify({
                'technical_analysis': analysis_output
            })
            
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            error_message = str(e)
            if "413" in error_message:
                return jsonify({'error': 'ファイルサイズが大きすぎます。100MB以下のファイルをアップロードしてください。'}), 413
            return jsonify({'error': f'分析中にエラーが発生しました: {error_message}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 