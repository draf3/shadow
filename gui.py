import sys
import time
from blinker import signal
from utils.logger import logger
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer, QThread, QObject, pyqtSignal, pyqtSlot
import config
import random
from glob import glob
import numpy as np

class GUI(QWidget):
    trend_id = pyqtSignal(int)
    framerate = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.is_running = False

        # Thread
        self.sentence_worker = SentenceWorker()
        self.sentence_worker_thread = QThread()
        self.sentence_worker.moveToThread(self.sentence_worker_thread)
        self.sentence_worker_thread.start()

        self.image_worker = ImageWorker()
        self.image_worker_thread = QThread()
        self.image_worker.moveToThread(self.image_worker_thread)
        self.image_worker_thread.start()

        # Widget
        self.framerate_label = QLabel("frame rate")
        self.framerate_spinbox = QSpinBox()
        self.framerate_spinbox.setRange(1, 120)
        self.framerate_spinbox.setValue(60)

        self.max_frame_label = QLabel("max frame")
        self.max_frame_spinbox = QSpinBox()
        self.max_frame_spinbox.setRange(1, 300)
        self.max_frame_spinbox.setValue(30)

        self.blur_checkbox = QCheckBox('blur', self)
        # self.blur_checkbox.setChecked(True)
        self.blur_ax_spinbox = QSpinBox()
        self.blur_ax_spinbox.setRange(1, 99)
        self.blur_ax_spinbox.setSingleStep(2)
        self.blur_ax_spinbox.setValue(11)
        self.blur_ay_spinbox = QSpinBox()
        self.blur_ay_spinbox.setRange(1, 99)
        self.blur_ay_spinbox.setSingleStep(2)
        self.blur_ay_spinbox.setValue(11)

        self.binary_checkbox = QCheckBox('binary', self)
        self.binary_t_spinbox = QSpinBox()
        self.binary_t_spinbox.setRange(0, 255)
        self.binary_t_spinbox.setValue(127)

        self.canny_checkbox = QCheckBox('canny', self)
        # self.canny_checkbox.setChecked(True)
        self.canny_t1_spinbox = QSpinBox()
        self.canny_t1_spinbox.setRange(0, 255)
        self.canny_t1_spinbox.setValue(10)
        self.canny_t2_spinbox = QSpinBox()
        self.canny_t2_spinbox.setRange(0, 255)
        self.canny_t2_spinbox.setValue(20)

        self.morphology_checkbox = QCheckBox('morphology', self)
        self.morphology_k_spinbox = QSpinBox()
        self.morphology_k_spinbox.setRange(1, 10)
        self.morphology_k_spinbox.setValue(5)

        self.invert_checkbox = QCheckBox('invert', self)
        # self.invert_checkbox.setChecked(True)

        self.blend_checkbox = QCheckBox('blend', self)
        self.blend_checkbox.setChecked(True)

        self.smaller_checkbox = QCheckBox('smaller', self)
        self.smaller_checkbox.setChecked(True)

        self.mask_checkbox = QCheckBox('mask', self)
        # self.mask_checkbox.setChecked(True)

        self.capture_checkbox = QCheckBox('capture', self)
        # self.capture_checkbox.setChecked(True)

        self.mask_path_textbox = QLineEdit(self.rand_mask_path(), self)

        self.save_checkbox = QCheckBox('save', self)
        # self.save_checkbox.setChecked(True)

        self.image_input_label = QLabel("input")
        self.image_preprocess_label = QLabel("preprocess")
        self.image_output_label = QLabel("output")
        self.image = QLabel(self)

        self.trend_combobox = QComboBox(self)
        for i, key in enumerate(config.TREND):
            name = config.TREND[key]['NAME']
            self.trend_combobox.addItem(name)

        self.auto_checkbox = QCheckBox('auto', self)
        self.auto_checkbox.setChecked(True)
        self.random_checkbox = QCheckBox('random', self)
        # self.random_checkbox.setChecked(True)

        self.sentence_text = QLabel("", self)
        self.sentence_text.resize(512, 100)
        self.sentence_text.setWordWrap(True)

        generate_sentence_btn = QPushButton("generate sentence", self)

        # Layout
        framerate_hbox = QHBoxLayout()
        framerate_hbox.addWidget(self.framerate_spinbox)
        framerate_hbox.addWidget(self.framerate_label)
        framerate_hbox.addStretch(1)

        maxframe_hbox = QHBoxLayout()
        maxframe_hbox.addWidget(self.max_frame_spinbox)
        maxframe_hbox.addWidget(self.max_frame_label)
        maxframe_hbox.addStretch(1)

        trend_hbox = QHBoxLayout()
        trend_hbox.addWidget(self.trend_combobox)
        # trend_hbox.addWidget(self.auto_checkbox)
        trend_hbox.addWidget(self.random_checkbox)
        # trend_hbox.addStretch(1)

        generate_hbox = QHBoxLayout()
        generate_hbox.addWidget(generate_sentence_btn)
        generate_hbox.addWidget(self.auto_checkbox)
        # generate_hbox.addStretch(1)

        blur_hbox = QHBoxLayout()
        blur_hbox.addWidget(self.blur_checkbox)
        blur_hbox.addWidget(self.blur_ax_spinbox)
        blur_hbox.addWidget(self.blur_ay_spinbox)
        blur_hbox.addStretch(1)

        binary_hbox = QHBoxLayout()
        binary_hbox.addWidget(self.binary_checkbox)
        binary_hbox.addWidget(self.binary_t_spinbox)
        binary_hbox.addStretch(1)

        canny_hbox = QHBoxLayout()
        canny_hbox.addWidget(self.canny_checkbox)
        canny_hbox.addWidget(self.canny_t1_spinbox)
        canny_hbox.addWidget(self.canny_t2_spinbox)
        canny_hbox.addStretch(1)

        morphology_hbox = QHBoxLayout()
        morphology_hbox.addWidget(self.morphology_checkbox)
        morphology_hbox.addWidget(self.morphology_k_spinbox)
        morphology_hbox.addStretch(1)

        mask_hbox = QHBoxLayout()
        mask_hbox.addWidget(self.mask_checkbox)
        mask_hbox.addWidget(self.mask_path_textbox)
        mask_hbox.addStretch(1)

        image_hbox = QHBoxLayout()
        image_hbox.addWidget(self.image_input_label)
        image_hbox.addWidget(self.image_preprocess_label)
        image_hbox.addWidget(self.image_output_label)


        vbox = QVBoxLayout()
        vbox.addLayout(image_hbox)
        vbox.addWidget(self.image)
        vbox.addLayout(trend_hbox)
        vbox.addLayout(framerate_hbox)
        vbox.addLayout(maxframe_hbox)
        vbox.addLayout(blur_hbox)
        vbox.addLayout(binary_hbox)
        vbox.addLayout(canny_hbox)
        vbox.addLayout(morphology_hbox)
        vbox.addWidget(self.invert_checkbox)
        vbox.addWidget(self.blend_checkbox)
        vbox.addWidget(self.smaller_checkbox)
        vbox.addLayout(mask_hbox)
        vbox.addWidget(self.capture_checkbox)
        vbox.addWidget(self.save_checkbox)
        vbox.addLayout(generate_hbox)
        vbox.addWidget(self.sentence_text)
        self.setLayout(vbox)



        # Event
        # self.on_start_jtalk = signal(config.EVENT['ON_START_JTALK'])
        self.framerate_spinbox.valueChanged.connect(self.changed_framerate_handler)
        generate_sentence_btn.clicked.connect(self.generate_sentence_handler)
        self.trend_id.connect(self.sentence_worker.generate_sentence_handler)
        self.framerate.connect(self.image_worker.changed_framerate_handler)

        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.change_trend)
        self.timer.start(5000)

        # Window
        # self.setGeometry(300, 300, 532, 440)
        self.title = 'shadow app'
        self.show()

    @property
    def max_frame(self):
        return self.max_frame_spinbox.value()

    @property
    def trend_idx(self):
        return self.trend_combobox.currentIndex()

    @property
    def binary_t(self):
        return self.binary_t_spinbox.value()

    @property
    def blur_ax(self):
        return self.blur_ax_spinbox.value()

    @property
    def blur_ay(self):
        return self.blur_ay_spinbox.value()

    @property
    def canny_t1(self):
        return self.canny_t1_spinbox.value()

    @property
    def canny_t2(self):
        return self.canny_t2_spinbox.value()

    @property
    def morphology_k(self):
        return self.morphology_k_spinbox.value()

    @property
    def mask_path(self):
        return self.mask_path_textbox.text()

    def is_binary(self):
        return self.binary_checkbox.isChecked()

    def is_blur(self):
        return self.blur_checkbox.isChecked()

    def is_canny(self):
        return self.canny_checkbox.isChecked()

    def is_morphology(self):
        return self.morphology_checkbox.isChecked()

    def is_invert(self):
        return self.invert_checkbox.isChecked()

    def is_blend(self):
        return self.blend_checkbox.isChecked()

    def is_smaller(self):
        return self.smaller_checkbox.isChecked()

    def is_mask(self):
        return self.mask_checkbox.isChecked()

    def is_capture(self):
        return self.capture_checkbox.isChecked()

    def is_save(self):
        return self.save_checkbox.isChecked()

    def change_trend(self):
        if self.random_checkbox.isChecked() and not self.is_running:
            next_idx = random.randrange(self.trend_combobox.count())
            self.trend_combobox.setCurrentIndex(next_idx)

    def render_img(self, image):
        self.image.setPixmap(QPixmap.fromImage(image))

    def render_img_handler(self, _, img):
        self.image.setPixmap(QPixmap.fromImage(img))

    def changed_framerate_handler(self):
        framerate = self.framerate_spinbox.value()
        self.framerate.emit(int(framerate))

    def generate_sentence_handler(self):
        self.is_running = True
        id = self.trend_combobox.currentIndex()
        self.trend_id.emit(int(id))

    def predicted_sentence_handler(self, _, sentence):
        self.sentence_text.setText(sentence)
        # self.on_start_jtalk.send(sentence=sentence)

    def end_jtalk_handler(self, _):
        if self.random_checkbox.isChecked():
            next_idx = random.randrange(self.trend_combobox.count())
            self.trend_combobox.setCurrentIndex(next_idx)

        if self.auto_checkbox.isChecked():
            mask_path = self.rand_mask_path()
            self.mask_path_textbox.setText(mask_path)
            self.generate_sentence_handler()
        else:
            self.is_running = False

    def rand_mask_path(self):
        paths = glob('images/*.png')
        img_paths = np.random.choice(paths, size=1)
        return img_paths[0]

    def closeEvent(self, e):
        sys.exit()


class SentenceWorker(QObject):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.on_select_trend_word = signal(config.EVENT['ON_SELECT_TREND_WORD'])

    @pyqtSlot(int)
    def generate_sentence_handler(self, id=0):
        self.on_select_trend_word.send(int(id))


class ImageWorker(QObject):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.on_changed_framerate = signal(config.EVENT['ON_CHANGED_FRAMERATE'])

    @pyqtSlot(int)
    def changed_framerate_handler(self, framerate=60):
        logger.debug(framerate)
        self.on_changed_framerate.send(int(framerate))