#!/usr/bin/python
# coding = utf-8
import base64
import socket
import struct
from io import BytesIO

import face_recognition
import cv2
import numpy as np
import os
import threading
from face_recognition_mod.OpencvBuffer import *
from util import *

SHORT_GAP = 1
LONG_GAP = 15


class recognition(threading.Thread):

    def __init__(self, servo1, servo2, face_arr=[{"name": "kjy", "data": "base64_npy"}],
                 ip='255.255.255.255', port=5051, ):
        threading.Thread.__init__(self)
        self.servo_x = servo1
        self.servo_y = servo2

        self.face_arr = face_arr
        self.is_auto = True
        self.ip = ip
        self.port = port
        self.reco_gap = SHORT_GAP

        self.video_capture = OpencvBuffer(cap=cv2.VideoCapture(0))
        # self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        # self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # enable broadcast
        self.server.connect((self.ip, self.port))

        self.known_face_encodings = []
        self.known_face_names = []

        for face_dir in self.face_arr:
            # 读取base64编码，恢复数组
            b64_decode = base64.b64decode(face_dir['face_code'])
            curData = np.loadtxt(BytesIO(b64_decode), dtype=bytes)
            curData = [float(x.decode()) for x in curData]
            self.known_face_encodings.append(curData)
            self.known_face_names.append(str(face_dir['name']))

    def send_frame(self, frame):
        try:
            if not self.is_auto:
                # new_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
                result, imgencode = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 25])
                self.server.sendto(imgencode, (self.ip, self.port))
        except Exception as e:
            self.server.sendto(struct.pack('b', 1), (self.ip, self.port))
            log_print('视频流异常', e)
            self.video_capture.stopcap()
            self.server.close()

    # 启动视频流
    def start_frames(self, ip):
        self.ip = ip
        self.is_auto = False
        self.reco_gap = LONG_GAP
        log_print("开启视频流")

    # 关闭视频流
    def stop_frames(self):
        self.is_auto = True
        self.reco_gap = SHORT_GAP
        log_print("关闭视频流")

    def run(self):
        x_servo = 210
        y_servo = 180

        log_print(self.known_face_encodings)
        log_print(self.known_face_names)
        face_locations = []
        face_names = []
        process_this_frame = 0
        self.video_capture.startcap()
        while True:
            ret, frame, small_frame, rgb_small_frame = self.video_capture.getnew()
            if not ret:
                continue

            # Only process every other frame of video to save time

            if process_this_frame >= self.reco_gap :
                face_locations = face_recognition.face_locations(rgb_small_frame)
                if face_locations:
                    x = (face_locations[0][1] + face_locations[0][3]) / 2
                    y = (face_locations[0][0] + face_locations[0][2]) / 2
                    log_print(x, y)  # 输出脸中心到右上顶点的水平和垂直距离
                else:
                    x, y = 80, 60  # 如果没有脸则让舵机保持不动，相当于脸在中央（这时的分辨率为160*120）
                    # 计算出舵机应该移动的角度，正负与舵机的安装方式有关
                dx = (80 - x) * 0.3125
                dy = (60 - y) * 0.3125

                if self.is_auto and abs(dx) >= 0.4:  # 设置一个阈值，当角度大于3时，才移动，避免舵机一直在原地抖动，下同
                    x_servo += dx
                    if x_servo > 340:  # 设置界限，超出范围不再转动，下同
                        x_servo = 340
                    elif x_servo < 100:
                        x_servo = 100
                    self.servo_x.setAngle(x_servo)  # 水平方向的舵机控制

                if self.is_auto and abs(dy) >= 0.9:  # 设置阈值
                    y_servo += dy
                    if y_servo > 280:
                        y_servo = 280
                    elif y_servo < 5:
                        y_servo = 5
                    self.servo_y.setAngle(y_servo)  # 垂直方向的舵机控制

                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                face_names = []
                for face_encoding in face_encodings:
                    # 匹配人脸
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    name = "Unknown"
                    # # If a match was found in known_face_encodings, just use the first one.
                    # if True in matches:
                    #     first_match_index = matches.index(True)
                    #     name = known_face_names[first_match_index]
                    # Or instead, use the known face with the smallest distance to the new face
                    face_distances = face_recognition.face_distance(self.known_face_encodings,
                                                                    face_encoding)  # 计算未知面孔与所有已知面孔的特征距离
                    best_match_index = np.argmin(face_distances)  # 给出distance最小的下标
                    if matches[best_match_index]:  # 若在matches列表中存在
                        name = self.known_face_names[best_match_index]

                    face_names.append(name)
                process_this_frame = 0
            # process_this_frame = not process_this_frame
            process_this_frame += 1

            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # 还原人脸位置
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
                log_print("识别成功", name)
            # 发送照片数据
            self.send_frame(frame)
            # cv2.imshow('Video', frame)

            # 'q'键退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                os.system("i2cset -f -y 1 0x60 0x08 0")
                os.system("i2cset -f -y 1 0x60 0x09 0")
                os.system("i2cset -f -y 1 0x60 0x0c 0")
                os.system("i2cset -f -y 1 0x60 0x0d 0")
                break

        self.video_capture.stopcap()
        cv2.destroyAllWindows()
        log_print("监控结束")

    def main_process(self):
        pass
        # 启动人脸识线程
        # threading.Thread(target=self.face_recognition).start()
        # 启动发送视频流线程
        # threading.Thread(target=self.send_frame).start()

