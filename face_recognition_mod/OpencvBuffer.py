import cv2
import time
import threading
from util import *

# 让opencv实时的从摄像头读取数据，不实时的原因是opencv自带缓冲区，
# 而且缓冲区的刷新时间是不可预知的，当算法运行跟不上摄像头的帧率时，
# opencv会返回旧的帧，导致不是实时

class OpencvBuffer:
    def __init__(self, cap, ring_size=5):
        self.items = [0 for i in range(ring_size)]
        self.ring_size = ring_size  # 缓冲大小
        self.pos = 0  # 当前最新数据的位置
        self.ready = 0  # 第一帧是否完成
        self.lock = threading.RLock()  # 锁
        self.cap = cap  # cv2.VideoCapture(0)对象
        self.thread = threading.Thread(target=self.run)  # 控制线程
        self.stopflag = 0  # 安全停止线程

    def startcap(self):  # 开启捕捉
        self.stopflag = 0
        self.thread.start()

    def stopcap(self):  # 停止捕捉
        self.stopflag = 1

    def run(self):  # 线程
        while (self.stopflag == 0):
            ret, img = self.cap.read()
            if (ret):
                self.push(img)
            else:
                log_print("请检查摄像头\n")
                time.sleep(0.5)

    def push(self, img):
        self.lock.acquire()
        self.pos = self.pos + 1
        if (self.pos > self.ring_size - 1):  # 循环放置
            self.pos = 0
        self.items[self.pos] = img
        self.ready = 1
        self.lock.release()
        # log_print("push")

    def getnew(self):  # 返回格式和cap.read()一致
        ret = 1
        if (self.ready == 0):
            ret = 0
            return ret,None,None,None
        self.lock.acquire()
        img = self.items[self.pos]
        small_img = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
        rgb_small_img = small_img[:, :, ::-1]
        self.lock.release()
        return ret, img, small_img,rgb_small_img
