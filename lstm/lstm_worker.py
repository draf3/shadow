from PyQt5.QtCore import QRunnable, pyqtSlot
import config
from logger import logger
from lstm.predictor import Predictor
from jtalk import JTalk

class LSTMWorker(QRunnable):

    def __init__(self, gui):
        super(LSTMWorker, self).__init__()
        self.gui = gui
        self.jtalk = JTalk(gui)
        self.prev_trend_idx = 0

        self.predictors = []
        for i, key in enumerate(config.TREND):
            data_path = config.TREND[key]['LSTM_TXT_PATH']
            model_path = config.TREND[key]['LSTM_MODEL_PATH']
            self.predictors.append(Predictor(data_path, model_path))

    @pyqtSlot()
    def run(self):
        while True:
            sentence = self.predictors[self.gui.trend_idx].predict()
            self.gui.sentence = sentence
            self.jtalk.say(sentence)