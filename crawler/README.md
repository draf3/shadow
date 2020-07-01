# shadow
## プロジェクト概要
普段なにも意識せずに行う「検索」という行為。
何が検索され人々の興味はどう移り変わっていくのか。
人々の興味により成り立つ「検索」という行為をGANによって視覚化します。
刹那的に消費される「検索トレンド」という情報を具現化し弔うプロジェクトです。
常に変わっていく積み重なったトレンドの姿を見て何を思うか。

---  
## 環境構築
- 下記を実行  
`
$ pip install -r requirements.txt  
`
- マシン環境に合わせた[ChromeDriver](https://chromedriver.chromium.org/downloads)をダウンロードして下記に配置  
`C://Program Files//chromedriver.exe`

- アプリの実行
`shadow.bat`を実行してください。  
5分間隔で`app.py`が実行されます。

---  

## Google Search
Googleの検索ではトレンドの検索と画像検索を使用

1. トレンド検索  
[pytrends](https://pypi.org/project/pytrends/)と[RSS](https://trends.google.co.jp/trends/trendingsearches/daily/rss?geo=JP)どちらか。pytrendsに関してはウェブ上のランキングと取得してくるランキングに差異が見られたため今回はRSSを採用。

2. 画像検索  
[google-images-download](https://github.com/hardikvasa/google-images-download)で試したものの、Googleの仕様変更により機能しない。そのためgithubのissuesに上がっていた[このLINK](https://github.com/hardikvasa/google-images-download/issues/301#issuecomment-586788933)のソースをベースにカスタマイズして使用。

## Twitter  
twitter検索はAPIを使用せず[GetOldTweets-python](https://qiita.com/jinto/items/60f23a6b5d9603836dab)を使用してツイートを取得。  
各Tweetから「。」を削除し、Tweet単位で「。」を付与。最終的に1文に結合して.txtファイルとして出力。  

【出力形式】  
`./tweets/yyyymmdd_hhmmss/[trend_word].txt`


## 感情分析
Twitterで取得したTweetを元に感情分析を行い、トレンドのワードに対して人々がどのような感情を抱いているかを数値化する。
1. 形態素解析  
[Mecab](https://qiita.com/menon/items/f041b7c46543f38f78f7)を採用。各TweetをMecabで単語単位で分割。
2. 極性辞書  
[単語感情極性対応表](http://www.lr.pi.titech.ac.jp/~takamura/pndic_ja.html)を用いて各単語のネガポジ判定を行う。
  
トレンドのワードと、それに対応するTweetから分析したネガポジの値をテーブルにしてcsvファイルに出力。

【出力形式】  
`./trends/yyyymmdd_hhmmss.csv`  
※[yyyymmdd_hhmmss]はtweetと同じ年月日時分秒。
  
  
GAN側ではtxtかcsvどちらかのoutputを監視して、ディレクトリ名かファイル名から[yyyymmdd_hhmmss]を取得してもう一方を取得。