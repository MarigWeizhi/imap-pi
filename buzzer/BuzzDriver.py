#!/usr/bin/env python
import RPi.GPIO as GPIO
import time
import threading
from utils import *

class BuzzDriver(threading.Thread):
    # 以 xxx = BuzzDriver() 创建对象
    def __init__(self, Buzzer = 22): # 默认22
        threading.Thread.__init__(self)
        CL = [0, 131, 147, 165, 175, 196, 211, 248] # 低调C          
        CM = [0, 262, 294, 330, 350, 393, 441, 495] # 中调C         
        CH = [0, 525, 589, 661, 700, 786, 882, 990] # 高调C          
        self.Buzzer = Buzzer
        self.CL = CL
        self.CM = CM
        self.CH = CH
        self.flag = False  # 初始状态 False = 关闭 True = 开启
        self.setup()

    def setup(self):
            GPIO.setmode(GPIO.BCM) # 物理编码端口
            GPIO.setup(self.Buzzer, GPIO.OUT)
            global Buzz
            Buzz = GPIO.PWM(self.Buzzer, 440)
    def loop(self):
        Buzz.ChangeFrequency(self.CH[7]) # 改音调在这里
        log_print ('\n   buzzer init...')
        while True:
            time.sleep(1)
            if self.flag:
                while True:
                    # log_print("start buzzing")
                    if not self.flag:
                        break
                    Buzz.start(50)
                    time.sleep(0.25)
                    Buzz.stop()
                    time.sleep(0.25)
            
    def destory(self):
        Buzz.stop()
        GPIO.output(self.Buzzer, 1)
        GPIO.cleanup()
    def run(self):
        self.loop()                          
if __name__ == '__main__':
    buzz = BuzzDriver(22)
    buzz.start()
    while True:
        if input() == '1':
            buzz.flag = True
        else:
            buzz.flag = False