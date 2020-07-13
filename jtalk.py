import subprocess
import winsound
import os
from logger import logger
import config
import traceback

class JTalk:
    def __init__(self, gui):
        self.gui = gui
        OPENJTALK_BINPATH = 'c:/open_jtalk/bin'
        OPENJTALK_DICPATH = 'c:/open_jtalk/dic'
        OPENJTALK_VOICEPATH = 'C:/open_jtalk/voice/m001/nitech_jp_atr503_m001.htsvoice'
        self.open_jtalk = [OPENJTALK_BINPATH + '/open_jtalk.exe']
        self.mech = ['-x', OPENJTALK_DICPATH]
        self.htsvoice = ['-m', OPENJTALK_VOICEPATH]
        self.speed = ['-r', '1']
        self.count = 0

    def say(self, sentence, output_audios_dir):
        try:

            if self.gui.is_save():
                if not os.path.exists(output_audios_dir):
                    os.makedirs(output_audios_dir)
                    self.count = 0
                    logger.debug('make dir %s' % output_audios_dir)

                name = '{}.wav'.format(self.count)
                path = os.path.join(output_audios_dir, name)
                outwav = ['-ow', path]

            else:
                path = 'talk.wav'
                outwav = ['-ow', path]

            cmd = self.open_jtalk + self.mech + self.htsvoice + self.speed + outwav
            c = subprocess.Popen(cmd, stdin=subprocess.PIPE)
            c.stdin.write(sentence.encode('shift-jis'))
            c.stdin.close()
            c.wait()

            if self.gui.is_save():
                self.count += 1
            else:
                winsound.PlaySound(path, winsound.SND_FILENAME)

        except Exception as e:
            print(traceback.format_exc())

        finally:
            pass
