import sys
import time
import threading
from PyQt5.QtWidgets import QApplication
from blinker import signal
import config
from cyclegan.cyclegan import CycleGAN
from lstm.predictor import Predictor
from spout import SPOUT
from gui import GUI
from jtalk import JTalk
from utils.logger import logger

sys.setrecursionlimit(2000)

def init_lstm():
    predictors = []
    for i, key in enumerate(config.TREND):
        text_path = config.TREND[key]['LSTM_TXT_PATH']
        model_path = config.TREND[key]['LSTM_MODEL_PATH']
        predictor = Predictor(i, text_path, model_path)
        predictors.append(predictor)

    on_select_trend_word = signal(config.EVENT['ON_SELECT_TREND_WORD'])
    for i, predictor in enumerate(predictors):
        on_select_trend_word.connect(predictor.predict, sender=i)

    return predictors

def run():
    prev_trend_idx = 0
    while True:
        for i, key in enumerate(config.TREND):
            if i == gui.trend_idx:
                if prev_trend_idx != gui.trend_idx:
                    gan.frame = 0
                    jtalk.count = 0
                img_dir = config.TREND[key]['CYCLEGAN_IMG_DIR']
                dst_img_dir = config.TREND[key]['DST_IMG_DIR']
                dst_audio_dir = config.TREND[key]['DST_AUDIO_DIR']
                gan.is_blur = gui.is_blur()
                gan.is_binary = gui.is_binary()
                gan.is_canny = gui.is_canny()
                gan.is_morphology = gui.is_morphology()
                gan.is_invert = gui.is_invert()
                gan.is_blend = gui.is_blend()
                gan.is_smaller = gui.is_smaller()
                gan.is_mask = gui.is_mask()
                gan.is_capture = gui.is_capture()
                gan.max_frame = gui.max_frame
                gan.binary_t = gui.binary_t
                gan.blur_ax = gui.blur_ax
                gan.blur_ay = gui.blur_ay
                gan.canny_t1 = gui.canny_t1
                gan.canny_t2 = gui.canny_t2
                gan.morphology_k = gui.morphology_k
                gan.mask_path = gui.mask_path
                jtalk.dst_audio_dir = dst_audio_dir
                jtalk.is_save = gui.is_save()
                if gui.is_save():
                    gan.predict(img_dir, dst_img_dir)
                else:
                    gan.predict(img_dir)

        prev_trend_idx = gui.trend_idx

def run_spout():
    spout = SPOUT()
    while True:
        time.sleep(0.01)
        spout.render(gan.simg)

if __name__ == '__main__':

    app = QApplication(sys.argv)

    #JTalk
    jtalk = JTalk()

    # GUI
    gui = GUI()

    # GUI Event
    on_predicted_sentence = signal(config.EVENT['ON_PREDICTED_SENTENCE'])
    on_predicted_sentence.connect(gui.predicted_sentence_handler)
    on_end_jtalk = signal(config.EVENT['ON_END_JTALK'])
    on_end_jtalk.connect(gui.end_jtalk_handler)
    on_render_img = signal(config.EVENT['ON_RENDER_IMG'])
    on_render_img.connect(gui.render_img_handler)
    on_start_jtalk = signal(config.EVENT['ON_START_JTALK'])
    on_start_jtalk.connect(jtalk.say)

    # LSTM
    lstm = init_lstm()

    # CycleGAN
    gan = CycleGAN()

    # CycleGAN Event
    on_changed_framerate = signal(config.EVENT['ON_CHANGED_FRAMERATE'])
    on_changed_framerate.connect(gan.changed_framerate_handler)


    threads = []
    t = threading.Thread(target=run_spout)
    t.setDaemon(True)
    t.start()
    threads.append(t)

    # Spout
    # t = threading.Thread(target=run_spout)
    # t.setDaemon(True)
    # t.start()
    # threads.append(t)

    # Loop
    run()

    sys.exit(gui.exec_())