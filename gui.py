import random
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from cyclegan.predictor import Predictor as CycleGANPredictor
from lstm.predictor import Predictor as LSTMPredictor
from lstm.trainer import Trainer
from app_worker import AppWorker
from trend import TrendStore, TrendFilter
from osc_sender import OscSender
from logger import logger
import config


class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

        self.trend_store = TrendStore()
        self.trend_filter = TrendFilter(self, self.trend_store)
        self.trainer = Trainer(self)
        self.cyclegan_predictor = CycleGANPredictor(self)
        self.lstm_predictor = LSTMPredictor(self)

        # NetWork
        self.osc_sender = OscSender(self.ip, self.port)

        # Thread
        self.threadpool = QThreadPool()
        self.app_worker = AppWorker(self)

        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.change_trend)
        self.timer.start(self.send_data_interval * 1000)

    def init_ui(self):
        # Widget
        self.dl_tweet_count_label = QLabel("download tweet count")
        self.dl_tweet_count_spinbox = QSpinBox()
        self.dl_tweet_count_spinbox.setRange(50, 200)
        self.dl_tweet_count_spinbox.setValue(100)
        self.dl_image_count_label = QLabel("download image count")
        self.dl_image_count_spinbox = QSpinBox()
        self.dl_image_count_spinbox.setRange(50, 400)
        self.dl_image_count_spinbox.setValue(100)
        self.trend_count_label = QLabel("trend count")
        self.trend_count_spinbox = QSpinBox()
        self.trend_count_spinbox.setRange(1, 10)
        self.trend_count_spinbox.setValue(5)
        self.gen_image_count_label = QLabel("generate image count")
        self.gen_image_count_spinbox = QSpinBox()
        self.gen_image_count_spinbox.setRange(10, 100)
        self.gen_image_count_spinbox.setValue(10)
        self.gen_audio_count_label = QLabel("generate audio count")
        self.gen_audio_count_spinbox = QSpinBox()
        self.gen_audio_count_spinbox.setRange(5, 50)
        self.gen_audio_count_spinbox.setValue(5)
        self.gen_waiting_time_label = QLabel("generate waiting time (min)")
        self.gen_waiting_time_spinbox = QSpinBox()
        self.gen_waiting_time_spinbox.setRange(0, 1440)
        self.gen_waiting_time_spinbox.setValue(1)
        self.send_data_interval_label = QLabel("send data interval (sec)")
        self.send_data_interval_spinbox = QSpinBox()
        self.send_data_interval_spinbox.setRange(0, 600)
        self.send_data_interval_spinbox.setValue(5)
        self.send_data_days_label = QLabel("send data (days ago)")
        self.send_data_days_spinbox = QSpinBox()
        self.send_data_days_spinbox.setRange(0, 30)
        self.send_data_days_spinbox.setValue(0)

        self.ip_label = QLabel("ip")
        self.ip_edit = QLineEdit('127.0.0.1', self)
        self.port_label = QLabel("port")
        self.port_edit = QLineEdit('10000', self)
        self.output_images_addr_label = QLabel("output_images_addr")
        self.output_images_addr_edit = QLineEdit('/output_images_dir', self)
        self.output_audios_addr_label = QLabel("output_audios_addr")
        self.output_audios_addr_edit = QLineEdit('/output_audios_dir', self)

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
        self.save_checkbox = QCheckBox('save', self)
        self.save_checkbox.setChecked(True)
        self.image_input_label = QLabel("input image")
        self.image_preprocess_label = QLabel("preprocess image")
        self.image_output_label = QLabel("output image")
        self.image = QLabel(self)
        # self.trend_combobox = QComboBox(self)
        generate_btn = QPushButton("generate", self)
        self.sentence_text = QLabel("", self)
        self.sentence_text.resize(512, 100)
        self.sentence_text.setWordWrap(True)

        # Layout
        dl_tweet_count_hbox = QHBoxLayout()
        dl_tweet_count_hbox.addWidget(self.dl_tweet_count_label)
        dl_tweet_count_hbox.addWidget(self.dl_tweet_count_spinbox)
        dl_image_count_hbox = QHBoxLayout()
        dl_image_count_hbox.addWidget(self.dl_image_count_label)
        dl_image_count_hbox.addWidget(self.dl_image_count_spinbox)
        trend_count_hbox = QHBoxLayout()
        trend_count_hbox.addWidget(self.trend_count_label)
        trend_count_hbox.addWidget(self.trend_count_spinbox)
        gen_image_count_hbox = QHBoxLayout()
        gen_image_count_hbox.addWidget(self.gen_image_count_label)
        gen_image_count_hbox.addWidget(self.gen_image_count_spinbox)
        gen_audio_count_hbox = QHBoxLayout()
        gen_audio_count_hbox.addWidget(self.gen_audio_count_label)
        gen_audio_count_hbox.addWidget(self.gen_audio_count_spinbox)
        gen_waiting_time_hbox = QHBoxLayout()
        gen_waiting_time_hbox.addWidget(self.gen_waiting_time_label)
        gen_waiting_time_hbox.addWidget(self.gen_waiting_time_spinbox)
        send_data_interval_hbox = QHBoxLayout()
        send_data_interval_hbox.addWidget(self.send_data_interval_label)
        send_data_interval_hbox.addWidget(self.send_data_interval_spinbox)
        send_data_days_hbox = QHBoxLayout()
        send_data_days_hbox.addWidget(self.send_data_days_label)
        send_data_days_hbox.addWidget(self.send_data_days_spinbox)

        ip_hbox = QHBoxLayout()
        ip_hbox.addWidget(self.ip_label)
        ip_hbox.addWidget(self.ip_edit)
        port_hbox = QHBoxLayout()
        port_hbox.addWidget(self.port_label)
        port_hbox.addWidget(self.port_edit)
        output_images_addr_hbox = QHBoxLayout()
        output_images_addr_hbox.addWidget(self.output_images_addr_label)
        output_images_addr_hbox.addWidget(self.output_images_addr_edit)
        output_audios_addr_hbox = QHBoxLayout()
        output_audios_addr_hbox.addWidget(self.output_audios_addr_label)
        output_audios_addr_hbox.addWidget(self.output_audios_addr_edit)

        framerate_hbox = QHBoxLayout()
        framerate_hbox.addWidget(self.framerate_label)
        framerate_hbox.addWidget(self.framerate_spinbox)
        maxframe_hbox = QHBoxLayout()
        maxframe_hbox.addWidget(self.frame_par_image_label)
        maxframe_hbox.addWidget(self.frame_par_image_spinbox)
        trend_hbox = QHBoxLayout()
        generate_hbox = QHBoxLayout()
        generate_hbox.addWidget(generate_btn)
        blur_hbox = QHBoxLayout()
        blur_hbox.addWidget(self.blur_checkbox)
        blur_hbox.addWidget(self.blur_ax_spinbox)
        blur_hbox.addWidget(self.blur_ay_spinbox)
        binary_hbox = QHBoxLayout()
        binary_hbox.addWidget(self.binary_checkbox)
        binary_hbox.addWidget(self.binary_t_spinbox)
        canny_hbox = QHBoxLayout()
        canny_hbox.addWidget(self.canny_checkbox)
        canny_hbox.addWidget(self.canny_t1_spinbox)
        canny_hbox.addWidget(self.canny_t2_spinbox)
        morphology_hbox = QHBoxLayout()
        morphology_hbox.addWidget(self.morphology_checkbox)
        morphology_hbox.addWidget(self.morphology_k_spinbox)
        image_hbox = QHBoxLayout()
        image_hbox.addWidget(self.image_input_label)
        image_hbox.addWidget(self.image_preprocess_label)
        image_hbox.addWidget(self.image_output_label)

        gbox_app = QGroupBox('App Config')
        gbox_app.setCheckable(True)
        vbox_app = QVBoxLayout()
        vbox_app.addLayout(dl_tweet_count_hbox)
        vbox_app.addLayout(dl_image_count_hbox)
        vbox_app.addLayout(trend_count_hbox)
        vbox_app.addLayout(gen_image_count_hbox)
        vbox_app.addLayout(gen_audio_count_hbox)
        vbox_app.addLayout(gen_waiting_time_hbox)
        vbox_app.addLayout(send_data_interval_hbox)
        vbox_app.addLayout(send_data_days_hbox)
        gbox_app.setLayout(vbox_app)

        gbox_net = QGroupBox('Network')
        gbox_net.setCheckable(True)
        vbox_net = QVBoxLayout()
        vbox_net.addLayout(ip_hbox)
        vbox_net.addLayout(port_hbox)
        vbox_net.addLayout(output_images_addr_hbox)
        vbox_net.addLayout(output_audios_addr_hbox)
        gbox_net.setLayout(vbox_net)

        gbox_i_a = QGroupBox('Image and Audio')
        gbox_i_a.setCheckable(True)
        vbox_i_a = QVBoxLayout()
        vbox_i_a.addLayout(trend_hbox)
        vbox_i_a.addLayout(framerate_hbox)
        vbox_i_a.addLayout(maxframe_hbox)
        vbox_i_a.addLayout(blur_hbox)
        vbox_i_a.addLayout(binary_hbox)
        vbox_i_a.addLayout(canny_hbox)
        vbox_i_a.addLayout(morphology_hbox)
        vbox_i_a.addWidget(self.invert_checkbox)
        vbox_i_a.addWidget(self.blend_checkbox)
        vbox_i_a.addWidget(self.smaller_checkbox)
        vbox_i_a.addWidget(self.save_checkbox)
        gbox_i_a.setLayout(vbox_i_a)

        hbox = QHBoxLayout()
        hbox.addWidget(gbox_app)
        hbox.addWidget(gbox_i_a)
        hbox.addWidget(gbox_net)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addLayout(generate_hbox)
        vbox.addLayout(image_hbox)
        vbox.addWidget(self.image)
        vbox.addWidget(self.sentence_text)

        self.setLayout(vbox)

        # Event
        generate_btn.clicked.connect(self.generate_handler)
        self.send_data_interval_spinbox.valueChanged.connect(self.update_send_data_interval)
        self.ip_edit.textChanged.connect(self.change_network)
        self.port_edit.textChanged.connect(self.change_network)

        # Window
        # self.setGeometry(300, 300, 532, 600)
        self.title = 'shadow app'
        self.show()

    @property
    def dl_tweet_count(self):
        return self.dl_tweet_count_spinbox.value()

    @property
    def dl_image_count(self):
        return self.dl_image_count_spinbox.value()

    @property
    def trend_count(self):
        return self.trend_count_spinbox.value()

    @property
    def gen_image_count(self):
        return self.gen_image_count_spinbox.value()

    @property
    def gen_audio_count(self):
        return self.gen_audio_count_spinbox.value()

    @property
    def gen_waiting_time(self):
        return self.gen_waiting_time_spinbox.value()

    @property
    def send_data_interval(self):
        return self.send_data_interval_spinbox.value()

    @property
    def send_data_days_ago(self):
        return self.send_data_days_spinbox.value()

    @property
    def ip(self):
        return self.ip_edit.text()

    @property
    def port(self):
        return int(self.port_edit.text())

    @property
    def output_images_addr(self):
        return self.output_images_addr_edit.text()

    @property
    def output_audios_addr(self):
        return self.output_audios_addr_edit.text()

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

    def is_save(self):
        return self.save_checkbox.isChecked()

    def render_img(self, image):
        self.image.setPixmap(QPixmap.fromImage(image))

    def generate_handler(self):
        self.threadpool.start(self.app_worker)

    def update_send_data_interval(self, value):
        self.timer.setInterval(value * 1000)

    def change_trend(self):
        trend = self.trend_filter.random_select()
        self.osc_sender.send(self.output_images_addr, trend['output_images_dir'])
        self.osc_sender.send(self.output_audios_addr, trend['output_audios_dir'])

    def change_network(self):
        self.osc_sender = OscSender(self.ip, self.port)