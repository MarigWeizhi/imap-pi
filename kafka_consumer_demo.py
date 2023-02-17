import time
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'my_topic',
    group_id='test_id',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest'
)
for msg in consumer:
    print(msg)
    print(f"topic = {msg.topic}")  # topic default is string
    print(f"partition = {msg.partition}")
    print(f"value = {msg.value.decode()}")  # bytes to string
    print(f"timestamp = {msg.timestamp}")
    print("time = ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(msg.timestamp / 1000)))