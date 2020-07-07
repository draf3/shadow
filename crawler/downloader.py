import time
import os
import datetime
import time
import csv
import glob
import math
import numpy as np
import cv2
from crawler.googlesearch import GoogleSearch
from crawler.twittersearch import TwitterSearch
from crawler.emotionanalysis import EmotionAnalysis
from trend_store import Trend
import config
from lstm.predictor import Predictor as LSTMPredictor
from jtalk import JTalk
from logger import logger
import util

class Downloader:
    def __init__(self, gui):
        self.gui = gui
        self.jtalk = JTalk(gui)
        self.RSS_URL = 'https://trends.google.co.jp/trends/trendingsearches/daily/rss?geo=JP'
        self.CRAWL_NUM = 5 # image crawl
        self.TWEET_NUM = 100 # number of tweets
        self.googlesearch = GoogleSearch()
        self.twittersearch = TwitterSearch()
        self.emotionanalysis = EmotionAnalysis()
        self.cur_trends = []
        self.data_id = 0

    ##### @takagi
    ##### Main block
    # Trendに関連した、Tweet、EmotionAnalysis、imageを保存する
    def run(self):
        t0 = time.time()

        # Trendテキストをリストに格納する
        trend_list = self.googlesearch.search_google_trends_rss(self.RSS_URL)

        # Tweet、EmotionAnalysisテキストをリストに格納する
        tweet_list = []
        ttl_list = []
        pn_list = []
        trend_count = 0
        for t in trend_list:
            tweets = self.twittersearch.search_tweet(t, self.TWEET_NUM)
            tweet_list.append(tweets)
            pn = self.emotionanalysis.analysis(tweets)
            pn_list.append(pn)
            # print(t, tweets, pn)
            trend_count += 1
            if trend_count > self.CRAWL_NUM:
                break

        ttl_list.append(trend_list)
        # ttl_list.append(tweet_list)
        ttl_list.append(pn_list)

        # 作成したリストを保存する
        now = self.date_str()
        # self.save_csv(ttl_list, now)

        # 画像をダウンロードする
        # set 5 keywords (temporary)
        # for trend in trend_list:
        # crawlNum = len(trend_list)

        # ディレクトリを作成し
        for i in range(self.CRAWL_NUM):

            # ディレクトリを作成する
            input_text_dir = os.path.join(config.INPUT_TEXT_DIR, now)
            self.make_dir(input_text_dir)

            input_image_dir = os.path.join(config.INPUT_IMAGE_DIR, now, trend_list[i])
            self.make_dir(input_image_dir)

            lstm_model_dir = os.path.join(config.LSTM_MODEL_DIR, now)
            self.make_dir(lstm_model_dir)

            output_image_dir = os.path.join(config.OUTPUT_IMAGE_DIR, now, trend_list[i])
            self.make_dir(output_image_dir)

            output_audio_dir = os.path.join(config.OUTPUT_AUDIO_DIR, now, trend_list[i])
            self.make_dir(output_audio_dir)

            # トレンドのデータを作成する
            trend = Trend()
            trend.title = trend_list[i]

            input_texts_path = os.path.join(input_text_dir, '{}.txt'.format(trend_list[i]))
            trend.input_texts_path = input_texts_path

            lstm_model_path = os.path.join(lstm_model_dir, '{}.h5'.format(i))
            trend.lstm_model_path = lstm_model_path

            trend.input_images_dir = input_image_dir
            trend.output_images_dir = output_image_dir
            trend.output_audios_dir = output_audio_dir

            # トレンドデータをデータベースに保存する
            self.gui.trend_store.save(trend)

            # ツイートとトレンド画像をダウンロードする
            self.save_tweets(tweet_list[i], input_texts_path)
            self.googlesearch.download_google_staticimages(trend_list[i], input_image_dir)
            self.resize(input_image_dir)

            # 画像を生成する
            self.gui.cyclegan_predictor.count = 0
            for i in range(10):
                self.gui.cyclegan_predictor.predict(input_image_dir, output_image_dir)

            # LSTMモデルを生成する
            self.gui.trainer.train(input_texts_path, lstm_model_path)

            # 音声を生成する
            self.gui.lstm_predictor.setup(input_texts_path, lstm_model_path)
            self.jtalk.count = 0
            for i in range(5):
                sentence = self.gui.lstm_predictor.predict()
                self.jtalk.say(sentence, output_audio_dir)


        t1 = time.time()
        total_time = t1 - t0
        print(f'Total time is {str(total_time)} seconds.')


    def resize(self, input_image_dir):
        imgs = []
        image_path = os.path.join(input_image_dir, '*.jpg')
        imgs.extend(glob.glob(image_path))
        size = 256
        x = 0
        y = 0
        count = 0
        for i in imgs:
            img_array = np.fromfile(i, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            # img = cv2.imread(i, 1)
            h, w, ch = img.shape[:3]

            if w > h:
                x = math.floor((w - h) / 2)
                img = img[y:h, x:x + h]
            elif h > w:
                y = math.floor((h - w) / 2)
                img = img[y:y + w, x:w]

            # img = cv2.GaussianBlur(img, (5, 5), 0)
            img = cv2.resize(img, dsize=(size, size))
            filepath = os.path.join(input_image_dir, '{}.jpg'.format(os.path.splitext(os.path.basename(i))[0]))
            util.imwrite(filepath, img)
            print(filepath)
            count += 1

    def make_dir(self, dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    ##### @takagi
    ##### create csv file
    # EmotionAnalysisを保存する
    def save_csv(self, ls, now):
        dir = os.path.join(config.ROOT, 'data', 'trends', now)
        if not os.path.exists(dir):
            os.makedirs(dir)

        filename = os.path.join(dir, '{}.csv'.format(now))
        with open(filename, 'w', encoding='cp932', errors='ignore') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows(ls)

    # Tweetを保存する
    def save_tweets(self, tweets, filename):
        with open(filename, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(tweets)
            f.close()

    def date_str(self):
        return datetime.datetime.now().strftime('%Y%m%d_%H%M%S%f')

if __name__ == '__main__':
    downloader = Downloader()
    downloader.run()