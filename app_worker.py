from PyQt5.QtCore import QRunnable, pyqtSlot
import config
from logger import logger
from crawler.downloader import Downloader

class AppWorker(QRunnable):

    def __init__(self, gui):
        super(AppWorker, self).__init__()
        self.gui = gui
        self.downloader = Downloader(gui)

    @pyqtSlot()
    def run(self):
        while True:
            self.downloader.run()