from __future__ import print_function, division
from keras_contrib.layers.normalization.instancenormalization import InstanceNormalization
from keras.layers import Input, Dropout, Concatenate
from keras.layers.advanced_activations import LeakyReLU
from keras.layers.convolutional import UpSampling2D, Conv2D
from keras.models import Model
from keras.optimizers import Adam
import tensorflow as tf
from tensorflow.python.keras.backend import set_session, clear_session
import datetime
import numpy as np
import cv2
import os
from glob import glob
from PyQt5.QtGui import QImage
from PyQt5 import QtTest
from blinker import signal
import traceback
import config
from cyclegan.data_loader import DataLoader
from utils.logger import logger
from capturer import Capturer


class CycleGAN():
    def __init__(self):
        self.sess = tf.Session()
        self.graph = tf.get_default_graph()
        set_session(self.sess)
        self.simg = None
        self.qimg = None
        self.out_size = 256
        self.max_frame = 200
        self.framerate = 60
        self.frame = 0
        self.binary_t = 127
        self.blur_ax = 5
        self.blur_ay = 5
        self.morphology_k = 5
        self.canny_t1 = 100
        self.canny_t2 = 200
        self.mask_path = 'images'
        self.prev_src = None

        self.is_binary = False
        self.is_blur = False
        self.is_canny = False
        self.is_morphology = False
        self.is_invert = False
        self.is_blend = False
        self.is_smaller = False
        self.is_mask = False
        self.is_capture = None
        # Input shape
        self.img_rows = 256
        self.img_cols = 256
        self.channels = 3
        self.img_shape = (self.img_rows, self.img_cols, self.channels)

        self.capturer = None

        # Configure data loader
        self.data_loader = DataLoader(img_res=(self.img_rows, self.img_cols))

        # Calculate output shape of D (PatchGAN)
        patch = int(self.img_rows / 2**4)
        self.disc_patch = (patch, patch, 1)

        # Number of filters in the first layer of G and D
        self.gf = 32
        self.df = 64

        # Loss weights
        self.lambda_cycle = 10.0                    # Cycle-consistency loss
        self.lambda_id = 0.1 * self.lambda_cycle    # Identity loss

        optimizer = Adam(0.0002, 0.5)

        # Build and compile the discriminators
        self.d_A = self.build_discriminator()
        self.d_B = self.build_discriminator()
        self.d_A.compile(loss='mse',
            optimizer=optimizer,
            metrics=['accuracy'])
        self.d_B.compile(loss='mse',
            optimizer=optimizer,
            metrics=['accuracy'])

        #-------------------------
        # Construct Computational
        #   Graph of Generators
        #-------------------------

        # Build the generators
        self.g_AB = self.build_generator()
        self.g_BA = self.build_generator()

        # Input images from both domains
        img_A = Input(shape=self.img_shape)
        img_B = Input(shape=self.img_shape)

        # Translate images to the other domain
        fake_B = self.g_AB(img_A)
        fake_A = self.g_BA(img_B)
        # Translate images back to original domain
        reconstr_A = self.g_BA(fake_B)
        reconstr_B = self.g_AB(fake_A)
        # Identity mapping of images
        img_A_id = self.g_BA(img_A)
        img_B_id = self.g_AB(img_B)

        # For the combined model we will only train the generators
        self.d_A.trainable = False
        self.d_B.trainable = False

        # Discriminators determines validity of translated images
        valid_A = self.d_A(fake_A)
        valid_B = self.d_B(fake_B)

        # Combined model trains generators to fool discriminators
        self.combined = Model(inputs=[img_A, img_B],
                              outputs=[ valid_A, valid_B,
                                        reconstr_A, reconstr_B,
                                        img_A_id, img_B_id ])
        self.combined.compile(loss=['mse', 'mse',
                                    'mae', 'mae',
                                    'mae', 'mae'],
                            loss_weights=[  1, 1,
                                            self.lambda_cycle, self.lambda_cycle,
                                            self.lambda_id, self.lambda_id ],
                            optimizer=optimizer)
        self.load_model()

        self.on_render_img = signal(config.EVENT['ON_RENDER_IMG'])

    def build_generator(self):
        """U-Net Generator"""

        def conv2d(layer_input, filters, f_size=4):
            """Layers used during downsampling"""
            d = Conv2D(filters, kernel_size=f_size, strides=2, padding='same')(layer_input)
            d = LeakyReLU(alpha=0.2)(d)
            d = InstanceNormalization()(d)
            return d

        def deconv2d(layer_input, skip_input, filters, f_size=4, dropout_rate=0):
            """Layers used during upsampling"""
            u = UpSampling2D(size=2)(layer_input)
            u = Conv2D(filters, kernel_size=f_size, strides=1, padding='same', activation='relu')(u)
            if dropout_rate:
                u = Dropout(dropout_rate)(u)
            u = InstanceNormalization()(u)
            u = Concatenate()([u, skip_input])
            return u

        # Image input
        d0 = Input(shape=self.img_shape)

        # Downsampling
        d1 = conv2d(d0, self.gf)
        d2 = conv2d(d1, self.gf*2)
        d3 = conv2d(d2, self.gf*4)
        d4 = conv2d(d3, self.gf*8)

        # Upsampling
        u1 = deconv2d(d4, d3, self.gf*4)
        u2 = deconv2d(u1, d2, self.gf*2)
        u3 = deconv2d(u2, d1, self.gf)

        u4 = UpSampling2D(size=2)(u3)
        output_img = Conv2D(self.channels, kernel_size=4, strides=1, padding='same', activation='tanh')(u4)

        return Model(d0, output_img)

    def build_discriminator(self):

        def d_layer(layer_input, filters, f_size=4, normalization=True):
            """Discriminator layer"""
            d = Conv2D(filters, kernel_size=f_size, strides=2, padding='same')(layer_input)
            d = LeakyReLU(alpha=0.2)(d)
            if normalization:
                d = InstanceNormalization()(d)
            return d

        img = Input(shape=self.img_shape)

        d1 = d_layer(img, self.df, normalization=False)
        d2 = d_layer(d1, self.df*2)
        d3 = d_layer(d2, self.df*4)
        d4 = d_layer(d3, self.df*8)

        validity = Conv2D(1, kernel_size=4, strides=1, padding='same')(d4)

        return Model(img, validity)

    def predict(self, img_dir, dst_img_dir=None):
        with self.graph.as_default():
            set_session(self.sess)

            try:
                img_A = None
                fake_B = None

                if self.is_capture:
                    if self.capturer is None:
                        self.capturer = Capturer()

                    if self.capturer.frame is None:
                        origin = np.zeros(self.img_shape, dtype=np.uint8)
                    else:
                        frame = self.capturer.frame
                        origin = frame[60:420, 140:500]
                        origin = cv2.resize(origin, dsize=(self.img_rows, self.img_cols))
                        # origin = np.reshape(origin, (1, 256, 256, 3))
                        # origin = np.array(origin) / 127.5 - 1

                else:
                    paths = glob('%s/*.jpg' % img_dir)
                    img_paths = np.random.choice(paths, size=1)
                    origin = cv2.imread(img_paths[0])

                src = origin

                if self.is_mask:
                    # mask_paths = glob('%s/*.png' % self.mask_path)
                    # mask_paths = np.random.choice(mask_paths, size=1)
                    # img_mask = cv2.imread(mask_paths[0])
                    # src = cv2.bitwise_and(src, img_mask)

                    img_mask = cv2.imread(self.mask_path)
                    img_mask = cv2.GaussianBlur(img_mask, (self.blur_ax, self.blur_ay), 0)
                    src = cv2.bitwise_and(src, img_mask)

                    # img_mask = cv2.imread('images/frame/frame256x256.png', -1)
                    # alpha = img_mask[:, :, 3]
                    # alpha = np.array(alpha / 255.0, dtype=np.float32)
                    # alpha = cv2.cvtColor(alpha, cv2.COLOR_GRAY2BGR)
                    # src = np.array(src * (1.0 - alpha),  dtype=np.uint8)


                if self.is_blur:
                    src = cv2.GaussianBlur(src, (self.blur_ax, self.blur_ay), 0)

                if self.is_binary:
                    src = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
                    src = cv2.threshold(src, self.binary_t, 255, cv2.THRESH_BINARY)[1]
                    src = cv2.cvtColor(src, cv2.COLOR_GRAY2BGR)

                if self.is_canny:
                    src = cv2.Canny(src, self.canny_t1, self.canny_t2)
                    src = cv2.cvtColor(src, cv2.COLOR_GRAY2BGR)

                if self.is_morphology:
                    kernel = np.ones((self.morphology_k, self.morphology_k), np.uint8)
                    src = cv2.morphologyEx(src, cv2.MORPH_CLOSE, kernel)

                if self.is_invert:
                    src = cv2.bitwise_not(src)

                # if self.is_mask:
                #     # mask_paths = glob('%s/*.png' % self.mask_path)
                #     # mask_paths = np.random.choice(mask_paths, size=1)
                #     # img_mask = cv2.imread(mask_paths[0])
                #     img_mask = cv2.imread(self.mask_path)
                #     img_mask = cv2.GaussianBlur(img_mask, (self.blur_ax, self.blur_ay), 0)
                #     src = cv2.bitwise_and(src, img_mask)

                # src = (src * 0.5 + (127.5 / 2.0)).astype(np.float32)

                # 画像処理
                if self.is_smaller:
                    bg = np.zeros(src.shape, dtype=np.uint8)
                    h, w = src.shape[:2]
                    simg = cv2.resize(src, dsize=(int(w / 2), int(h / 2)))

                    edge_t = int(h / 4)
                    edge_b = int(h / 4 * 3)
                    edge_l = int(w / 4)
                    edge_r = int(w / 4 * 3)

                    bg[edge_t:edge_b, edge_l:edge_r, :] = simg[:, :, :]
                    src = bg

                cur_framerate = self.framerate

                for i in range(self.max_frame):
                    if cur_framerate != self.framerate:
                        break

                    # 初回は前フレームも同じ画像を使う
                    if self.prev_src is None:
                        self.prev_src = src

                    if img_A is None:
                        src_rgb = cv2.cvtColor(src, cv2.COLOR_BGR2RGB)
                        img_A = self.data_loader.format(src_rgb)

                    # ブレンドモードは2枚の画像をなめらかに変化させる
                    if self.is_blend:
                        weight = i / self.max_frame
                        blend_img = cv2.addWeighted(self.prev_src, 1 - weight, src, weight, 0)
                        src_rgb = cv2.cvtColor(blend_img, cv2.COLOR_BGR2RGB)
                        img_A = self.data_loader.format(src_rgb)
                        img_A = img_A.astype(np.float32)
                        fake_B = self.g_AB.predict(img_A)
                        fake_B = self.g_AB.predict(fake_B)

                    else:
                        src_rgb = cv2.cvtColor(src, cv2.COLOR_BGR2RGB)
                        img_A = img_A.astype(np.float32)
                        fake_B = self.g_AB.predict(img_A)

                    img_fake_B = np.concatenate(fake_B)
                    img_fake_B = 0.5 * img_fake_B + 0.5
                    img_fake_B = np.array(img_fake_B * 255.0, dtype=np.uint8)
                    img_fake_B = cv2.cvtColor(img_fake_B, cv2.COLOR_RGB2BGR)
                    mask_fake_B = cv2.cvtColor(img_fake_B, cv2.COLOR_RGB2GRAY)
                    mask_fake_B = cv2.threshold(mask_fake_B, 10, 255, cv2.THRESH_BINARY)[1]
                    contours, hierarchy = cv2.findContours(mask_fake_B, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

                    mask_fake_B = np.zeros(self.img_shape, dtype=np.uint8)
                    # mask_edge = np.ones(self.img_shape, dtype=np.uint8) * 255
                    for i in range(0, len(contours)):
                        if len(contours[i]) > 0:
                            if cv2.contourArea(contours[i]) < 500:
                                continue
                            cv2.drawContours(mask_fake_B, contours, i, (255,255,255), -1)
                            # cv2.drawContours(mask_edge, contours, i, (100,100,100), 10)

                    # kernel = np.ones((5, 5), np.uint8)
                    # mask_fake_B = cv2.erode(mask_fake_B, kernel, iterations=2)
                    mask_fake_B = cv2.GaussianBlur(mask_fake_B, (self.blur_ax, self.blur_ay), 0)

                    alpha = np.array(mask_fake_B / 255.0, dtype=np.float32)
                    img_fake_B = np.array(img_fake_B * alpha,  dtype=np.uint8)
                    img_fake_B = np.array(img_fake_B * alpha, dtype=np.uint8)

                    # cv2.imshow("image", img_fake_B)

                    img_fake_B = cv2.cvtColor(img_fake_B, cv2.COLOR_BGR2RGB)
                    img_fake_B = np.array(img_fake_B, dtype=np.float32)
                    fake_B = self.data_loader.format(img_fake_B)

                    self.qimg = self.convert_pyqt(origin, src_rgb, fake_B)
                    # self.show_img_portrait(fake_B)

                    # 画像を保存する
                    if dst_img_dir:
                        self.save_imgs(fake_B, dst_img_dir)
                        self.frame += 1

                    # pyqtで画像の描画イベントを送信
                    self.on_render_img.send(img=self.qimg)
                    QtTest.QTest.qWait(int(1000 / self.framerate))

                    # ブレンドモードでなければ生成画像をフィードバックループする
                    if not self.is_blend:
                        img_A = fake_B

                self.prev_src = src

            except Exception as e:
                print(traceback.format_exc())

    def convert_pyqt(self, img_h_l, img_h_c, img_h_r):
        _img_h_l = cv2.cvtColor(img_h_l, cv2.COLOR_BGR2RGB)
        _img_h_l = _img_h_l.astype(np.float32) / 255.0
        _img_h_c = img_h_c.astype(np.float32) / 255.0
        _img_h_r = np.concatenate(img_h_r)
        _img_h_r = 0.5 * _img_h_r + 0.5
        _img_h = cv2.hconcat([_img_h_l, _img_h_c, _img_h_r])
        # _img_h = cv2.cvtColor(_img_h, cv2.COLOR_BGR2RGB)
        _img_h = np.array(_img_h * 255.0, dtype=np.uint8)
        _h, _w = _img_h.shape[:2]
        return QImage(_img_h.flatten(), _w, _h, QImage.Format_RGB888)

    def load_model(self):

        def load(model, model_name):
            weights_path = 'cyclegan/models/%s_weights.hdf5' % model_name
            model.load_weights(weights_path)

        load(self.d_A, "cyclegan_d_A")
        load(self.d_B, "cyclegan_d_B")
        load(self.g_AB, "cyclegan_g_AB")
        load(self.g_BA, "cyclegan_g_BA")
        load(self.combined, "cyclegan_combined")

    def save_imgs(self, img, dst_img_dir):
        if not os.path.exists(dst_img_dir):
            os.makedirs(dst_img_dir)
            logger.debug('make dir %s' % dst_img_dir)

        # path = dst_img_dir + '/{:05d}.jpg'.format(self.frame)
        path = dst_img_dir + '/{}.jpg'.format(self.frame)

        dst = np.concatenate(img)
        dst = 0.5 * dst + 0.5
        dst = np.array(dst * 255.0, dtype=np.uint8)
        dst = cv2.cvtColor(dst, cv2.COLOR_RGB2BGR)
        # cv2.imshow("dst", dst)
        cv2.imwrite(path, dst)

    def show_img_portrait(self, img):
        src = np.concatenate(img)
        src = 0.5 * src + 0.5
        src = np.array(src * 255.0, dtype=np.uint8)
        src = cv2.cvtColor(src, cv2.COLOR_RGB2BGR)

        h = 336
        w = 168
        ch = 3

        # edge_t = int(h/4)
        # edge_b = int(h/4*3)
        # simg = cv2.resize(src, dsize=(w, w))
        # bg = np.zeros((h, w, ch), dtype=np.uint8)
        # bg[edge_t:edge_b, :, :] = simg

        edge_l = int(h / 4)
        edge_r = int(h / 4 * 3)
        img_l = cv2.resize(src, dsize=(h, h))
        bg = np.zeros((h, w, ch), dtype=np.uint8)

        bg = img_l[:, edge_l:edge_r, :]

        cv2.imshow("dst", bg)


    def changed_framerate_handler(self, framerate):
        self.framerate = framerate