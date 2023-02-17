# SPDX-FileCopyrightText: Copyright (c) 2020 Bryan Siepert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
import time
import os
import busio
import board
import adafruit_shtc3

# 解除温湿度传感器被占用
os.system("i2cset -f -y 1 0x60 0x00 0")

# i2c = busio.I2C(board.SCL, board.SDA)
i2c = board.I2C()
sht = adafruit_shtc3.SHTC3(i2c)

while True:
    temperature, relative_humidity = sht.measurements
    print("Temperature: %0.1f C" % temperature)
    print("Humidity: %0.1f %%" % relative_humidity)
    print("")
    time.sleep(1)
