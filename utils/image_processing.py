import base64
from io import BytesIO
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
model_path = str(BASE_DIR.joinpath('model').joinpath('face_model.yml'))

recognizer = cv2.face.LBPHFaceRecognizer_create()
img_name = strftime("%Y%m%d%H%M%S", localtime()) + str(randint(10, 99)) + '.jpg'
sign_img_save_path = BASE_DIR.joinpath('media/face_img')


def user_face_file(user_dir):
    path = sign_img_save_path.joinpath(user_dir)
    path.mkdir(exist_ok=True)


def base64_to_cv2(base_str):
    img_str = base64.b64decode(base_str)
    image_np = np.fromstring(img_str, np.uint8)
    image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    return image


def image_to_io(image_str):
    face_bytes = bytes(image_str.encode('utf8'))
    face_str = base64.b64decode(face_bytes)
    image_io = BytesIO(face_str)
    return image_io


def image_to_np(image):
    image = Image.open(image).convert('L')
    # image = Image.open(image)
    # 将图片样本转换为ndarray类型
    image_np = np.array(image, 'uint8')
    return image_np
