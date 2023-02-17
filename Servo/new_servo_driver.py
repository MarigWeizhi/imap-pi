#!/usr/bin/python

import time
import math
import smbus
import os
import threading
from util import *

# ============================================================================
# Raspi PCA9685 16-Channel PWM Servo Driver
# ============================================================================

class PCA9685:
    # Registers/etc.
    __MODE1 = 0x00
    __MODE2 = 0x01
    __SUBADR1 = 0x02
    __SUBADR2 = 0x03
    __SUBADR3 = 0x04
    __MODE1 = 0x00
    __PRESCALE = 0xFE
    __LED0_ON_L = 0x06
    __LED0_ON_H = 0x07
    __LED0_OFF_L = 0x08
    __LED0_OFF_H = 0x09
    __ALLLED_ON_L = 0xFA
    __ALLLED_ON_H = 0xFB
    __ALLLED_OFF_L = 0xFC
    __ALLLED_OFF_H = 0xFD

    # Bits
    __RESTART = 0x80
    __SLEEP = 0x10
    __ALLCALL = 0x01
    __INVRT = 0x10
    __OUTDRV = 0x04

    def __init__(self, address=0x60, debug=False):
        self.bus = smbus.SMBus(1)
        self.address = address
        self.debug = debug
        if (self.debug):
            log_print("Reseting PCA9685")
        self.write(self.__MODE1, 0x00)

    def write(self, reg, value):
        "Writes an 8-bit value to the specified register/address"
        self.bus.write_byte_data(self.address, reg, value)
        if (self.debug):
            log_print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))

    def read(self, reg):
        "Read an unsigned byte from the I2C device"
        result = self.bus.read_byte_data(self.address, reg)
        if (self.debug):
            log_print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
        return result

    def setPWMFreq(self, freq):
        "Sets the PWM frequency"
        prescaleval = 25000000.0  # 25MHz
        prescaleval /= 4096.0  # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        if (self.debug):
            log_print("Setting PWM frequency to %d Hz" % freq)
            log_print("Estimated pre-scale: %d" % prescaleval)
        prescale = math.floor(prescaleval + 0.5)
        if (self.debug):
            log_print("Final pre-scale: %d" % prescale)

        oldmode = self.read(self.__MODE1);
        newmode = (oldmode & 0x7F) | 0x10  # sleep
        self.write(self.__MODE1, newmode)  # go to sleep
        self.write(self.__PRESCALE, int(math.floor(prescale)))
        self.write(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.write(self.__MODE1, oldmode | 0x80)

    def setPWM(self, channel, on, off):
        "Sets a single PWM channel"
        self.write(self.__LED0_ON_L + 4 * channel, on & 0xFF)
        self.write(self.__LED0_ON_H + 4 * channel, on >> 8)
        self.write(self.__LED0_OFF_L + 4 * channel, int(off) & 0xFF)
        self.write(self.__LED0_OFF_H + 4 * channel, int(off) >> 8)
        if (self.debug):
            log_print("channel: %d  LED_ON: %d LED_OFF: %d" % (channel, on, off))

    def setServoPulse(self, channel, pulse):
        "Sets the Servo Pulse,The PWM frequency must be 50HZ"
        pulse = pulse * 4096 / 20000  # PWM frequency is 50HZ,the period is 20000us
        self.setPWM(channel, 0, pulse)

    def stop(self, channel):
        # 0x08 0x09 is channel 0
        # 0x0c 0x0d is channel 1
        os.system("i2cset -f -y 1 0x60 0x0{} 0".format(self.__LED0_OFF_L + 4 * channel))
        os.system("i2cset -f -y 1 0x60 0x0{} 0".format(self.__LED0_OFF_H + 4 * channel))


class servo_driver:

    def __init__(self, channel=0, debug=False):
        self.channel = channel
        self.angle = 180

        pwm = PCA9685(0x60, debug)
        self.pwm = pwm
        pwm.setPWMFreq(50)
        pwm.setServoPulse(self.channel, 1500)

    def setAngle(self, angle=-1):
        angle = self.angle if angle == -1 else angle
        self.pwm.setServoPulse(self.channel, angle / (360) * (2500 - 500) + 500)

    def stop(self):
        self.pwm.stop(self.channel)


class servo_opt(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.servo_x = servo_driver(0)
        self.servo_y = servo_driver(1)
        self.isClose = False
        self.cameraActionState = "Stop"

    def run(self):
        try:
            while not self.isClose:
                # time.sleep(0.001)
                self.cameraAction()
        except Exception as e:
            log_print("舵机", e)
            self.stop()

    # 相机操作
    def cameraAction(self):
        command = self.cameraActionState

        if command == 'Stop':
            return

        if command == 'CamLeft' and self.servo_x.angle > 340:
            log_print("左转转到极限了" + str(int(self.servo_x.angle)) + "度")
            return
        elif command == 'CamRight' and self.servo_x.angle < 100:
            log_print("右转转到极限了" + str(int(self.servo_x.angle)) + "度")
            return
        elif command == 'CamUp' and self.servo_y.angle > 280:
            log_print("上转转到极限了" + str(int(self.servo_y.angle)) + "度")
            return
        elif command == 'CamDown' and self.servo_y.angle < 5:
            log_print("下转转到极限了" + str(int(self.servo_y.angle)) + "度")
            return

        gap_angle = 0.3

        if command == 'CamUp':
            self.servo_y.angle += gap_angle
            self.servo_y.setAngle()
            log_print("垂直方向" + str(int(self.servo_y.angle)) + "度")

        elif command == 'CamDown':
            self.servo_y.angle -= gap_angle
            self.servo_y.setAngle()
            log_print("垂直方向" + str(int(self.servo_y.angle)) + "度")

        elif command == 'CamLeft':
            self.servo_x.angle += gap_angle
            self.servo_x.setAngle()
            log_print("水平方向" + str(int(self.servo_x.angle)) + "度")

        elif command == 'CamRight':
            self.servo_x.angle -= gap_angle
            self.servo_x.setAngle()
            log_print("水平方向" + str(int(self.servo_x.angle)) + "度")

    def reset(self):
        self.servo_x.angle = 210
        self.servo_x.setAngle()
        log_print("水平重置" + str(int(self.servo_x.angle)) + "度")
        self.servo_y.angle = 180
        self.servo_y.setAngle()
        log_print("垂直重置" + str(int(self.servo_y.angle)) + "度")

    def stop(self):
        self.servo_x.stop()
        self.servo_y.stop()


if __name__ == '__main__':
    # pwm = PCA9685(0x60, debug=True)
    # count = 0
    # channel = 0
    # while True:
    #     # setServoPulse(2,2500)
    #     count += 1
    #     if (count == 2):
    #         break
    #     for i in range(500, 2500, 10):
    #         pwm.setServoPulse(channel, i)
    #         time.sleep(0.02)
    #
    #     for i in range(2500, 500, -10):
    #         pwm.setServoPulse(channel, i)
    #         time.sleep(0.02)
    #     pwm.stop(channel)
    servo_x = servo_driver(0)
    servo_y = servo_driver(1)

    for i in range(360):
        servo_x.setAngle(i)
