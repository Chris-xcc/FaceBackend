from pathlib import Path, PurePath

import cv2

from backend.settings import BASE_DIR

# 分类器
detector = cv2.CascadeClassifier("haarcascade_frontalface_alt2.xml")

recognizer = cv2.face.LBPHFaceRecognizer_create()

# 人脸样本
face_samples = []
# 标签样本
labels = []

# 模型保存路径
def save_model(model):
    save_model_path = BASE_DIR.joinpath('model')
    return str(save_model_path.joinpath(model))


# def get_images(path):
#     # media\face_img
#     path = os.path.join('media', path)
#     # print(path)
#     # 遍历media\face_img下的所有文件
#     for label in os.listdir(path):
#         # print(label)
#         # 拼接路径并改变目录到 工程目录\media\face_img\label
#         # print(label)
#         # os.chdir(os.path.join(path, label))
#         # path = os.getcwd()
#
#         # 'E:\\GraduationProject\\face\\src\\Opencv_\\media\\face_img\\2017127260
#         label_path = os.path.abspath(os.path.join(path, label))
#         # print(os.listdir(label_path))
#         # 获取图片样本路径
#         image_sample_paths = [(os.path.join(label_path, img)) for img in os.listdir(label_path)]
#         # print(image_sample_paths)
#         # 返回该标签下的所有图片样本路径、标签
#         yield image_sample_paths, label


def get_images(path):
    # 项目工程\media\face_img
    path = BASE_DIR.joinpath('media').joinpath(path)

    # 遍历media\face_img下的所有文件
    for label in Path.iterdir(path):
        # 拼接路径并改变目录到 工程目录\media\face_img\label
        # print(label)

        # 获取图片样本路径 [WindowsPath('项目工程/media/face_img/1/2020112015241575.jpg'),
        image_sample_paths = [label.joinpath(img) for img in Path.iterdir(label)]
        # print(image_sample_paths)
        # <class 'pathlib.WindowsPath'>
        # print(type(image_sample_paths[0]))
        # # 返回该标签下的所有图片样本路径、标签
        yield image_sample_paths, PurePath(str(label)).name

# for sample_paths, sample_label in get_images('face_img'):
#     # 遍历图片样本
#     for sample in sample_paths:
#         image = Image.open(sample).convert('L')
#         # 将图片样本转换为ndarray类型
#         image_np = np.array(image).astype('uint8')
#         # print(image_np)
#         # 检测人脸位置
#         faces = detector.detectMultiScale(image_np)
#         # 对人脸贴上标签
#         for (x, y, w, h) in faces:
#             face_samples.append(image_np[y:y + h, x:x + w])
#             labels.append(int(sample_label))
# # print(face_samples)
# # print((np.array(labe)))
# # 训练模型
# recognizer.train(face_samples, np.array(labels))
# # 保存模型
# recognizer.save('mytrain.yml')
#
# # Faces, Ids = get_images('face_img')
# # print(Faces)
# # print('==============')
# # print(Ids)
# # recognizer.train(Faces, np.array(Ids))
# # recognizer.save('trainner1.yml')
