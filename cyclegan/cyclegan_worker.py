from PyQt5.QtCore import QRunnable, pyqtSlot
import config
from logger import logger
from cyclegan.predictor import Predictor

class CycleganWorker(QRunnable):

    def __init__(self, gui):
        super(CycleganWorker, self).__init__()
        self.gui = gui
        self.cyclegan = Predictor(gui)

    @pyqtSlot()
    def run(self):
        while True:
            self.cyclegan.predict()