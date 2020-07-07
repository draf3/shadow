from __future__ import print_function
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.layers import LSTM
from keras.optimizers import RMSprop
import tensorflow as tf
from tensorflow.python.keras.backend import set_session
import numpy as np
import sys
import io
import config
from logger import logger
import re
import random
from PyQt5.QtWidgets import *
import traceback


class Predictor():
    def __init__(self, gui):
        self.sess = tf.Session()
        self.graph = tf.get_default_graph()
        set_session(self.sess)
        self.gui = gui

    def setup(self, input_texts_path, lstm_model_path):
        with self.graph.as_default():
            set_session(self.sess)
            with io.open(input_texts_path, encoding='utf-8') as f:
                self.text = f.read().lower()
            logger.debug(f'corpus length:{len(self.text)}')

            self.end_point_indexes = [str.end() for str in re.finditer('。', self.text)]

            self.chars = sorted(list(set(self.text)))
            logger.debug(f'total chars:{len(self.chars)}')

            self.char_indices = dict((c, i) for i, c in enumerate(self.chars))
            self.indices_char = dict((i, c) for i, c in enumerate(self.chars))

            self.max_sentence = 200
            self.maxlen = 10
            self.temperature = 0.2
            step = 1
            sentences = []
            next_chars = []

            for i in range(0, len(self.text) - self.maxlen, step):
                sentences.append(self.text[i: i + self.maxlen])
                next_chars.append(self.text[i + self.maxlen])
            logger.debug(f'nb sequences:{len(sentences)}')
            logger.debug(sentences)
            logger.debug(next_chars)

            logger.debug('Vectorization...')
            x = np.zeros((len(sentences), self.maxlen, len(self.chars)), dtype=np.bool)
            y = np.zeros((len(sentences), len(self.chars)), dtype=np.bool)
            for i, sentence in enumerate(sentences):
                for t, char in enumerate(sentence):
                    x[i, t, self.char_indices[char]] = 1
                y[i, self.char_indices[next_chars[i]]] = 1

            self.model = Sequential()
            self.model.add(LSTM(128, input_shape=(self.maxlen, len(self.chars))))
            self.model.add(Dense(len(self.chars)))
            self.model.add(Activation('softmax'))

            self.model.load_weights(lstm_model_path)

            optimizer = RMSprop(lr=0.01)
            self.model.compile(loss='categorical_crossentropy', optimizer=optimizer)


    def sample(self, preds, temperature=1.0):
        preds = np.asarray(preds).astype('float64')
        preds = np.log(preds) / temperature
        exp_preds = np.exp(preds)
        preds = exp_preds / np.sum(exp_preds)
        probas = np.random.multinomial(1, preds, 1)
        return np.argmax(probas)

    def predict(self):
        with self.graph.as_default():
            set_session(self.sess)

            try:

                while True:
                    start_index = random.choice(self.end_point_indexes)
                    if len(self.text) - start_index > self.maxlen:
                        break

                sentence = self.text[start_index: start_index + self.maxlen]

                # sentence = word.lower()
                logger.debug('Generating text')

                for diversity in [self.temperature]:

                    generated = ''
                    generated += sentence
                    logger.debug('Generating with seed: "' + sentence + '"')
                    sys.stdout.write(generated)

                    for i in range(self.max_sentence):
                        sentence, generated, next_char = self.generate_character(
                            diversity, sentence, generated)

                        QApplication.processEvents()

                        if next_char == "。":
                            break

                    print()

            except Exception as e:
                print(traceback.format_exc())

            finally:
                return generated

    def generate_character(self, diversity, sentence, generated):
        x_pred = np.zeros((1, self.maxlen, len(self.chars)))
        for t, char in enumerate(sentence):
            x_pred[0, t, self.char_indices[char]] = 1.

        preds = self.model.predict(x_pred, verbose=0)[0]
        next_index = self.sample(preds, diversity)
        next_char = self.indices_char[next_index]

        new_generated = generated + next_char
        new_sentence = sentence[1:] + next_char

        sys.stdout.write(next_char)
        sys.stdout.flush()

        return new_sentence, new_generated, next_char