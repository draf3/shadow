import os, datetime, logging
import tensorflow as tf

# Path
ROOT = os.getcwd()
DATA_DIR = os.path.join(ROOT, 'data')
INPUT_TEXT_DIR = os.path.join(DATA_DIR, 'input_texts')
INPUT_IMAGE_DIR = os.path.join(DATA_DIR, 'input_images')
LSTM_MODEL_DIR = os.path.join(DATA_DIR, 'lstm_models')
OUTPUT_IMAGE_DIR = os.path.join(DATA_DIR, 'output_images')
OUTPUT_AUDIO_DIR = os.path.join(DATA_DIR, 'output_audios')
TREND_DATA = os.path.join(DATA_DIR, 'trend.json')

# NetWork
IP = '127.0.0.1'
PORT = 10000
OUTPUT_IMAGES_ADDR = '/output_images_dir'
OUTPUT_AUDIOS_ADDR = '/output_audios_dir'

# Logger
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

LOG_DIR = os.path.join(ROOT, 'log')
LOG_FILE = os.path.join(LOG_DIR, 'output_%s.log' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
is_save_log = False
logging_level = LOGGING_LEVEL['DEBUG']
logger_mode = LOGGER_MODE['ALL']