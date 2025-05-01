FROM python:3.9-slim

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    binutils \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app

# 必要なファイルのコピー
COPY requirements.txt .
COPY app.py .
COPY templates/ templates/

# 依存関係のインストール
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install pyinstaller==6.5.0

# Macバイナリのビルド
RUN pyinstaller --onefile \
    --name MusicAnalyzer \
    --hidden-import=scipy \
    --hidden-import=scipy.special \
    --hidden-import=scipy.special._cdflib \
    --hidden-import=scipy.special._ufuncs \
    --hidden-import=scipy.special._ufuncs_cxx \
    app.py 