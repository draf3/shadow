from threading import Lock, Thread
from logger import logger
import json, random, datetime
import config

class Trend:
    def __init__(self,
                 id=None,
                 title='',
                 input_texts_path='',
                 input_images_dir='',
                 lstm_model_path='',
                 output_images_dir='',
                 output_audios_dir='',
                 created_at=''):

        self.id = id
        self.title = title
        self.input_texts_path = input_texts_path
        self.input_images_dir = input_images_dir
        self.lstm_model_path = lstm_model_path
        self.output_images_dir = output_images_dir
        self.output_audios_dir = output_audios_dir
        self.created_at = created_at


class TrendStoreBase(type):
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        logger.debug("TrendStoreBase call")
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class TrendStore(metaclass=TrendStoreBase):
    def __init__(self):
        self.trends = []
        self.trend_count = 0
        logger.debug("TrendStore init")

    def load(self):
        try:
            database = json.load(open(config.TREND_DATA, mode='r', encoding='utf-8'))
        except FileNotFoundError:
            logger.debug('File not found {}.'.format(config.TREND_DATA))
            database = None
        finally:
            return database

    def save(self, trend):
        database = self.load()
        if database:
            id = len(database)
        else:
            database = []
            id = 0

        database.insert(0, {
            'id': id,
            'title': trend.title,
            'input_texts_path': trend.input_texts_path,
            'input_images_dir': trend.input_images_dir,
            'lstm_model_path': trend.lstm_model_path,
            'output_images_dir': trend.output_images_dir,
            'output_audios_dir': trend.output_audios_dir,
            'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        })

        json.dump(database, open(config.TREND_DATA, mode='w', encoding='utf-8'), indent=4, ensure_ascii=False)

    def get_data(self, idx):
        database = self.load()
        if database:
            data = database[idx]
        else:
            data = ''

        return data

    def get_len(self):
        database = self.load()
        if database:
            length = len(database)
        else:
            length = 0

        return length


if __name__ == '__main__':
    trend_store = TrendStore()
    for i in range(10):
        trend = Trend()
        trend.id = trend_store.get_len()
        trend.title = 'title_{}'.format(i)
        trend.input_texts_path = 'input_texts_path_{}'.format(i)
        trend.input_images_dir = 'input_images_dir_{}'.format(i)
        trend.lstm_model_path = 'lstm_model_path_{}'.format(i)
        trend.output_images_dir = 'output_images_dir_{}'.format(i)
        trend.output_audios_dir = 'output_audios_dir_{}'.format(i)
        trend_store.save(trend)

    data = trend_store.get_data(random.randrange(trend_store.get_len()))
    logger.debug(data)

    # Singleton test
    # t0 = TrendStore()
    # t1 = TrendStore()
    # t0.trend_count = 10
    # print(t0.trend_count)
    # print(t1.trend_count)