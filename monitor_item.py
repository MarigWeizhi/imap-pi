import json


# 定义一个MonitorItem类
class MonitorItem:
    def __init__(self, string):
        data = json.loads(string)
        self.max = data['max']
        self.min = data['min']
        self.open = data['open']
        self.type = data['type']

    @classmethod
    def from_string(cls, string):
        # 返回一个新的MonitorItem对象，传入字符串参数
        return cls(string)