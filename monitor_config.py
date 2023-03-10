import json
from monitor_item import MonitorItem
from utils import log_print


class MonitorConfig:
    def __init__(self, string):
        self.json_str = string
        data = json.loads(string)
        # 将字典中的键值对赋值给类的属性
        self.interval = data['interval']
        self.isDelete = data['isDelete']
        self.siteId = data['siteId']
        self.timestamp = data['timestamp']
        self.version = data['version']

        # data = json.loads()
        self.monitor_items = {}
        # 遍历data中的键值对
        for key, value in data['monitorItems'].items():
            value_string = json.dumps(value)
            # 调用MonitorItem类的from_string方法，创建一个MonitorItem对象
            monitor_item = MonitorItem.from_string(value_string)
            self.monitor_items[key] = monitor_item

    @classmethod
    # 返回一个新的MonitorConfig对象，传入字符串参数
    def from_string(cls, string):
        try:
            new_config = cls(string)
        except Exception as e:
            log_print('解析异常', string, e)
            return None
        return new_config

    def to_json(self):
        return self.json_str


if __name__ == '__main__':

    string = '''
 {"interval": 10, "isDelete": 0, "monitorItems": {"tmp": {"max": 26.99, "min": 0.0, "open": 1, "type": "tmp"},"lx": {"max": 1923.49, "min": 0.0, "open": 1, "type": "lx"},"hmt": {"max": 0.65, "min": 0.0, "open": 1, "type": "hmt"}},"siteId": 1, "timestamp": 1678364424029, "version": 1}
    '''
    monitor_config = MonitorConfig(string)
    print(monitor_config.to_json())
