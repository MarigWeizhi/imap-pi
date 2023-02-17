import socket
import threading
import time


def getLocalIp():
    '''Get the local ip'''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def log_print(*args):
    file_path = time.strftime("/home/pi/iwms-server/log/%y%m%d_iwms_log.txt")
    f = open(file_path, mode='a+')
    print(time.strftime("[%y/%m/%d %X] "), *args)
    print(time.strftime("[%y/%m/%d %X] "), *args, file=f)
    f.close()


class send_driver():
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # enable broadcast
        self.server.connect((self.ip, self.port))

    def send_data(self, data):
        self.server.sendall(data.encode())


if __name__ == '__main__':
    # send = send_driver('192.168.2.3', 5052)
    # send.send_data('temp@dev1#T:28.5,H:58.6')
    log_print("打印测试")
    log_print("2020-1-1", "打印测试2")
