import datetime
import socket
import threading
import time
import cv2
import base64

import requests


def frame_to_base64(frame):
    # _, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(frame)
    return jpg_as_text.decode('utf-8')

def time_to_seconds(date_string):
    date_object = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    return int(date_object.timestamp()*1000) - 8 * 60 * 60 * 1000


def timestamp():
    return int(time.time() * 1000)


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
    file_path = time.strftime("/home/pi/imap-pi/log/%y%m%d_imap_log.txt")
    f = open(file_path, mode='a+')
    print(time.strftime("[%y/%m/%d %X] "), *args)
    print(time.strftime("[%y/%m/%d %X] "), *args, file=f)
    f.close()

def send_post_request(key,string, url):
    data = {key: string}
    response = requests.post(url, data=data)
    return response.text

def send_photo_demo():
    video = cv2.VideoCapture(0)
    success, image = video.read()
    _, frame = cv2.imencode('.jpg', image)
    send_post_request('img', frame_to_base64(frame), 'http://192.168.2.2:8080/report/photo/1')

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
    # log_print("打印测试")
    # log_print("2020-1-1", "打印测试2")
    # print(time_to_seconds('2022-09-01 00:00:00'))
    send_photo_demo()
