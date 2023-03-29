import collections
import time

from flask import Flask,Response
from utils import *

app = Flask(__name__)

class VideoCamera(object):
    _instance_lock = threading.Lock()

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(VideoCamera, "_instance"):
            with VideoCamera._instance_lock:
                if not hasattr(VideoCamera, "_instance"):
                    VideoCamera._instance = VideoCamera(*args, **kwargs)
        return VideoCamera._instance

    def __init__(self):
        if not hasattr(VideoCamera, "video"):
            print('创建')
            # 通过opencv获取实时视频流
            self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        ret,jpeg = cv2.imencode('.jpg', image)
        return jpeg

def gen():
    camera = VideoCamera.instance()
    image = camera.get_frame()
    send_photos(image)
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame.tobytes() + b'\r\n')

# 将视频流路由至ip:port/device/1
@app.route('/device/1')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def send_photos(image):
    # camera = VideoCamera.instance()
    # image = camera.get_frame()
    resp = send_post_request('img', frame_to_base64(image), 'http://192.168.2.2:8080/report/photo/1')
    print(resp)

# t1 = threading.Thread(target=send_photos)
# t1.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,threaded=True)
