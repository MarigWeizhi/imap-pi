import face_recognition
import cv2
import numpy as np
import os
import csv

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)
path = "./data/images/"
imgs_path = os.listdir(path)

# 人脸数据
face_encoding_list = []

# 后期检查已经入库的人，优化人脸数据（均值）
with open("./data/face_data.csv", mode="w", newline="") as file_write:
    writer = csv.writer(file_write)
    for file_name in imgs_path:
        name = file_name.split(".")[0]
        print("正在计算:" + name + "的图像数据")
        img_path = os.path.join(path, file_name)
        writer.writerow([name] + list(face_recognition.face_encodings(face_recognition.load_image_file(img_path))[0]))
