import time
from PyQt5.QtCore import QRunnable, pyqtSlot
from app import App

class AppWorker(QRunnable):

    def __init__(self, gui):
        super(AppWorker, self).__init__()
        self.gui = gui
        self.app = App(gui)

    @pyqtSlot()
    def run(self):
        while True:
            self.app.run()
            time.sleep(self.gui.gen_waiting_time * 60)