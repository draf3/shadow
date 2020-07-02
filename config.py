import os, datetime, logging


ROOT = os.getcwd()

LOGGING_LEVEL = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

LOGGER_MODE = {
    'MSG': '[%(levelname)s][%(asctime)s] %(message)s',
    'MODULE': '[%(levelname)s][%(asctime)s][%(module)s:%(lineno)s:%(funcName)s] %(message)s',
    'FILEPATH': '[%(levelname)s][%(asctime)s][%(pathname)s:%(lineno)s:%(funcName)s] %(message)s',
    'THREAD_PROCESS': '[%(levelname)s][%(asctime)s][%(threadName)s][%(processName)s] %(message)s',
    'ALL': '[%(levelname)s][%(asctime)s][%(threadName)s][%(processName)s][%(pathname)s:%(lineno)s:%(funcName)s] %(message)s'
}

# Setting Trend
TREND = {
    'COVID': {
        'NAME': 'コロナ感染者数',
        'LSTM_MODEL_PATH': os.path.join(ROOT, 'lstm/models/covid_weights.h5'),
        'LSTM_TXT_PATH': os.path.join(ROOT, 'lstm/data/covid.txt'),
        'CYCLEGAN_IMG_DIR': os.path.join(ROOT, 'cyclegan/trend_images/covid256'),
        'DST_IMG_DIR': os.path.join(ROOT, 'dst/covid/images'),
        'DST_AUDIO_DIR': os.path.join(ROOT, 'dst/covid/audio'),
    },
    'JOHNSON': {
        'NAME': 'ジョンソン首相',
        'LSTM_MODEL_PATH': os.path.join(ROOT, 'lstm/models/johnson_weights.h5'),
        'LSTM_TXT_PATH': os.path.join(ROOT, 'lstm/data/johnson.txt'),
        'CYCLEGAN_IMG_DIR': os.path.join(ROOT, 'cyclegan/trend_images/johnson256'),
        'DST_IMG_DIR': os.path.join(ROOT, 'dst/johnson/images'),
        'DST_AUDIO_DIR': os.path.join(ROOT, 'dst/johnson/audio'),
    },
    'JR': {
        'NAME': 'JR東日本',
        'LSTM_MODEL_PATH': os.path.join(ROOT, 'lstm/models/jr_weights.h5'),
        'LSTM_TXT_PATH': os.path.join(ROOT, 'lstm/data/jr.txt'),
        'CYCLEGAN_IMG_DIR': os.path.join(ROOT, 'cyclegan/trend_images/jr256'),
        'DST_IMG_DIR': os.path.join(ROOT, 'dst/jr/images'),
        'DST_AUDIO_DIR': os.path.join(ROOT, 'dst/jr/audio'),
    },
    'EARTHQUAKE': {
        'NAME': '地震',
        'LSTM_MODEL_PATH': os.path.join(ROOT, 'lstm/models/earthquake_weights.h5'),
        'LSTM_TXT_PATH': os.path.join(ROOT, 'lstm/data/earthquake.txt'),
        'CYCLEGAN_IMG_DIR': os.path.join(ROOT, 'cyclegan/trend_images/earthquake256'),
        'DST_IMG_DIR': os.path.join(ROOT, 'dst/earthquake/images'),
        'DST_AUDIO_DIR': os.path.join(ROOT, 'dst/earthquake/audio'),
    },
    'KIMETSU': {
        'NAME': '鬼滅の刃',
        'LSTM_MODEL_PATH': os.path.join(ROOT, 'lstm/models/kimetsu_weights.h5'),
        'LSTM_TXT_PATH': os.path.join(ROOT, 'lstm/data/kimetsu.txt'),
        'CYCLEGAN_IMG_DIR': os.path.join(ROOT, 'cyclegan/trend_images/kimetsu256'),
        'DST_IMG_DIR': os.path.join(ROOT, 'dst/kimetsu/images'),
        'DST_AUDIO_DIR': os.path.join(ROOT, 'dst/kimetsu/audio'),
    },
    'NIKKEIHEIKIN': {
        'NAME': '日経平均',
        'LSTM_MODEL_PATH': os.path.join(ROOT, 'lstm/models/nikkeiheikin_weights.h5'),
        'LSTM_TXT_PATH': os.path.join(ROOT, 'lstm/data/nikkeiheikin.txt'),
        'CYCLEGAN_IMG_DIR': os.path.join(ROOT, 'cyclegan/trend_images/nikkeiheikin256'),
        'DST_IMG_DIR': os.path.join(ROOT, 'dst/nikkeiheikin/images'),
        'DST_AUDIO_DIR': os.path.join(ROOT, 'dst/nikkeiheikin/audio'),
    },
    'NODAYOJIRO': {
        'NAME': '野田洋次郎',
        'LSTM_MODEL_PATH': os.path.join(ROOT, 'lstm/models/nodayojiro_weights.h5'),
        'LSTM_TXT_PATH': os.path.join(ROOT, 'lstm/data/nodayojiro.txt'),
        'CYCLEGAN_IMG_DIR': os.path.join(ROOT, 'cyclegan/trend_images/nodayojiro256'),
        'DST_IMG_DIR': os.path.join(ROOT, 'dst/nodayojiro/images'),
        'DST_AUDIO_DIR': os.path.join(ROOT, 'dst/nodayojiro/audio'),
    },
    'TERADASHIN': {
        'NAME': '寺田心',
        'LSTM_MODEL_PATH': os.path.join(ROOT, 'lstm/models/teradashin_weights.h5'),
        'LSTM_TXT_PATH': os.path.join(ROOT, 'lstm/data/teradashin.txt'),
        'CYCLEGAN_IMG_DIR': os.path.join(ROOT, 'cyclegan/trend_images/teradashin256'),
        'DST_IMG_DIR': os.path.join(ROOT, 'dst/teradashin/images'),
        'DST_AUDIO_DIR': os.path.join(ROOT, 'dst/teradashin/audio'),
    }
}

LOG_DIR = os.path.join(ROOT, 'log')
LOG_FILE = os.path.join(LOG_DIR, 'output_%s.log' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
is_save_log = False
logging_level = LOGGING_LEVEL['DEBUG']
logger_mode = LOGGER_MODE['ALL']