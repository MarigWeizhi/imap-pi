import threading
from shtc3_driver import shtc3_driver
from update_web import start

class tmp_hum_monitor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        #启动温湿传感器
        shtc3 = shtc3_driver()
        shtc3.start()

        # 启动web服务
        start()

if __name__ == '__main__':
    monitor = tmp_hum_monitor()
    monitor.start()