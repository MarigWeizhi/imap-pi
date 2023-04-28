import json
import time
import datetime
import random

import pytz as pytz
import requests

from config import hour_ranges_tmp, hour_ranges_hmt, hour_ranges_lx
from data.kafka_producer import PyProducer
from utils import time_to_seconds

DEVICE_IDS = [5]
# DATA_REPORT_URL = 'http://192.168.2.20:8080/report/cur/'
DATA_REPORT_URL = 'http:///192.168.43.38:8080/report/cur/'
timezone = pytz.timezone("Etc/GMT-8")


# 定义随机数据生成逻辑
def random_tmp(id=1, time=1678338000000):
    date_object = datetime.datetime.fromtimestamp(time / 1000 % 946656000, tz=timezone)
    hour = date_object.hour
    temp_range = hour_ranges_tmp[hour]
    # 在温度区间内随机生成
    temp = round(random.uniform(temp_range[0], temp_range[1]), 2)
    return temp


def random_hmt(id=1, time=1678338000000):
    date_object = datetime.datetime.fromtimestamp(time / 1000 % 946656000, tz=timezone)
    hour = date_object.hour
    hmt_range = hour_ranges_hmt[hour]
    # 在温度区间内随机生成
    temp = round(random.uniform(hmt_range[0], hmt_range[1]), 2)
    return temp


def random_lx(id=1, time=1678338000000):
    date_object = datetime.datetime.fromtimestamp(time / 1000 / 946656000, tz=timezone)
    hour = date_object.hour
    lx_range = hour_ranges_lx[hour]
    # 在温度区间内随机生成
    lx = round(random.uniform(lx_range[0], lx_range[1]), 2)
    return lx


# 开始时间戳到结束时间戳，单位是秒，保证gap，保证截止到end
def data_kafka_generate(start, end, gap, prod):
    print('生成数据量：', 5 * int((end - start) / gap / 1000))
    for device_id in DEVICE_IDS:
        print('正在生成站点', device_id, '的数据')
        cur = start
        while cur < end:
            report_data = {
                "siteId": device_id,
                "timestamp": cur,
                "type": "report",
                "version": 1,
                "status": 0,
                "data": {
                    "tmp": random_tmp(device_id, cur),
                    "hmt": random_hmt(device_id, cur),
                    "lx": random_lx(device_id, cur)
                }
            }
            # print(report_data)
            prod.send_data2(report_data)
            cur += gap * 1000
    # send_flag_data()


# flag = 2 为开始标志  3为结束标志
def send_flag_data(mod=1, flag=2, prod=None):
    cur = time.time() * 1000
    report_data = {
        "siteId": 0,
        "timestamp": cur,
        "type": "report",
        "version": 1,
        "status": flag,
        "data": {
            "tmp": random_tmp(1, cur),
            "hmt": random_hmt(1, cur),
            "lx": random_lx(1, cur)
        }
    }
    if mod == 1:
        flag_data = {'report': json.dumps(report_data)}
        requests.post(DATA_REPORT_URL + str(1), data=flag_data)
    else:
        prod.send_data2(report_data)


def gen_all():
    prod = PyProducer(topic='report')
    start_datetime = '2023-02-28 00:00:00'
    end_datetime = '2023-03-10 00:00:00'
    gap = 60 * 5
    data_kafka_generate(time_to_seconds(start_datetime),
                        time_to_seconds(end_datetime),
                        gap,
                        prod)


def gen_little():
    prod = PyProducer(topic='report')
    start_datetime = '2023-04-20 00:00:00'
    end_datetime =   '2023-04-28 12:00:00'
    gap = 60 * 20
    data_kafka_generate(time_to_seconds(start_datetime),
                        time_to_seconds(end_datetime),
                        gap,
                        prod)


def loding_test(count=1000, mod=1):
    data_list = []
    for i in range(count):
        cur = time.time() * 1000
        report_data = {
            "siteId": 0,
            "timestamp": cur,
            "type": "report",
            "version": 1,
            "status": 1,
            "data": {
                "tmp": random_tmp(1, cur),
                "hmt": random_hmt(1, cur),
                "lx": random_lx(1, cur)
            }
        }
        data_list.append(report_data)
    prod = PyProducer(topic='report')
    start_time = time.time() * 1000
    print('http' if mod == 1 else 'kafka 测试')
    print('测试量：', count)
    send_flag_data(mod, 2, prod)
    for data in data_list:
        flag_data = {'report': json.dumps(data)}
        if mod == 1:
            requests.post(DATA_REPORT_URL + str(1), data=flag_data)
        else:
            prod.send_data2(data)
    send_flag_data(mod, 3, prod)
    end_time = time.time() * 1000
    print('开始时间', int(start_time))
    print('结束时间', int(end_time))
    print('花费时间：', int(end_time) - int(start_time), 'ms')


def get_yesterday():
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    yesterday_start = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
    yesterday_end = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)
    yesterday_start_str = yesterday_start.strftime('%Y-%m-%d %H:%M:%S')
    yesterday_end_str = yesterday_end.strftime('%Y-%m-%d %H:%M:%S')
    return yesterday_start_str, yesterday_end_str


def gen_yesterday():
    prod = PyProducer(topic='report')
    start_datetime, end_datetime = get_yesterday()
    print(start_datetime,end_datetime)
    gap = 60 * 5
    data_kafka_generate(time_to_seconds(start_datetime),
                        time_to_seconds(end_datetime),
                        gap,
                        prod)


if __name__ == '__main__':
    start_time = time.time() * 1000
    gen_little()

    # gen_yesterday()

    # http 负载测试
    # loding_test(10000, 1)
    # kakfa负载测试
    # loding_test(500, 2)

    # send_flag_data()
    # end_time = time.time() * 1000
    # print('开始时间', int(start_time))
    # print('结束时间', int(end_time))
    # print('花费时间：', int(end_time) - int(start_time))
