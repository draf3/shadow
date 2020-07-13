import numpy as np
import os, datetime, cv2, math, glob


def imread(filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
    try:
        n = np.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        return img
    except Exception as e:
        print(e)
        return None

def imwrite(filename, img, params=None):
    try:
        ext = os.path.splitext(filename)[1]
        result, n = cv2.imencode(ext, img, params)

        if result:
            with open(filename, mode='w+b') as f:
                n.tofile(f)
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False

def resize_square_images(input_image_dir, diameter):
    imgs = []
    types = ('*.jpg', '*.png')

    for files in types:
        image_path = os.path.join(input_image_dir, files)
        imgs.extend(glob.glob(image_path))

    x = 0
    y = 0
    for i in imgs:
        img_array = np.fromfile(i, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        h, w, ch = img.shape[:3]

        if w > h:
            x = math.floor((w - h) / 2)
            img = img[y:h, x:x + h]
        elif h > w:
            y = math.floor((h - w) / 2)
            img = img[y:y + w, x:w]

        # img = cv2.GaussianBlur(img, (5, 5), 0)
        img = cv2.resize(img, dsize=(diameter, diameter))
        filepath = os.path.join(input_image_dir, '{}.jpg'.format(os.path.splitext(os.path.basename(i))[0]))
        imwrite(filepath, img)
        print(filepath)

def make_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def save_texts(texts, filepath):
    with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:
        f.write(texts)
        f.close()

def date_str():
    return datetime.datetime.now().strftime('%Y%m%d_%H%M%S%f')

