import cv2
from PIL import Image
from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from utils.image_processing import (detector_cv2, image_to_np, image_to_io, img_name, base64_to_cv2, sign_img_save_path,
                                    user_face_file)
from .models import User, Sign


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详情序列化类
    """
    # SEX_TYPE = (
    #     ('male', '男'),
    #     ('female', '女'),
    # )
    # username = serializers.CharField(required=False, label='姓名', help_text='姓名', max_length=20,
    #                                  validators=[UniqueValidator(queryset=User.objects.all(), message='该用户已存在')])
    # sex = serializers.CharField(required=False, label='性别', help_text='性别', read_only=True)
    new_password = serializers.CharField(required=False, label='新密码', help_text='新密码', write_only=True)
    check_password = serializers.CharField(required=False, label='确认密码', help_text='确认密码', write_only=True)
    face = serializers.CharField(required=False, label='人脸图片', help_text='人脸图片', )

    # validators=[FileExtensionValidator(['jpg', 'png'], message='必须为jpg,png格式的文件')])

    def update(self, instance, validated_data):
        """更新，instance为要更新的对象实例"""
        # username = validated_data.get('username', instance.username)
        # sex = validated_data.get('sex', instance.sex)
        new_password = validated_data.get('new_password', instance.password)
        check_password = validated_data.get('check_password', instance.check_password)
        face = validated_data.get('face', instance.face)
        img = base64_to_cv2(face)
        img_path = (sign_img_save_path.joinpath(instance.number).joinpath(img_name))

        # 数据库保存目录
        # face_img / 2017127290 / 2020120121133629.jpg
        db_path = '/'.join(img_path.parts[-3:])

        # 创建用户人脸目录
        user_face_file(instance.number)
        # print(db_path)
        # print(img_path)
        cv2.imwrite(str(img_path), img)
        # print(image)
        # face_img / 2017127249 / 微信图片_20201125224726.jpg
        # print(db_path,img_path)
        instance.face = db_path
        # print(instance.face)
        if new_password == check_password:
            instance.set_password(new_password)
        instance.save()
        # print(1111)
        return instance

    def validate_face(self, face):
        # base64人脸图片
        image = base64_to_cv2(face)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        faces = detector_cv2.detectMultiScale(gray, 1.2, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(gray, (x, y), (x + w, y + h), (0, 0, 225), 2)

        if len(faces) == 1:
            pass
        else:
            raise serializers.ValidationError('图片不符合要求')

        return face

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'new_password',
            'sex',
            'number',
            'check_password',
            'face',
            'is_superuser'
        ]
        read_only_fields = [
            'username',
            'number',
            'is_superuser',
            'sex',
        ]


class UserRegisterSerializer(serializers.Serializer):
    SEX_TYPE = (
        ('male', '男'),
        ('female', '女'),
    )
    username = serializers.CharField(required=True, label='姓名', help_text='姓名', max_length=20,
                                     validators=[UniqueValidator(queryset=User.objects.all(), message='该用户已存在')])
    number = serializers.CharField(required=True, label='学号', help_text='学号', max_length=20, min_length=7,
                                   validators=[UniqueValidator(queryset=User.objects.all(), message='学号已存在')])
    password = serializers.CharField(required=True, label='密码', help_text='密码', max_length=14, min_length=6,
                                     write_only=True)
    check_password = serializers.CharField(required=True, label='确认密码', help_text='确认密码',
                                           max_length=14, min_length=6, write_only=True)

    sex = serializers.ChoiceField(required=True, label='性别', help_text='性别', choices=SEX_TYPE)

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
        """
        创建用户
        :param validated_data:
        :return:
        """
        username = validated_data['username']
        number = validated_data['number']
        password = validated_data['password']
        sex = validated_data['sex']
        user = User.objects.create(number=number, password=password, sex=sex, username=username)
        user_face_file(number)

        # 设置用户密码
        user.set_password(password)
        user.save()
        return user


class SignCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sign
        fields = '__all__'


class StuSignSerializer(serializers.ModelSerializer):
    face = serializers.CharField(required=False, label='人脸图片', help_text='人脸图片', )

    # max_length=None, use_url=True, allow_empty_file=False,
    # validators=[FileExtensionValidator(['jpg', 'png','jpeg'], message='必须为jpg,png格式的文件')])
    def validate(self, attrs):
        face_base64 = attrs['face']
        image = image_to_io(face_base64)
        image_np = image_to_np(image)

        faces = detector_cv2.detectMultiScale(image_np, 1.2, 5)
        # 人脸数量
        if len(faces) == 1:
            return attrs
        else:
            raise serializers.ValidationError('图片无效')

    # def validate(self, attrs):
    # 图片
    # face = attrs['face'].file
    # print(face.__dict__)
    # image = Image.open(face.file).convert('L')
    # # 将图片样本转换为ndarray类型
    # image_np = np.array(image, 'uint8')
    # cv2.imshow('1',image_np)
    # cv2.waitKey(0)
    #     image_np = image_to_np(face)
    #     faces = detector_cv2.detectMultiScale(image_np, 1.2, 5)
    #     # 人脸数量
    #     if len(faces) == 1:
    #         return attrs
    #     else:
    #         raise serializers.ValidationError('图片无效')

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
        serializers_user = UserRetrieveSerializer(user, many=True)
        return serializers_user.data

    class Meta:
        model = Sign
        fields = '__all__'


class SignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sign
        fields = '__all__'
