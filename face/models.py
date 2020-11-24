from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
def get_photo_path(instance, img):
    number = instance.number
    return 'face_img/{}/{}'.format(number, img)


class User(AbstractUser):
    SEX_TYPE = (
        ('male', '男'),
        ('female', '女'),
    )
    username = models.CharField('姓名', max_length=20, unique=True, null=True, blank=True)
    number = models.CharField('学号', max_length=20, unique=True)
    sex = models.CharField('性别', max_length=6, choices=SEX_TYPE)
    face = models.ImageField('人脸', blank=True, upload_to=get_photo_path)
    signin = models.ManyToManyField('Sign', blank=True, verbose_name='签到')

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'user'


class Sign(models.Model):
    title = models.CharField('标题', max_length=50)
    description = models.CharField('描述', max_length=150, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'sign'
