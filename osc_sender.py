from abc import ABCMeta, abstractmethod
from pythonosc import udp_client
import traceback
from logger import logger


class OscSenderBase(metaclass=ABCMeta):
    def __init__(self, ip, port):
        self._client = udp_client.SimpleUDPClient(ip, port)

    @abstractmethod
    def send(self, address, msg):
        pass


class OscSender(OscSenderBase):
    def __init__(self, ip, port):
        super().__init__(ip, port)

    def send(self, address, data):
        self._client.send_message(address, data)
        logger.debug(data)

if __name__ == '__main__':
    osc_sender = OscSender('127.0.0.1', 10000)
    osc_sender.send('/list', [1., 4., 'hello'])
    osc_sender.send('/str', 'world')