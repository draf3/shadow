import cv2
import threading

class Capturer(threading.Thread):

    def __init__(self):
        super().__init__()
        self.setDaemon(True)
        self.cap = cv2.VideoCapture(0)
        self.frame = None
        self.start()

    def run(self):
        while True:
            ret, frame = self.cap.read()
            self.frame = frame
            # print(self.frame.shape)
            # cv2.imshow("img", frame)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
        # self.cap.release()

    def __del__(self):
        self.cap.release()