import got3 as got

word = '吉野家'
tweetNum = 10

# 検索でツイート取得
# tweetCriteria = got.manager.TweetCriteria().setQuerySearch('コロナ').setSince(
#     "2020-03-20").setUntil("2020-03-21").setTopTweets(True).setMaxTweets(10)
tweetCriteria = got.manager.TweetCriteria().setQuerySearch(word).setTopTweets(True).setMaxTweets(tweetNum)

tweet = got.manager.TweetManager.getTweets(tweetCriteria)

for v in tweet:
    print(v.text)


# print(tweet)
