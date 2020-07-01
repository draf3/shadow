from __future__ import print_function
from keras.callbacks import LambdaCallback
from keras.models import Sequential, load_model
from keras.layers import Dense, Activation
from keras.layers import LSTM
from keras.optimizers import RMSprop
from keras.utils.data_utils import get_file
import matplotlib.pyplot as plt  # 追加
import numpy as np
import random
import sys
import io

def save_model(model, filepath):
    try:
        model.save(filepath)
        print(f"モデルを保存しました {filepath}")
    except:
        print(f"モデルを保存に失敗しました {filepath}")


def load_model_weights(model, filepath):
    try:
        model.load_weights(filepath)
        print(f"重みデータを読み込みました {filepath}")
    except:
        print(f"重みデータを読み込みに失敗しました {filepath}")


def save_model_weights(model, filepath):
    try:
        model.save_weights(filepath)
        print(f"重みデータを保存しました {filepath}")
    except:
        print(f"重みデータを保存にに失敗しました {filepath}")

is_finetuning = False  # 重みデータを読み込み再学習させるか
 
path = './teradashin.txt'
with io.open(path, encoding='utf-8') as f:
    text = f.read().lower()
print('corpus length:', len(text))
 
chars = sorted(list(set(text)))
print('total chars:', len(chars))
char_indices = dict((c, i) for i, c in enumerate(chars))
indices_char = dict((i, c) for i, c in enumerate(chars))
 
# cut the text in semi-redundant sequences of maxlen characters
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
 
print('Vectorization...')
x = np.zeros((len(sentences), maxlen, len(chars)), dtype=np.bool)
y = np.zeros((len(sentences), len(chars)), dtype=np.bool)
for i, sentence in enumerate(sentences):
    for t, char in enumerate(sentence):
        x[i, t, char_indices[char]] = 1
    y[i, char_indices[next_chars[i]]] = 1

if is_finetuning:
    print('Load model...')
    model = load_model('./lstm200223.h5')
    load_model_weights(model, './lstm_weight200223.5')

else:
    # build the model: a single LSTM
    print('Build model...')
    model = Sequential()
    model.add(LSTM(128, input_shape=(None, len(chars))))
    model.add(Dense(len(chars)))
    model.add(Activation('softmax'))

    optimizer = RMSprop(lr=0.01)
    model.compile(loss='categorical_crossentropy', optimizer=optimizer)

history = model.fit(x, y,
                    batch_size=128,
                    epochs=100)

save_model(model, './lstm_teradashino.h5')
save_model_weights(model, './lstm_weight_teradashin.h5')
 
# Plot Training loss & Validation Loss
loss = history.history["loss"]
epochs = range(1, len(loss) + 1)
plt.plot(epochs, loss, "bo", label = "Training loss" )
plt.title("Training loss")
plt.legend()
plt.savefig("loss.png")
plt.close() 