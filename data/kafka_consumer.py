import json
import time
from kafka import KafkaConsumer, KafkaProducer

class PyConsumer(KafkaConsumer):
    def __init__(self, topic, callback=None, ips=['47.116.66.37:9092']):
        super().__init__(topic,
                         bootstrap_servers=ips,
                         auto_offset_reset='earliest')
        self.callback = callback if callback else self.print_data

    def print_data(self, message):
        print("time = ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(message.timestamp / 1000)))
        print("msg = ", str(message.value, encoding='utf-8'))

    def monitor_data(self):
        for message in super().__iter__():
            self.callback(message.value)


if __name__ == '__main__':
    consumer = PyConsumer(topic='config')
    # 调用监控数据的方法
    consumer.monitor_data()
    print("影响后续进行")
