import scipy
from glob import glob
import numpy as np
import cv2
from PIL import Image

class DataLoader():
    def __init__(self, img_res=(256, 256)):
        self.img_res = img_res

    def load_img(self, path):
        img = self.imread(path)
        img = scipy.misc.imresize(img, self.img_res)
        img = self.format(img)
        return img

    def pil2cv(self, img):
        if img.ndim == 2:
            return img
        elif img.shape[2] == 3:
            return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        elif img.shape[2] == 4:
            return cv2.cvtColor(img, cv2.COLOR_RGBA2BGRA)

    def cv2pil(self, img):
        if img.ndim == 2:
            return img
        elif img.shape[2] == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        elif img.shape[2] == 4:
            return cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)

    def format(self, img):
        _img = img / 127.5 - 1.0
        _img = _img[np.newaxis, :, :, :]
        return _img

    def imread(self, path):
        return scipy.misc.imread(path, mode='RGB').astype(np.float)
