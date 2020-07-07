from __future__ import print_function
from keras.callbacks import LambdaCallback
from keras.models import Sequential, load_model
from keras.layers import Dense, Activation
from keras.layers import LSTM
from keras.optimizers import RMSprop
import tensorflow as tf
from tensorflow.python.keras.backend import set_session
from keras.utils.data_utils import get_file
import matplotlib.pyplot as plt  # 追加
import numpy as np
import random
import sys
import io


class Trainer:
    '''
    LSTMモデルを生成するクラス
    '''
    def __init__(self, gui):
        self.gui = gui
        self.sess = tf.Session()
        self.graph = tf.get_default_graph()
        set_session(self.sess)

    def train(self, input_texts_path, lstm_model_path):
        with self.graph.as_default():
            set_session(self.sess)

            # 学習のためのデータセットを作る
            # ファイルを読み込む
            with io.open(input_texts_path, encoding='utf-8') as f:
                text = f.read().lower()
            print('corpus length:', len(text))

            # 重複しない文字のインデックスを作る
            chars = sorted(list(set(text)))
            print('total chars:', len(chars))
            char_indices = dict((c, i) for i, c in enumerate(chars))
            print(char_indices)

            # センテンスと次の文字のリストを作る
            maxlen = 10
            step = 1
            sentences = []
            next_chars = []
            for i in range(0, len(text) - maxlen, step):
                sentences.append(text[i: i + maxlen])
                next_chars.append(text[i + maxlen])
            print('nb sequences:', len(sentences))
            print(sentences)
            print(next_chars)

            # x:訓練データとy:教師データを作る
            print('Vectorization...')
            x = np.zeros((len(sentences), maxlen, len(chars)), dtype=np.bool)
            y = np.zeros((len(sentences), len(chars)), dtype=np.bool)
            for i, sentence in enumerate(sentences):
                for t, char in enumerate(sentence):
                    x[i, t, char_indices[char]] = 1
                y[i, char_indices[next_chars[i]]] = 1

            # LSTMモデルをビルドする
            print('Build model...')
            model = Sequential()
            model.add(LSTM(128, input_shape=(None, len(chars))))
            model.add(Dense(len(chars)))
            model.add(Activation('softmax'))
            optimizer = RMSprop(lr=0.01)
            model.compile(loss='categorical_crossentropy', optimizer=optimizer)

            # 学習を開始する
            history = model.fit(x, y, batch_size=128, epochs=3)

            # モデルの重みを保存する
            self.save_model_weights(model, lstm_model_path)

            # Training lossとValidation Lossをプロットする
            loss = history.history["loss"]
            epochs = range(1, len(loss) + 1)
            plt.plot(epochs, loss, "bo", label="Training loss")
            plt.title("Training loss")
            plt.legend()
            plt.savefig("loss.png")
            plt.close()

    def save_model(self, model, filepath):
        try:
            model.save(filepath)
            print(f"モデルを保存しました {filepath}")
        except:
            print(f"モデルを保存に失敗しました {filepath}")

    def save_model_weights(self, model, filepath):
        try:
            model.save_weights(filepath)
            print(f"重みデータを保存しました {filepath}")
        except:
            print(f"重みデータを保存にに失敗しました {filepath}")



if __name__ == '__main__':
    trainer = Trainer()
    trainer.train('./data/teradashin.txt')