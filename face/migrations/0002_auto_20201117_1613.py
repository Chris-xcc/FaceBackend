# Generated by Django 3.1.3 on 2020-11-17 08:13

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('face', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='face',
            field=models.ImageField(blank=True, upload_to=models.CharField(max_length=20, unique=True, verbose_name='姓名'), validators=[django.core.validators.FileExtensionValidator(['jpg', 'png'], message='必须为jpg,png格式的文件')], verbose_name='人脸'),
        ),
    ]
