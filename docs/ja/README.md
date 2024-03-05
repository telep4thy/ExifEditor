<h1 align="center"><img src="../../imgs/exif_editor.png"></h1>

-------

## 説明

ExifEditorを使用することで、画像ファイルのExif情報を編集することができます。

## 特徴

ExifEditorは、画像ファイルに付属するExif情報を編集するためのグラフィカルなツールです。
このアプリケーションを使用することで、画像ファイルのExif情報の読み込み、書き込みをすることができます。また、Exif情報の新規作成をすることもできます。
.jpgまたは.tiffの画像ファイルのみ対象です。

編集可能なExif情報は以下に記載されている項目です:

- 撮影日時
- メーカー名
- カメラモデル名
- レンズモデル名
- 焦点距離
- f値
- 露光時間
- ISO

## 動作環境

- Windows 10 64-bit 以降

(MacOSをはじめ、上記以外の環境での動作は確認していません。動作は自己責任でお願いします。)

## 開発環境

使用した言語とライブラリは、以下の通りです。

- Python 3.8 or later
- tkinter
- PIL
- piexif

## スタンドアロンの実行可能ファイルをビルドする方法

pyinstallerを使用することで、簡単にexe化することができます:

```bash
# install pyinstaller (if Anaconda, you should use conda.)
pip install pyinstaller
# build by using pyinstaller
pyinstaller exif_editor.py --onefile --noconsole --exclude pandas --exclude numpy
```

### postscript

現在公開中のExifEditorは、初期バージョンです。
何か問題点や改善点がありましたら、お問い合わせください。
随時、機能の追加や実装を行う予定です...
