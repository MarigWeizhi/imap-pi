from kafka import KafkaProducer
import json
from utils import *


class PyProducer():

    def __init__(self, ips=['47.116.66.37:9092', ], topic='test'):
        self.ips = ips
        self.topic = topic

        self.producer = KafkaProducer(
            bootstrap_servers=self.ips,
            max_block_ms=10000,
            max_request_size=10485760,
            send_buffer_bytes=10485760,
            value_serializer=lambda m: json.dumps(m, ensure_ascii=False).encode(),
            api_version=(0, 10)
        )

    def send_data2(self,data):
        self.producer.send(topic=self.topic, value=data)

    def send_data(self, data):
        log_print("send_data", data)
        future = self.producer.send(topic=self.topic, value=data)
        result = future.get(timeout=10)
        log_print("result", result)

if __name__ == '__main__':

    prod = PyProducer()
    for _id in range(200, 205):
        record = {"title": "今天真美丽", "_id": _id}
        prod.send_data(record)
