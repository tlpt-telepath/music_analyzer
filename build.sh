#!/bin/bash

# 仮想環境の作成と有効化
python3 -m venv venv
source venv/bin/activate

# 必要なパッケージのインストール
pip install -r requirements.txt
pip install pyinstaller

# PyInstallerでビルド
pyinstaller build.spec

# ビルド後のクリーンアップ
deactivate

echo "ビルドが完了しました。dist/MusicAnalyzer.app を確認してください。" 