#!/user/bin/python3
import datetime
import json
import os
import time
# import busio
import board
import adafruit_shtc3
import threading
import socket
from buzzer.BuzzDriver import *
from utils import *
import requests


DATA_REPORT_URL = 'http://47.116.66.37:9000/api/dataReport'

class shtc3_driver(threading.Thread):

    def __init__(self, remote_ip='192.168.2.3', remote_port=5050, min_tmp=-10, max_tmp=38, min_hmt=20, max_hmt=80):
        threading.Thread.__init__(self)
        self.android_ip = None
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.min_tmp = min_tmp
        self.max_tmp = max_tmp
        self.min_hmt = min_hmt
        self.max_hmt = max_hmt
        self.is_warning = False
        self.is_stop = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 解除温湿传感器接口被占用
        os.system("i2cset -f -y 1 0x60 0x00 0")

        # 初始化传感器
        # i2c = busio.I2C(board.SCL, board.SDA)
        i2c = board.I2C()
        self.sht = adafruit_shtc3.SHTC3(i2c)

        # 更新时间
        # os.system("sudo ntpdate cn.pool.ntp.org")

        # 蜂鸣器控制
        self.buzz = BuzzDriver()
        self.buzz.start()

    # 检查数据是否超出阈值
    def data_check(self):
        if not self.is_warning and (self.cur_tmp > self.max_tmp or self.cur_tmp < self.min_tmp or \
                                    self.cur_hmt > self.max_hmt or self.cur_hmt < self.min_hmt):
            self.is_warning = True
            log_print('启动警报', '温度：', self.cur_tmp, "湿度：", self.cur_hmt)
            self.buzz.flag = True

        if self.is_warning and (self.min_tmp < self.cur_tmp < self.max_tmp and
                                self.min_hmt < self.cur_hmt < self.max_hmt):
            self.is_warning = False
            log_print('关闭警报')
            self.buzz.flag = False

    # 更新当前时刻温湿度
    def dataJsonWrite(self, dataset):
        # 保存至本地
        # file = open("shtc3/data/data.json", "w")
        # file.write("[")
        # json.dump(dataset, file)
        # file.write("]")
        # file.close()

        # {"devCode": "IWMS_DEV_001", "tmp": "19.2", "hmt": "55.2"}
        req_data = {
            "devCode": "IWMS_DEV_001",
            "tmp": "%.1f" % dataset["tmp"],
            "hmt": "%.1f" % dataset["hmt"],
        }
        android_data = "temp@cam1#T:%.1f,H:%.1f" % (float(dataset["tmp"]), float(dataset['hmt']))

        # UDP发送数据给服务器(旧)
        # self.sock.sendto(bytes(data.encode('utf-8')), (self.remote_ip, self.remote_port))

        # 数据上报（新）
        # data_json = json.dumps(req_data)
        response = requests.post(DATA_REPORT_URL, req_data)
        # print(response.text)
        try:
            # UDP发送数据给安卓
            if self.android_ip:
                self.sock.sendto(bytes(android_data.encode('utf-8')), (self.android_ip, 5052))

            response = json.loads(response.text)
            self.min_tmp = response['minT']
            self.min_hmt = response['minH']
            self.max_tmp = response['maxT']
            self.max_hmt = response['maxH']
        except:
            print("数据上报返回值，异常")
            print(response)
            print(type(response))



    # 更新时间段平均温湿度
    def rangeJsonWrite(self, dataset, range):
        # range = 1 每小时数据
        # range = 0 每五分钟数据
        if range:
            log_print('一小时平均数据更新', dataset)
            file = open("shtc3/data/halfDay.json", "a+")
        else:
            log_print('五分钟平均数据更新', dataset)
            file = open("shtc3/data/hour.json", "a+")
        file.seek(0, 0)
        DataList = json.load(file)
        del DataList[0]
        DataList.append(dataset)
        file.seek(0, 0)
        file.truncate()
        json.dump(DataList, file)
        file.close()

        if range:
            # 60分钟平均数据
            data = "60temp@%s" % str(dataset)
            self.sock.sendto(bytes(data.encode('utf-8')), (self.remote_ip, self.remote_port))
        else:
            # 5分钟平均数据
            data = "5temp@%s" % str(dataset)
            self.sock.sendto(bytes(data.encode('utf-8')), (self.remote_ip, self.remote_port))

    def run(self):

        while not self.is_stop:
            min_p = time.time()
            hour_p = time.time()

            sum_5min = {"tmp": 0, "hmt": 0}
            sum_1h = {"tmp": 0, "hmt": 0}
            try:
                temperature, humidity = self.sht.measurements
                data = {"tmp": temperature, "hmt": humidity}

                log_print('温湿度数据开始更新', data)
                self.rangeJsonWrite(data, 0)
                self.rangeJsonWrite(data, 1)
                while not self.is_stop:
                    temperature, humidity = self.sht.measurements

                    # 防止未获取到数据
                    # temperature = temperature if not temperature else 28
                    # humidity = humidity if not humidity else 50

                    # 温湿度监控
                    self.cur_tmp = temperature
                    self.cur_hmt = humidity

                    self.data_check()
                    data = {"tmp": temperature, "hmt": humidity}
                    sum_5min['tmp'] += data['tmp']
                    sum_5min['hmt'] += data['hmt']
                    sum_1h['tmp'] += data['tmp']
                    sum_1h['hmt'] += data['hmt']

                    self.dataJsonWrite(data)
                    min_l = time.time()
                    if min_l - min_p >= 300:
                        sum_5min['tmp'] = '%.2f' % (float(sum_5min['tmp']) / 300)
                        sum_5min['hmt'] = '%.2f' % (float(sum_5min['hmt']) / 300)
                        self.rangeJsonWrite(sum_5min, 0)

                        # log_print('近5分钟温湿度', sum_5min)
                        # 5分钟计时刷新
                        min_p = time.time()
                        hour_l = time.time()
                        sum_5min = {"tmp": 0, "hmt": 0}

                        if hour_l - hour_p >= 3600:
                            sum_1h['tmp'] = '%.2f' % (float(sum_1h['tmp']) / 3600)
                            sum_1h['hmt'] = '%.2f' % (float(sum_1h['hmt']) / 3600)

                            self.rangeJsonWrite(sum_1h, 1)
                            # 1小时计时刷新
                            hour_p = time.time()
                            sum_1h = {"tmp": 0, "hmt": 0}

                    # 数据1秒写入一次
                    time.sleep(1)
            except KeyboardInterrupt as ke:
                log_print(ke)
            except Exception as e:
                log_print(e)

            log_print("服务10秒后重启")
            time.sleep(10)


if __name__ == "__main__":
    shtc3 = shtc3_driver()
    shtc3.start()
