import subprocess
import winsound
from datetime import datetime
import os
from blinker import signal
from utils.logger import logger
import config
import traceback

class JTalk:
    def __init__(self):
        # depend on your install folder
        OPENJTALK_BINPATH = 'c:/open_jtalk/bin'
        OPENJTALK_DICPATH = 'c:/open_jtalk/dic'
        # OPENJTALK_VOICEPATH = 'c:/open_jtalk/bin/nitech_jp_atr503_m001.htsvoice'
        OPENJTALK_VOICEPATH = 'C:/open_jtalk/voice/m001/nitech_jp_atr503_m001.htsvoice'
        self.open_jtalk = [OPENJTALK_BINPATH + '/open_jtalk.exe']
        self.mech = ['-x', OPENJTALK_DICPATH]
        self.htsvoice = ['-m', OPENJTALK_VOICEPATH]
        self.speed = ['-r', '1']
        self.dst_audio_dir = "audio"
        self.count = 0
        self.is_save = False

    def say(self, _, sentence):
        try:
            if self.is_save:
                if not os.path.exists(self.dst_audio_dir):
                    os.makedirs(self.dst_audio_dir)
                    logger.debug('make dir %s' % self.dst_audio_dir)

                # path = self.dst_audio_dir + '/{:03d}.wav'.format(self.count)
                path = self.dst_audio_dir + '/{}.wav'.format(self.count)
                outwav = ['-ow', path]

            else:
                outwav = ['-ow', 'audio/talk.wav']

            cmd = self.open_jtalk + self.mech + self.htsvoice + self.speed + outwav
            c = subprocess.Popen(cmd, stdin=subprocess.PIPE)
            # convert text encoding from utf-8 to shitf-jis
            c.stdin.write(sentence.encode('shift-jis'))
            c.stdin.close()
            c.wait()

            if self.is_save:
                self.count += 1
            else:
                # play wav audio file with winsound module
                winsound.PlaySound('audio/talk.wav', winsound.SND_FILENAME)

        except Exception as e:
            print(traceback.format_exc())

        finally:
            on_end_jtalk = signal(config.EVENT['ON_END_JTALK'])
            on_end_jtalk.send()

    # def save(self, _, sentence):
    #     try:
    #         if not os.path.exists(self.dst_audio_dir):
    #             os.makedirs(self.dst_audio_dir)
    #             logger.debug('make dir %s' % self.dst_audio_dir)
    #
    #         # path = self.dst_audio_dir + '/{:03d}.wav'.format(self.count)
    #         path = self.dst_audio_dir + '/{}.wav'.format(self.count)
    #         outwav = ['-ow', path]
    #         cmd = self.open_jtalk + self.mech + self.htsvoice + self.speed + outwav
    #         c = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    #         # convert text encoding from utf-8 to shitf-jis
    #         c.stdin.write(sentence.encode('shift-jis'))
    #         c.stdin.close()
    #         c.wait()
    #
    #         self.count += 1
    #
    #     except Exception as e:
    #         print(traceback.format_exc())
    #
    #     finally:
    #         on_end_jtalk = signal(config.EVENT['ON_END_JTALK'])
    #         on_end_jtalk.send()
