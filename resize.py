import cv2
import numpy as np
import glob
import os
import math

imgs = []
imgs.extend(glob.glob("./nikkeiheikin/*.jpg"))
size = 256
x = 0
y = 0
count = 0
for i in imgs:
    img = cv2.imread(i, 1)
    h, w, ch = img.shape[:3]

    if w > h:
        x = math.floor((w - h) / 2)
        img = img[y:h, x:x + h]
    elif h > w:
        y = math.floor((h - w) / 2)
        img = img[y:y + w, x:w]

    # img = cv2.GaussianBlur(img, (5, 5), 0)
    img = cv2.resize(img, dsize=(size, size))
    name = os.path.join('./nikkeiheikin256/', os.path.splitext(os.path.basename(i))[0])
    name += '.jpg'
    cv2.imwrite(name, img)
    print(name)
    count += 1