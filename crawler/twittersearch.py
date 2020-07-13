import re
import crawler.GetTweet.got3 as got
import os

class TwitterSearch:
    '''
        Twitterからデータを取得するクラス

    '''
    def __init__(self):
        pass

    # Tweetのリストを返す
    def search_tweet(self, word, num):
        tweetCriteria = got.manager.TweetCriteria().setQuerySearch(word).setTopTweets(True).setMaxTweets(num)
        tweet = got.manager.TweetManager.getTweets(tweetCriteria)
        # tweets = []
        tweets = ''
        for v in tweet:
            # tweets.append(v.text)
            f = self.format_text(v.text)
            f += '。'
            # f = v.text
            # print(f)
            tweets += f
        print(tweets)
        return tweets

    ###  tweetの余分な文字削除
    ###  https://hacknote.jp/archives/19937/
    def format_text(self, text):
        text=re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-…]+', "", text)
        text=re.sub('RT', "", text)
        text=re.sub('お気に入り', "", text)
        text=re.sub('まとめ', "", text)
        text=re.sub(r'[!-~]', "", text)#半角記号,数字,英字
        text=re.sub(r'[︰-＠]', "", text)#全角記号
        text=re.sub('\n', "", text)#改行文字
        text=re.sub('。', "", text)#。文字
        text=re.sub(' ', "", text)#半角スペース

        return text