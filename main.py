import os

from buzzer.BuzzDriver import BuzzDriver
from data.kafka_consumer import PyConsumer
from monitor_config import MonitorConfig
from shtc3.shtc3_driver_new import shtc3_driver_new
from data.kafka_producer import PyProducer
from gy30.gy30_driver import gy30_driver
from camera import *
import threading

# REMOTE_IP = '47.116.66.37:9092'
REMOTE_IP = '47.113.150.217:9092'
LOCAL_IP = '127.0.0.1'
DEVICE_ID = 1

KAFKA_PORT = 9092

global_var = collections.Counter()


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
    def update_config(msg):
        tmp_config = MonitorConfig.from_string(msg)
        # 如果解析异常就不要这条消息
        if tmp_config and tmp_config.siteId == DEVICE_ID:
            global_var['config'] = tmp_config

    global producer
    # 生产数据
    producer = PyProducer(ips=[REMOTE_IP,],topic='report')
    # 订阅监控配置
    consumer = PyConsumer(topic='config', callback=update_config,ips=[REMOTE_IP,])
    listener_thread = threading.Thread(target=consumer.monitor_data)
    # 启动子线程
    listener_thread.start()


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
        "status": 0,
        "data": {
            "tmp": tmp,
            "hmt": hmt / 100,
            "lx": brightness
        }
    }
    return report_data


def check_data(monitor_config: MonitorConfig, report_data):
    if not monitor_config: return
    if monitor_config.isDelete: return
    if monitor_config.interval <= 0: return
    if isinstance(cur_config,int):return
    def is_normal(cur, min, max):
        return min <= cur <= max

    tmp_data = report_data['data']['tmp']
    hmt_data = report_data['data']['hmt']
    lx_data = report_data['data']['lx']
    tmp_min = monitor_config.monitor_items['tmp'].min
    tmp_max = monitor_config.monitor_items['tmp'].max
    hmt_min = monitor_config.monitor_items['hmt'].min
    hmt_max = monitor_config.monitor_items['hmt'].max
    lx_min = monitor_config.monitor_items['lx'].min
    lx_max = monitor_config.monitor_items['lx'].max

    # report_data = {
    #     "siteId": DEVICE_ID,
    #     "timestamp": timestamp(),
    #     "type": "report",
    #     "version": 1,
    #     "data": {
    #         "tmp": tmp,
    #         "hmt": hmt / 100,
    #         "lx": brightness
    #     }
    # }
    flag = False
    if monitor_config.monitor_items['tmp'].open and not is_normal(tmp_data, tmp_min, tmp_max):
        log_print('温度异常', tmp_data, '参考值:', tmp_min, '~', tmp_max)
        flag = True
    if monitor_config.monitor_items['hmt'].open and not is_normal(hmt_data, hmt_min, hmt_max):
        log_print('湿度异常', hmt_data, '参考值:', hmt_min, '~', hmt_max)
        flag = True
    if monitor_config.monitor_items['lx'].open and not is_normal(lx_data, lx_min, lx_max):
        log_print('亮度异常', lx_data, '参考值:', lx_min, '~', lx_max)
        flag = True

    if flag:  buzz.open(2)
    log_print('当前监控配置：', monitor_config.to_json())
    # log_print('当前最大温度：', monitor_config.monitor_items['tmp'].max)
    # log_print('当前监控配置版本：', monitor_config.version)
    # log_print('当前监控间隔：', monitor_config.interval)


def init_buzzer():
    global buzz
    buzz = BuzzDriver(22)
    buzz.start()


if __name__ == '__main__':
    try:
        log_print("当前工作目录", os.getcwd())
        log_print("工作目录初始化...")
        os.chdir('/home/pi/imap-pi')
        log_print("当前工作目录", os.getcwd())

        log_print("蜂鸣器初始化")
        init_buzzer()

        log_print("温湿度传感器初始化")
        init_shtc3()

        log_print("光亮度传感器初始化")
        init_gy30()

        log_print("Kafka初始化")
        init_kafka()

        # log_print("摄像头初始化")
        # 摄像头要求在主线程，有点麻烦，干脆在外部开两个进程
        # init_camara()

        log_print("开始运行")
        while True:
            try:
                # 采集数据
                cur_config: MonitorConfig = global_var['config']
                # 关闭监控
                if not cur_config or cur_config.isDelete or cur_config.interval <= 0:
                    log_print("监控配置：", (None if isinstance(cur_config,int) else cur_config.to_json()))
                    log_print("关闭监控，设备休眠")
                    time.sleep(3)
                    continue
                report_data = get_report_data()
                check_data(cur_config, report_data)
                producer.send_data(report_data)
                # 上报周期
                time.sleep(cur_config.interval)
            except Exception as e:
                log_print("异常", e)
    except Exception as e:
        log_print("程序终止", e)
