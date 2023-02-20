/usr/sbin/i2cset -f -y 1 0x60 0x00 0
# 视频流程序后台单独运行
python3 camera.py &
python3 main.py