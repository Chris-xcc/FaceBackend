from random import randint
from time import strftime, localtime

import cv2
import dlib
import numpy as np
from PIL import Image

from backend.settings import BASE_DIR

# Dlib 正向人脸检测器 / Use frontal face detector of Dlib
detector_dlib = dlib.get_frontal_face_detector()

detector_cv2 = cv2.CascadeClassifier(str(BASE_DIR.joinpath('model').joinpath('haarcascade_frontalface_alt2.xml')))
model_path = str(BASE_DIR.joinpath('model').joinpath('trainner.yml'))

recognizer = cv2.face.LBPHFaceRecognizer_create()
img_name = strftime("%Y%m%d%H%M%S", localtime()) + str(randint(10, 99)) + '.jpg'


def image_to_np(image):
    image = Image.open(image).convert('L')
    # 将图片样本转换为ndarray类型
    image_np = np.array(image, 'uint8')
    return image_np
