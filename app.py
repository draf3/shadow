import os, time
from crawler.googlesearch import GoogleSearch
from crawler.twittersearch import TwitterSearch
from trend import Trend
import config, util
from jtalk import JTalk
from logger import logger
from osc_sender import OscSender


class App:
    def __init__(self, gui):
        self.gui = gui
        self.jtalk = JTalk(gui)
        self.RSS_URL = 'https://trends.google.co.jp/trends/trendingsearches/daily/rss?geo=JP'
        self.CRAWL_NUM = 5 # image crawl
        self.TWEET_NUM = 100 # number of tweets
        self.IMAGE_NUM = 10
        self.AUDIO_NUM = 5
        self.IMAGE_SIZE = 256
        self.googlesearch = GoogleSearch()
        self.twittersearch = TwitterSearch()
        # NetWork
        self.osc_sender = OscSender(config.IP, config.PORT)

    ##### @takagi
    ##### Main block
    # Trendに関連した、Tweet、imageを保存する
    def run(self):
        t0 = time.time()

        # Trendテキストをリストに格納する
        trend_list = self.googlesearch.search_google_trends_rss(self.RSS_URL)

        # Tweetテキストをリストに格納する
        tweet_list = []
        trend_count = 0
        for t in trend_list:
            tweets = self.twittersearch.search_tweet(t, self.TWEET_NUM)
            tweet_list.append(tweets)
            # logger.debug(t, tweets, pn)
            trend_count += 1
            if trend_count > self.CRAWL_NUM:
                break

        # タイムスタンプを作成する
        now = util.date_str()

        # データを作成する
        for i in range(self.CRAWL_NUM):

            # ファイルを格納するパスを作成
            input_text_dir = os.path.join(config.INPUT_TEXT_DIR, now)
            input_image_dir = os.path.join(config.INPUT_IMAGE_DIR, now, trend_list[i])
            lstm_model_dir = os.path.join(config.LSTM_MODEL_DIR, now)
            output_image_dir = os.path.join(config.OUTPUT_IMAGE_DIR, now, trend_list[i])
            output_audio_dir = os.path.join(config.OUTPUT_AUDIO_DIR, now, trend_list[i])
            input_texts_path = os.path.join(input_text_dir, '{}.txt'.format(trend_list[i]))
            lstm_model_path = os.path.join(lstm_model_dir, '{}.h5'.format(i))

            # トレンドのデータを作成する
            trend = Trend()
            trend.title = trend_list[i]
            trend.input_texts_path = input_texts_path
            trend.lstm_model_path = lstm_model_path
            trend.input_images_dir = input_image_dir
            trend.output_images_dir = output_image_dir
            trend.output_audios_dir = output_audio_dir

            # ディレクトリを作成する
            util.make_dir(input_text_dir)
            util.make_dir(input_image_dir)
            util.make_dir(lstm_model_dir)
            util.make_dir(output_image_dir)
            util.make_dir(output_audio_dir)

            # トレンドデータをデータベースに保存する
            self.gui.trend_store.save(trend)

            # ツイートとトレンド画像をダウンロードする
            util.save_texts(tweet_list[i], input_texts_path)
            self.googlesearch.download_google_staticimages(trend_list[i], input_image_dir)
            util.resize_square_images(input_image_dir, self.IMAGE_SIZE)

            # 画像を生成する
            self.gui.cyclegan_predictor.count = 0
            for i in range(self.IMAGE_NUM):
                self.gui.cyclegan_predictor.predict(input_image_dir, output_image_dir)

            # LSTMモデルを生成する
            self.gui.trainer.train(input_texts_path, lstm_model_path)

            # 音声を生成する
            self.gui.lstm_predictor.setup(input_texts_path, lstm_model_path)
            self.jtalk.count = 0
            for i in range(self.AUDIO_NUM):
                sentence = self.gui.lstm_predictor.predict()
                self.jtalk.say(sentence, output_audio_dir)

            # データを送信する
            # self.osc_sender.send(config.OUTPUT_IMAGES_ADDR, output_image_dir)
            # self.osc_sender.send(config.OUTPUT_AUDIOS_ADDR, output_audio_dir)



        t1 = time.time()
        total_time = t1 - t0
        logger.debug(f'Total time is {str(total_time)} seconds.')
