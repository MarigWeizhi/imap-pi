#!/user/bin/python3
import os
import board
import adafruit_shtc3
from utils import *

class shtc3_driver_new():
    def __init__(self):
        # 解除温湿传感器接口被占用
        os.system("/usr/sbin/i2cset -f -y 1 0x60 0x00 0")

        # 初始化传感器
        # i2c = busio.I2C(board.SCL, board.SDA)
        i2c = board.I2C()
        self.sht = adafruit_shtc3.SHTC3(i2c)

    def get_tmp_hmt(self):
        temperature, humidity = self.sht.measurements
        return temperature,humidity

if __name__ == '__main__':
    sht = shtc3_driver_new()
    for i in range(10):
        print(sht.get_tmp_hmt())
        time.sleep(1)