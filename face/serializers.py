import cv2
from time import localtime, strftime
from random import randint

import numpy as np
from PIL import Image
from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from utils.image_processing import detector_dlib, detector_cv2, image_to_np
from .models import User, Sign


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详情序列化类
    """
    SEX_TYPE = (
        ('male', '男'),
        ('female', '女'),
    )
    username = serializers.CharField(required=False, label='姓名', help_text='姓名', max_length=20,
                                     validators=[UniqueValidator(queryset=User.objects.all(), message='该用户已存在')])
    sex = serializers.ChoiceField(required=False, label='性别', help_text='性别', choices=SEX_TYPE)
    password = serializers.CharField(required=False, label='密码', help_text='密码', write_only=True)
    check_password = serializers.CharField(required=False, label='确认密码', help_text='确认密码', write_only=True)
    face = serializers.ImageField(required=False, label='人脸图片', help_text='人脸图片',
                                  validators=[FileExtensionValidator(['jpg', 'png'], message='必须为jpg,png格式的文件')])

    def update(self, instance, validated_data):
        """更新，instance为要更新的对象实例"""
        username = validated_data.get('username', instance.username)
        sex = validated_data.get('sex', instance.sex)
        password = validated_data.get('password', instance.password)
        check_password = validated_data.get('check_password', instance.check_password)
        face = validated_data.get('face', instance.face)
        if face:
            image_np = image_to_np(face)
            faces = detector_dlib(image_np, 0)
            for index, rect in enumerate(faces):
                cv2.rectangle(image_np, (rect.top(), rect.left()), (rect.bottom(), rect.right()), (0, 0, 225), 2)

            if len(faces) == 1:
                pass
            else:
                raise serializers.ValidationError('图片不符合要求')
            img_name = strftime("%Y%m%d%H%M%S", localtime()) + str(randint(10, 99)) + '.jpg'
            face._name = img_name
            instance.face = face
        if password or check_password == '':
            pass
        else:
            if password == check_password:
                instance.set_password(password)
            else:
                raise serializers.ValidationError('密码不一致')
        instance.save()
        return instance

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'password',
            'number',
            'sex',
            'check_password',
            'face'
        ]
        read_only_fields = [
            'number',
        ]


class UserRegisterSerializer(serializers.Serializer):
    SEX_TYPE = (
        ('male', '男'),
        ('female', '女'),
    )
    # username = serializers.CharField(required=True, label='姓名', help_text='姓名', max_length=20,
    #                                  validators=[UniqueValidator(queryset=User.objects.all(), message='该用户已存在')])
    number = serializers.CharField(required=True, label='学号', help_text='学号', max_length=20, min_length=7,
                                   validators=[UniqueValidator(queryset=User.objects.all(), message='学号已存在')])
    password = serializers.CharField(required=True, label='密码', help_text='密码', max_length=14, min_length=6,
                                     write_only=True)
    check_password = serializers.CharField(required=True, label='确认密码', help_text='确认密码',
                                           max_length=14, min_length=6, write_only=True)

    # sex = serializers.ChoiceField(required=True, label='性别', help_text='性别', choices=SEX_TYPE)

    def validate(self, attrs):
        """
         整体验证
        :param attrs:
        :return:
        """
        password = attrs['password']
        check_password = attrs['check_password']
        if password != check_password:
            raise serializers.ValidationError('密码不一致')
        return attrs

    def create(self, validated_data):
        # username = validated_data['username']
        number = validated_data['number']
        password = validated_data['password']
        # sex = validated_data['sex']
        user = User.objects.create(number=number, password=password)

        # 设置用户密码
        user.set_password(password)
        user.save()
        return user


class SignCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sign
        fields = '__all__'


class StuSignSerializer(serializers.ModelSerializer):
    face = serializers.ImageField(required=False, label='人脸图片', help_text='人脸图片',
                                  max_length=None, use_url=True, allow_empty_file=False,
                                  validators=[FileExtensionValidator(['jpg', 'png'], message='必须为jpg,png格式的文件')])

    def validate(self, attrs):

        # 图片
        face = attrs['face']
        image_np = image_to_np(face)
        faces = detector_cv2.detectMultiScale(image_np, 1.2, 5)
        # 人脸数量
        if len(faces) == 1:
            return attrs
        else:
            raise serializers.ValidationError('图片无效')

    class Meta:
        model = Sign
        fields = ['id', 'face', 'title']
        read_only_fields = [
            'title',
            'id'
        ]


class SignInfoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sign
        fields = '__all__'


class UserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'number', 'sex']


class SignInfoRetrieveSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        user = User.objects.filter(signin__id=obj.id)
        serializers_post = UserRetrieveSerializer(user, many=True)
        return serializers_post.data

    class Meta:
        model = Sign
        fields = '__all__'


class SignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sign
        fields = '__all__'
