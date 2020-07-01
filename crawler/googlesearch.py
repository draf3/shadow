from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from pytrends.request import TrendReq

import feedparser
import pprint
import json
import os
import argparse
import time
import sys

import pandas as pd
import requests
import urllib
import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)


class GoogleSearch:
    '''
    Googleからデータを取得するクラス

    '''
    def __init__(self):
        ##### for google image search
        self.dummycount = 20  ##### first 20 images' urls in google search is not url start from 'https://'
        self.maxcount = 100
        self.tryNum = 5
        self.chromedriver = 'C://Program Files//chromedriver.exe'
        self.Google_trend_list = []

    ##### for google trend search
    ##### 20200318
    ##### @takagi
    ##### google trend search (pytrends)
    # フィードからトレンドを取得し、リストを返す
    def search_google_trends_rss(self, feed):
        ##### google trend search
        d = feedparser.parse(feed)
        for entry in d.entries:
            self.Google_trend_list.append(entry.title)

        return self.Google_trend_list

    ##### 20200318
    ##### @takagi
    ##### google search function
    ##### add searchword to argument
    # Googleを巡回して一連の処理を実行する。
    # searchwordで検索した画像をダウンロードする
    def download_google_staticimages(self, searchword):

        # ディレクトリが存在してなければ作る
        dirs = 'pictures/' + searchword
        if not os.path.exists(dirs):
            os.makedirs(dirs)

        # chromedricerでURLを巡回する
        searchurl = 'https://www.google.com/search?q=' + searchword + '&source=lnms&tbm=isch'
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        #options.add_argument('--headless')
        try:
            browser = webdriver.Chrome(self.chromedriver, options=options)
        except Exception as e:
            print(f'No found chromedriver in this environment.')
            print(f'Install on your machine. exception: {e}')
            sys.exit()

        browser.set_window_size(1280, 1024)
        browser.get(searchurl)
        time.sleep(1)

        print(f'Getting you a lot of images. This may take a few moments...')

        element = browser.find_element_by_tag_name('body')

        # Scroll down
        for i in range(self.tryNum):
        # for i in range(50):
            element.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.3)

        try:
            browser.find_element_by_id('smb').click()
            # for i in range(50):
            for i in range(self.tryNum):
                element.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.3)
        except:
            for i in range(self.tryNum):
                element.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.3)

        print(f'Reached end of page.')

        page_source = browser.page_source

        soup = BeautifulSoup(page_source, 'lxml')
        images = soup.find_all('img')

        urls = []

        imageLen = min(len(images), self.dummycount + self.maxcount)
        if imageLen == 0:
            return 0

        # 画像のダウンロードパスを作り、Urlsに格納する
        for i in range(imageLen):
            try:
                url = images[i]['data-src']
                if not url.find('https://'):
                    urls.append(url)
            except:
                try:
                    url = images[i]['src']
                    if not url.find('https://'):
                        urls.append(images[i]['src'])
                except Exception as e:
                    print(f'No found image sources.')
                    print(e)

        # Urlsから画像を保存する
        count = 0
        if urls:
            for url in urls:
                try:
                    res = requests.get(url, verify=False, stream=True)
                    rawdata = res.raw.read()
                    with open(os.path.join(dirs, 'img_' + str(count) + '.jpg'), 'wb') as f:
                        f.write(rawdata)
                        count += 1
                except Exception as e:
                    print('Failed to write rawdata.')
                    print(e)

        browser.close()
        return count