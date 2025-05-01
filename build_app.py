import PyInstaller.__main__
import os
import platform

def build():
    # アプリケーションのエントリーポイントを指定
    entry_point = 'app.py'
    
    # 基本のPyInstallerオプション
    base_opts = [
        entry_point,
        '--onefile',  # シングルファイルとして出力
        '--clean',    # キャッシュをクリーン
        '--name=MusicAnalyzer',  # 出力ファイル名
        '--add-data=templates:templates',  # テンプレートフォルダを含める
        '--hidden-import=sklearn.utils._cython_blas',
        '--hidden-import=sklearn.neighbors.typedefs',
        '--hidden-import=sklearn.neighbors.quad_tree',
        '--hidden-import=sklearn.tree',
        '--hidden-import=sklearn.tree._utils',
        '--hidden-import=librosa',
        '--hidden-import=soundfile',
    ]

    # Windows向けの追加オプション
    windows_opts = base_opts + [
        '--target-platform=win32',
        '--target-arch=x86_64',
    ]

    # 現在のプラットフォームに応じてビルド
    if platform.system() == 'Darwin':  # macOS
        # macOS用のビルド
        print("Building for macOS...")
        PyInstaller.__main__.run(base_opts)
        
        # Windows用のビルド
        print("Building for Windows...")
        PyInstaller.__main__.run(windows_opts)
    else:
        # その他のプラットフォーム用のビルド
        print(f"Building for {platform.system()}...")
        PyInstaller.__main__.run(base_opts)

if __name__ == '__main__':
    build() 