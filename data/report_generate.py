import json
import time
from datetime import datetime
import random

import pytz as pytz

from config import month_ranges, hour_ranges_tmp, hour_ranges_hmt, hour_ranges_lx
from kafka_producer import PyProducer
from utils import time_to_seconds

DEVICE_IDS = [1, 2, 3, 4, 5]
timezone = pytz.timezone("Etc/GMT-8")


# 定义随机数据生成逻辑
def random_tmp(id=1, time=1678338000000):
    date_object = datetime.fromtimestamp(time/1000%946656000, tz=timezone)
    hour = date_object.hour
    temp_range = hour_ranges_tmp[hour]
    # 在温度区间内随机生成
    temp = round(random.uniform(temp_range[0], temp_range[1]), 2)
    return temp


def random_hmt(id=1, time=1678338000000):
    date_object = datetime.fromtimestamp(time/1000%946656000, tz=timezone)
    hour = date_object.hour
    hmt_range = hour_ranges_hmt[hour]
    # 在温度区间内随机生成
    temp = round(random.uniform(hmt_range[0], hmt_range[1]), 2)
    return temp


def random_lx(id=1, time=1678338000000):
    date_object = datetime.fromtimestamp(time/1000/946656000, tz=timezone)
    hour = date_object.hour
    lx_range = hour_ranges_lx[hour]
    # 在温度区间内随机生成
    lx = round(random.uniform(lx_range[0], lx_range[1]), 2)
    return lx


# 开始时间戳到结束时间戳，单位是秒，保证gap，保证截止到end
def data_generate(start, end, gap, prod):
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
            prod.send_data2(report_data)
            cur += gap*1000


def gen_all():
    prod = PyProducer(topic='report')
    start_datetime = '2023-02-28 00:00:00'
    end_datetime = '2023-03-10 00:00:00'
    gap = 60 * 5
    data_generate(time_to_seconds(start_datetime),
                  time_to_seconds(end_datetime),
                  gap,
                  prod)


def gen_little():
    prod = PyProducer(topic='report')
    start_datetime = '2023-02-28 00:00:00'
    end_datetime = '2023-03-10 00:00:00'
    gap = 60 * 5
    data_generate(time_to_seconds(start_datetime),
                  time_to_seconds(end_datetime),
                  gap,
                  prod)


if __name__ == '__main__':
    start_time = time.time()
    gen_little()
    print('花费时间：', time.time() - start_time)
