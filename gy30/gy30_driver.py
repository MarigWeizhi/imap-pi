import time
import smbus


class gy30_driver():

    def __init__(self):
        self.bus = smbus.SMBus(1)
        self.addr = 0x23
        self.cmd = 0x11

    def get_brightness(self):
        data = self.bus.read_i2c_block_data(self.addr, self.cmd)
        result = int((data[1] + (256 * data[0])) / 1.2 + 0.5)
        return result


if __name__ == '__main__':
    gy30 = gy30_driver()
    while 1:
        print(gy30.get_brightness(), 'lx')
        time.sleep(1)