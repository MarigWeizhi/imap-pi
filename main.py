import os
from shtc3.shtc3_driver_new import shtc3_driver_new
from utils import *
from kafka_demo import kafka_producer
from gy30.gy30_driver import gy30_driver
from camera import *
import threading
from kafka import KafkaProducer
import json

REMOTE_IP = '47.116.66.37'
LOCAL_IP = '127.0.0.1'
DEVICE_ID = 1

KAFKA_PORT = 9092


# 温湿度模块初始化
def init_shtc3():
    global shtc
    shtc = shtc3_driver_new()


# 光亮度模块初始化
def init_gy30():
    global gy30
    gy30 = gy30_driver()


# kafka模块初始化
def init_kafka():
    global test_producer
    test_producer = kafka_producer(['47.116.66.37:9092'], 'test')


# target=app.run,kwargs={'host':'0.0.0.0', 'debug'=True, 'threaded'=True}
def init_camara():
    camara_args = {
        'host': '0.0.0.0',
        'debug': True,
        'threaded': True}
    thread = threading.Thread(target=app.run, kwargs=camara_args)
    thread.start()

# 封装上报数据
def get_report_data():
    tmp, hmt = shtc.get_tmp_hmt()
    brightness = gy30.get_brightness()

    report_data = {
        "siteId": DEVICE_ID,
        "timestamp": timestamp(),
        "type": "report",
        "version": 1,
        "data": {
            "tmp": tmp,
            "hmt": hmt / 100,
            "lx": brightness
        }
    }
    return report_data


if __name__ == '__main__':
    try:
        log_print("当前工作目录", os.getcwd())
        log_print("工作目录初始化...")
        os.chdir('/home/pi/imap-pi')
        log_print("当前工作目录", os.getcwd())

        log_print("温湿度传感器初始化")
        init_shtc3()

        log_print("光亮度传感器初始化")
        init_gy30()

        log_print("Kafka初始化")
        init_kafka()

        # log_print("摄像头初始化")
        # init_camara()

        log_print("开始运行")
        while True:
            try:
                # 采集数据
                report_data = get_report_data()
                test_producer.send_data(report_data)
                time.sleep(1)
            except Exception as e:
                log_print("异常", e)
    except Exception as e:
        log_print("程序终止", e)
