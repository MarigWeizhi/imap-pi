#!/usr/bin/python
# -*- coding: utf-8 -*-
from util import *
from Servo.new_servo_driver import *
from shtc3.shtc3_driver import *
from face_recognition_mod.recognitionWithTrack_820 import *
import select
import os

# from gpiozero import Servo

REMOTE_IP = '47.116.66.37'
REMOTE_PORT = 14564
SERVER_IP = getLocalIp()
SERVER_PORT = 5050
BUFSIZ = 1024
# LOG_FILE = open('./')


is_auto = True
is_close = False
server_address = (SERVER_IP, SERVER_PORT)
main_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 立刻释放端口
main_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
main_sock.bind(server_address)
# 最大同时连接数为5
main_sock.listen(5)
# 放每个客户端的socket
socks = [main_sock, ]


# 舵机初始化
def init_servo():
    global servo
    servo = servo_opt()
    servo.start()
    servo.reset()


# 初始化人脸识别模块(摄像头模块)
def init_recognition(face_data):
    global frames_reco
    frames_reco = recognition(servo.servo_x, servo.servo_y, face_arr=face_data)
    frames_reco.start()


# 温湿度模块初始化
def init_shtc3(ip):
    global shtc3
    shtc3 = shtc3_driver(ip)
    # 守护线程，主线程关闭后随之关闭
    shtc3.setDaemon(True)
    shtc3.start()


# 设备注册,获取人脸数据
def dev_register(SERVER_IP):
    tmp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tmp_socket.connect((REMOTE_IP, REMOTE_PORT))
    tmp_socket.send(bytes("register@%s," % SERVER_IP, 'utf8'))
    total_data = b''
    while True:
        part_data = tmp_socket.recv(BUFSIZ)
        log_print("拼接")
        total_data += part_data
        if not part_data or part_data[-1] == b','[0]: break

    data = eval(total_data.decode('utf8')[:-1])
    return data


def opt_servo(command, socket):
    if command == 'CamUp' or command == 'CamDown' or command == 'CamLeft' or command == 'CamRight':
        servo.cameraActionState = command
    elif command == 'Shutdown':
        servo.stop()
        log_print("程序被远程关闭")
        socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # tcpServer.shutdown()
        socket.close()
        time.sleep(1)
        exit()
    elif command == 'reset':
        servo.reset()
    else:
        log_print("接收到一个特殊指令：" + command)
        servo.cameraActionState = 'Stop'


# 修改温湿度阈值
def setup_config(data, conn):
    global shtc3
    try:
        temp_list = data.split(",")
        shtc3.min_tmp = float(temp_list[0]) if temp_list[0] else shtc3.min_tmp
        shtc3.max_tmp = float(temp_list[1]) if temp_list[1] else shtc3.max_tmp
        shtc3.min_hmt = float(temp_list[2]) if temp_list[2] else shtc3.min_hmt
        shtc3.max_hmt = float(temp_list[3]) if temp_list[3] else shtc3.max_hmt
        log_print("修改温湿度成功,%f,%f,%f,%f" % (shtc3.min_tmp, shtc3.max_tmp, shtc3.min_hmt, shtc3.max_hmt))
        conn.send(bytes('success,', 'utf8'))
    except Exception as e:
        conn.send(bytes('fail,', 'utf8'))
        log_print( "修改阈值异常", e)
    finally:
        socks.remove(conn)
        conn.close()


def handle_data(data, socket):
    # 反馈连接
    log_print("服务端接受到%s" % data)

    tempStr_arr = data.split("@")
    if tempStr_arr[0] == 'com':
        opt_servo(tempStr_arr[1], socket)
    elif tempStr_arr[0] == 'config':
        setup_config(tempStr_arr[1], socket)
    else:
        log_print('异常指令，无法解析', data)


if __name__ == '__main__':
    log_print("当前工作目录",os.getcwd())
    log_print("工作目录初始化...")
    os.chdir('/home/pi/iwms-server')
    log_print("当前工作目录",os.getcwd())

    log_print("舵机初始化...")
    init_servo()

    log_print("温湿度初始化")
    init_shtc3(REMOTE_IP)

    # 设备注册(获取人脸数据)
    face_data = dev_register(SERVER_IP)
    log_print("获取到人脸数据", face_data)

    # 启动人脸识别
    init_recognition(face_data)

    log_print("开始监听%s:%d" % server_address)
    while True:
        r, w, e = select.select(socks, [], [], 10)
        try:
            for fd in r:
                if fd == main_sock:
                    conn, addr = fd.accept()
                    socks.append(conn)
                    log_print("accept from", addr)

                    # 启动视频流
                    frames_reco.start_frames(addr[0])

                    # 更新安卓端ip
                    shtc3.android_ip = addr[0]

                    recv_data = conn.recv(BUFSIZ)

                    data = recv_data.decode("utf8")
                    log_print("main_socket接受到%s" % data)

                    if not data or data == 'exit':
                        socks.remove(conn)
                        log_print('连接已断开')
                        # 关闭视频流
                        frames_reco.stop_frames()

                    handle_data(data, conn)

                else:
                    msg = fd.recv(BUFSIZ)
                    # 反馈连接(先解码成字符串，形成新字符串，后重新编码发送)
                    data = msg.decode("utf8")
                    log_print("服务端接受到%s" % data)

                    if not data or data == 'exit':
                        socks.remove(fd)
                        log_print('连接已断开')
                        # 关闭视频流
                        frames_reco.stop_frames()
                    else:
                        handle_data(data, conn)

        except ConnectionAbortedError:
            socks.remove(fd)
        except UnicodeDecodeError as ue:
            log_print("编码异常", ue)
        except Exception as e:
            log_print("异常", e)
            main_sock.close()
            break

    shtc3.is_stop = True
