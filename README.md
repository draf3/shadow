# Shadow App

## 環境構築
Anacondaのenvファイルを使って環境構築を行います。
そのため、Anaconda（Miniconda）をインストールしてください。

次に下記コマンドを実行し、  
Anacondaでshadowという名前の環境を作り、`keras-contrib`をインストールします。
```
$ conda env create -n shadow -f env.yml
$ pip install git+https://www.github.com/keras-team/keras-contrib.git
```

クロールを行うため、自分のChormeのバージョンに対応したChromeDriverをダウンロードし、下記のパスに配置します。  
`C://Program Files//chromedriver.exe`

## アプリの実行

アプリを実行するため、環境を`shadow`に切り替えてください。
```
$ conda activate shadow
```
次にプロジェクトのルートディレクトリに移動します。

```
$ cd C:\path\to\shadow
```

以下のコマンドで実行完了です。
```
$ python main.py
```

## 送信データ
プロトコルはOSCを使っています。  
画像と音声が格納された2つのディレクトリパスを、設定したアドレスに送信します。  
ip、port、addresはGUIウィンドウから変更することが出来ます。

| ip | port | address       | type   | msg                  |
| ---- | ---- | ------------- | ------ | --------------------- |
| 127.0.0.1 | 10000 | /output_images_dir | string | "C:\path\to\output_images" |
| 127.0.0.1 | 10000 | /output_audios_dir | string | "C:\path\to\output_audios" |



## 保存データ
dataディレクトリ配下にリソースを保存します。
- input_images
  - トレンドで検索しダウンロードしたjpg画像を格納。
  - ファイル名は0,1,2...の連番
- input_text
  - トレンドで検索しダウンロードしたTweetのtxtファイルを格納。
  - ファイル名はトレンド名
- lstm_models
  - トレンドのTweetテキストから生成したLSTMモデルを格納。
  - ファイル名は0,1,2...の連番
- output_audios
  - トレンドのTweetテキストから生成したwavファイルを格納。
  - ファイル名は0,1,2...の連番
- output_images
  - トレンド画像から生成した画像を格納。jpgファイル
  - ファイル名は0,1,2...の連番

## GUIウィンドウ
![app view](images/app_view.png)

### App Config
- download tweet count
  - 設定した数だけツイートをダウンロードする
- download image count
  - 設定した数だけ画像をダウンロードする
- trend count
  - トレンドワードのリミット数を設定する
- generate image count
  - 画像の生成に用いる画像の枚数を設定する
- generate audio count
  - 設定した数だけオーディオデータを生成する
- generate waiting time(min)
  - トレンドワードが一巡したあと、設定した時間だけ待機状態になる
- send data interval(sec)
  - 設定した時間毎にOSCで送信する
- send data(days ago)
  - 設定した日数より前のデータを選択し送信する

### Image and Audio
- frame rate
  - 生成画像のフレームレートを設定する
- frame par iamge
  - 画像一枚あたりのフレーム数
- blur
  - ブラー処理
- binary
  - 二値化（白黒）処理
- canny
  - 輪郭検出処理
- morphology
  - 黒の面積を膨張させる
- invert
  - 色の反転
- blend
  - 画像をフェードで切り替える
- smaller
  - 画像のサイズを中央に小さく表示する
- save
  - 画像とオーディオを保存する
  
### Network
- ip
  - 送信先のIPを設定する。初期値は '127.0.0.1'
- port
  - 送信先のPORTを設定する。初期値は 10000
- output_images_addr
  - 画像ディレクトリの送信先のアドレスを設定する。初期値は '/output_images_dir'
- output_audios_addr
  - オーディオディレクトリの送信先のアドレスを設定する。初期値は '/output_audios_dir'
  
### Other
- generate
  - 処理を開始する