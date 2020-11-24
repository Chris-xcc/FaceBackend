import numpy as np
from PIL import Image
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from rest_framework import status, mixins, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from utils.permissions import IsOwnerOrReadOnly
from utils.image_processing import detector_cv2, model_path, recognizer, img_name, image_to_np
from utils.train import get_images, save_model

from .models import User, Sign
from .serializers import (UserDetailSerializer, UserRegisterSerializer, SignCreateSerializer, StuSignSerializer,
                          SignInfoListSerializer, SignInfoRetrieveSerializer, SignSerializer)


class CustomBackend(ModelBackend):
    """
    自定义用户验证:
        学号登录
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(number=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


# 用户
class UserViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """
    用户
    list:
            所有用户（admin权限）
    retrieve:
            用户个人信息
    create:
            用户注册
    update:
            用户个人资料修改
    """
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_queryset(self):
        if self.action == 'retrieve':
            return User.objects.filter(username=self.request.user.username)
        elif self.action == 'create':
            return User.objects.all()
        elif self.action == 'list':
            return User.objects.all()
        return User.objects.filter(username=self.request.user.username)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action == 'create':
            return UserRegisterSerializer
        return UserDetailSerializer

    def get_permissions(self):
        if self.action == 'retrieve':
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        elif self.action == 'create':
            return []
        elif self.action == 'list':
            return [IsAdminUser()]
        return []

    # 用户注册并登录
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        re_dict = serializer.data
        # payload = jwt_payload_handler(user)
        # re_dict['token'] = jwt_encode_handler(payload)
        # re_dict['name'] = user.username

        headers = self.get_success_headers(serializer.data)
        return Response('用户创建成功', status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()

    # 用户个人资料修改
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response('信息修改成功', status=status.HTTP_200_OK)

    # 返回当前用户 /user/{id} id可以是任意值
    def get_object(self):
        return self.request.user


class StuSignViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
        list:
            所有签到标题
        retrieve：
            学生签到
        update：
            学生上传图片完成签到
    """
    permission_classes = [IsAuthenticated, ]
    queryset = Sign.objects.all()
    serializer_class = StuSignSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid()
        face = request.data['face']
        # # print(face)
        # image = Image.open(face).convert('L')
        # image_np = np.array(image, 'uint8')
        image_np = image_to_np(face)

        faces = detector_cv2.detectMultiScale(image_np, 1.2, 5)
        recognizer.read(model_path)
        user = User.objects.filter(username=request._user)[0]

        for (x, y, w, h) in faces:
            img_id, conf = recognizer.predict(image_np[y:y + h, x:x + w])
            # print(img_id, conf)
            # img_id = 2017127249
            if user.number == img_id:
                face._name = img_name
                user.signin.add(instance.id)
                user.face = face
                user.save()
                # print(user_face)
                # serializer.is_valid(raise_exception=True)
                # self.perform_update(serializer)
                #
                # if getattr(instance, '_prefetched_objects_cache', None):
                #     # If 'prefetch_related' has been applied to a queryset, we need to
                #     # forcibly invalidate the prefetch cache on the instance.
                #     instance._prefetched_objects_cache = {}

                return Response('签到成功')
            else:
                return Response('签到失败，请重试')
        return Response('获取图片失败')


class SignCreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = SignCreateSerializer
    permission_classes = [IsAdminUser, ]
    queryset = Sign.objects.all()


class SignInfoViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
        签到标题
        retrieve：
            签到情况
    """
    queryset = Sign.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'list':
            return SignInfoListSerializer
        if self.action == 'retrieve':
            return SignInfoRetrieveSerializer


class SignViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Sign.objects.all()
    serializer_class = SignSerializer


class TrainModel(APIView):
    """
    训练模型
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 人脸样本
        face_samples = []
        # 标签样本
        labels = []

        for sample_paths, sample_label in get_images('face_img'):
            # print(sample_paths)
            # 遍历图片样本
            for sample in sample_paths:
                # 将图片样本转换为ndarray类型
                image_np = image_to_np(sample)
                # print(image_np)
                # 检测人脸位置
                faces = detector_cv2.detectMultiScale(image_np)
                # 对人脸贴上标签
                for (x, y, w, h) in faces:
                    face_samples.append(image_np[y:y + h, x:x + w])
                    labels.append(int(sample_label))

        # 训练模型
        recognizer.train(face_samples, np.array(labels))
        # 保存模型
        recognizer.save(save_model('face_model.yml'))
        return Response('模型已更新')
