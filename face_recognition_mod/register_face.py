import face_recognition
import cv2
import numpy as np
import time
import glob

def register(imgNum):
    name = input('请输入用户名：')
    time.sleep(2)
    print('目视摄像头')
    video_capture = cv2.VideoCapture(0)
    for i in range(imgNum):
        ret, frame = video_capture.read()
        cv2.imwrite('/home/pi/iwms-server/face_recognition/test_images/' + name.strip() + str(i) + '.jpg', frame)
    print('采集完成')

    # 计算人脸数据
    img_path = glob.glob('/home/pi/iwms-server/face_recognition/test_images/' + name + '*' + '.jpg')
    print(img_path)
    all_face_encoding = []
    for img in img_path:
        image = face_recognition.load_image_file(img)
        face_encoding = face_recognition.face_encodings(image)[0]
        all_face_encoding.append(face_encoding)
        print(type(face_encoding))
        print(face_encoding)
    all_face_encoding = np.array(all_face_encoding)
    mean_face = np.mean(all_face_encoding, 0)
    print(type(mean_face))
    np.save('/home/pi/iwms-server/face_recognition/face_encoding/' + name.strip() + '.npy', mean_face)
    print(mean_face)

if __name__ == '__main__':
    register(2)