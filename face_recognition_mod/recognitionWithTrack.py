# coding = utf-8
import face_recognition
import cv2
import numpy as np
import glob
import os
from Servo.Emakefun_MotorHAT import Emakefun_MotorHAT

def run():
    mh = Emakefun_MotorHAT(addr=0x60)
    servo1 = mh.getServo(1)
    servo2 = mh.getServo(2)
    x_servo = 105
    y_servo = 90
    servo1.writeServo(x_servo)
    servo2.writeServo(y_servo)

    video_capture = cv2.VideoCapture(0)
    all_faces_encoding = glob.glob('./face_encoding/*.npy')
    known_face_encodings = []
    known_face_names = []
    known_face_encodings = [np.load(face_encoding) for face_encoding in all_faces_encoding]
    known_face_names = [face.split('/')[2].split('.')[0] for face in all_faces_encoding]
    print(known_face_encodings)
    print(known_face_names)
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = 0
    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]
        # Only process every other frame of video to save time
        if process_this_frame == 6:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            if face_locations:
                x = (face_locations[0][1] + face_locations[0][3]) / 2
                y = (face_locations[0][0] + face_locations[0][2]) / 2
                print(x, y)  # 输出脸中心到右上顶点的水平和垂直距离
            else:
                x, y = 80, 60  # 如果没有脸则让舵机保持不动，相当于脸在中央（这时的分辨率为160*120）
                # 计算出舵机应该移动的角度，正负与舵机的安装方式有关
            dx = (80 - x) * 0.3125
            dy = (60 - y) * 0.3125

            if abs(dx) >= 0.5:  # 设置一个阈值，当角度大于3时，才移动，避免舵机一直在原地抖动，下同
                x_servo += dx
                if x_servo > 179:  # 设置界限，超出范围不再转动，下同
                    x_servo = 179
                elif x_servo < 1:
                    x_servo = 1
                servo1.writeServo(x_servo)  # 水平方向的舵机控制

            if abs(dy) >= 1.5:  # 设置阈值
                y_servo += dy
                if y_servo > 140:
                    y_servo = 140
                elif y_servo < 1:
                    y_servo = 1
                servo2.writeServo(y_servo)  # 垂直方向的舵机控制

            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"
                # # If a match was found in known_face_encodings, just use the first one.
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     name = known_face_names[first_match_index]
                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings,
                                                                    face_encoding)  # 计算未知面孔与所有已知面孔的特征距离
                best_match_index = np.argmin(face_distances)  # 给出distance最小的下标
                if matches[best_match_index]:  # 若在matches列表中存在
                    name = known_face_names[best_match_index]
                face_names.append(name)
            process_this_frame = 0
        process_this_frame += 1
        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        # Display the resulting image
        # 显示画面
        # cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            os.system("i2cset -f -y 1 0x60 0x08 0")
            os.system("i2cset -f -y 1 0x60 0x09 0")
            os.system("i2cset -f -y 1 0x60 0x0c 0")
            os.system("i2cset -f -y 1 0x60 0x0d 0")
            break
    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    run()