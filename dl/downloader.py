import time
import os
import datetime
import time
import csv
from dl.googlesearch import GoogleSearch
from dl.twittersearch import TwitterSearch
from dl.emotionanalysis import EmotionAnalysis
# from multiprocessing import Process
# import lstm.app


class Downloader:
    def __init__(self):
        self.RSS_URL = 'https://trends.google.co.jp/trends/trendingsearches/daily/rss?geo=JP'
        self.CRAWL_NUM = 5 # image crawl
        self.TWEET_NUM = 100 # number of tweets
        self.googlesearch = GoogleSearch()
        self.twittersearch = TwitterSearch()
        self.emotionanalysis = EmotionAnalysis()

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
        for t in trend_list:
            tweets =  self.twittersearch.search_tweet(t, self.TWEET_NUM)
            tweet_list.append(tweets)
            pn = self.emotionanalysis.analysis(tweets)
            pn_list.append(pn)
            # print(t, tweets, pn)
        ttl_list.append(trend_list)
        # ttl_list.append(tweet_list)
        ttl_list.append(pn_list)

        # 作成したリストを保存する
        now = self.date_str()
        self.save_csv(ttl_list, now)
        self.save_tweets(trend_list, tweet_list, now)

        # 画像をダウンロードする
        # set 5 keywords (temporary)
        # for trend in trend_list:
        # crawlNum = len(trend_list)
        for i in range(self.CRAWL_NUM):
            self.googlesearch.download_google_staticimages(trend_list[i])


        t1 = time.time()
        total_time = t1 - t0
        print(f'Total time is {str(total_time)} seconds.')


    ##### @takagi
    ##### create csv file
    # EmotionAnalysisを保存する
    def save_csv(self, ls, now):
        dir = './trends/' + now
        if not os.path.exists(dir):
            os.makedirs(dir)

        filename = dir + '/' + now + '.csv'
        with open(filename, 'w', encoding='cp932', errors='ignore') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows(ls)

    # Tweetを保存する
    def save_tweets(self, trends, tweets, now):
        dir = './tweets/' + now
        if not os.path.exists(dir):
            os.makedirs(dir)

        for i in range(self.CRAWL_NUM):
            filename = dir + '/' + trends[i] + '.txt'
            with open(filename, 'w', encoding='cp932', errors='ignore') as f:
                f.write(tweets[i])
                f.close()

    def date_str(self):
        return datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

if __name__ == '__main__':
    downloader = Downloader()
    downloader.run()
    # process_list = []
    #
    # process = Process(target=main)
    # process.start()
    # process_list.append(process)
    # process = Process(target=lstm.app.run)
    # process.start()
    # process_list.append(process)
    #
    # for process in process_list:
    #     process.join()