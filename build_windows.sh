#!/bin/bash

# Dockerイメージのビルド
docker build -t music-analyzer-builder .

# コンテナの実行とビルド
docker run --rm -v "$PWD/dist:/app/dist" music-analyzer-builder

# 権限の設定
chmod +x dist/MusicAnalyzer 