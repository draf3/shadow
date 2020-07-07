import sys, random
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import config
from logger import logger
from cyclegan.cyclegan_worker import CycleganWorker
from cyclegan.predictor import Predictor as CycleGANPredictor
from lstm.lstm_worker import LSTMWorker
from lstm.predictor import Predictor as LSTMPredictor
from lstm.trainer import Trainer
from crawler.downloader import Downloader
from app_worker import AppWorker
from trend_store import TrendStore

class GUI(QWidget):
    def __init__(self):
        super().__init__()

        self.is_running = False

        # Widget
        self.framerate_label = QLabel("frame rate")
        self.framerate_spinbox = QSpinBox()
        self.framerate_spinbox.setRange(1, 120)
        self.framerate_spinbox.setValue(60)
        self.frame_par_image_label = QLabel("frame par image")
        self.frame_par_image_spinbox = QSpinBox()
        self.frame_par_image_spinbox.setRange(1, 300)
        self.frame_par_image_spinbox.setValue(30)
        self.blur_checkbox = QCheckBox('blur', self)
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
        self.blend_checkbox = QCheckBox('blend', self)
        self.blend_checkbox.setChecked(True)
        self.smaller_checkbox = QCheckBox('smaller', self)
        self.smaller_checkbox.setChecked(True)
        self.capture_checkbox = QCheckBox('capture', self)
        self.save_checkbox = QCheckBox('save', self)
        self.save_checkbox.setChecked(True)
        self.image_input_label = QLabel("input")
        self.image_preprocess_label = QLabel("preprocess")
        self.image_output_label = QLabel("output")
        self.image = QLabel(self)
        # self.trend_combobox = QComboBox(self)

        # for i, key in enumerate(config.TREND):
        #     name = config.TREND[key]['NAME']
        #     self.trend_combobox.addItem(name)

        self.random_checkbox = QCheckBox('random', self)
        self.sentence_text = QLabel("", self)
        self.sentence_text.resize(512, 100)
        self.sentence_text.setWordWrap(True)
        generate_btn = QPushButton("generate", self)

        # Layout
        framerate_hbox = QHBoxLayout()
        framerate_hbox.addWidget(self.framerate_spinbox)
        framerate_hbox.addWidget(self.framerate_label)
        framerate_hbox.addStretch(1)
        maxframe_hbox = QHBoxLayout()
        maxframe_hbox.addWidget(self.frame_par_image_spinbox)
        maxframe_hbox.addWidget(self.frame_par_image_label)
        maxframe_hbox.addStretch(1)
        trend_hbox = QHBoxLayout()
        # trend_hbox.addWidget(self.trend_combobox)
        trend_hbox.addWidget(self.random_checkbox)
        generate_hbox = QHBoxLayout()
        generate_hbox.addWidget(generate_btn)
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
        vbox.addWidget(self.capture_checkbox)
        vbox.addWidget(self.save_checkbox)
        vbox.addLayout(generate_hbox)
        vbox.addWidget(self.sentence_text)
        self.setLayout(vbox)

        # Window
        # self.setGeometry(300, 300, 532, 440)
        self.title = 'shadow app'
        self.show()

        self.trend_store = TrendStore()
        self.trainer = Trainer(self)
        self.cyclegan_predictor = CycleGANPredictor(self)
        self.lstm_predictor = LSTMPredictor(self)


        # Thread
        self.threadpool = QThreadPool()
        self.app_worker = AppWorker(self)
        # self.downloader = Downloader(self)
        # self.cyclegan_worker = CycleganWorker(self)
        # self.lstm_worker = LSTMWorker(self)

        # Event
        generate_btn.clicked.connect(self.generate_handler)


    @property
    def framerate(self):
        return self.framerate_spinbox.value()

    @property
    def frame_par_image(self):
        return self.frame_par_image_spinbox.value()

    @property
    def trend_idx(self):
        return self.trend_combobox.currentIndex()

    @property
    def trend_name(self):
        return self.trend_combobox.currentText()

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
    def sentence(self):
        return self.sentence_text.text()

    @sentence.setter
    def sentence(self, text):
        self.sentence_text.setText(text)

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

    def is_capture(self):
        return self.capture_checkbox.isChecked()

    def is_save(self):
        return self.save_checkbox.isChecked()

    def render_img(self, image):
        self.image.setPixmap(QPixmap.fromImage(image))

    def generate_handler(self):
        self.is_running = True
        self.threadpool.start(self.app_worker)
        # self.threadpool.start(self.cyclegan_worker)
        # self.threadpool.start(self.lstm_worker)