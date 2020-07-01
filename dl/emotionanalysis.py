# -*- coding: utf-8 -*-
import pandas as pd
import MeCab

### 参考
### https://dailytextmining.hatenablog.com/entry/2018/07/12/065500
### 


class EmotionAnalysis:
    '''
        感情分析の結果を返すクラス

    '''
    def __init__(self):
        FILKE_PATH='dic/pn_ja.dic.txt'
        pn_table = pd.read_csv(FILKE_PATH, engine='python', encoding='shift_jis', sep=':', names=('Word','Reading','POS','PN'))

        word_list = list(pn_table['Word'])
        pn_list = list(pn_table['PN'])
        self.npjp_dic = dict(zip(word_list, pn_list))

    def analysis(self, tweet):
        tagger = MeCab.Tagger ("")
        kaisekiyou = tweet.split('¥n')
        string = ' '.join(kaisekiyou)
        mecab = tagger.parse(string)

        kaigyou = mecab.splitlines()
        pn_num = 0
        pn_ttl = 0
        average = 0
        for tango_list in kaigyou:
            tab = tango_list.split('\t')
            if tab[0] in self.npjp_dic:
                pn_score = self.npjp_dic[tab[0]]
                pn_num+=1
                pn_ttl+=pn_score
                # print(tab[0], pn_score)
            # else:
                # pn_score = '辞書に単語がないです'
        if pn_num == 0:
            average = 0
        else:
            average = pn_ttl/pn_num
        return average