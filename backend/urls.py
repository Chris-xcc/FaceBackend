"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.views.static import serve
from django.conf.urls.static import static
from django.urls import path, re_path, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from rest_framework_jwt.views import obtain_jwt_token

from backend.settings import MEDIA_ROOT
from face.views import UserViewSet, StuSignViewSet, SignCreateViewSet, SignInfoViewSet, TrainModel, SignViewSet

router = routers.DefaultRouter()

router.register(r'user', UserViewSet, basename='user')
router.register(r'sign_create', SignCreateViewSet, basename='sign_create')
router.register(r'sign_stu', StuSignViewSet, basename='sign_stu')
router.register(r'sign_info', SignInfoViewSet, basename='sign_info')
router.register(r'sign', SignViewSet, basename='sign')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('train/',TrainModel.as_view(),),
    path('docs/', include_docs_urls(title='我的博客')),
    path('api-auth/', include('rest_framework.urls')),
    re_path(r'^login/', obtain_jwt_token),
    # 生产环境下加入该行，用于在（debug=False）生产环境下显示图片，如果不加该行，在生产环境下无法显示图片
    re_path('media/(?P<path>.*)', serve, {"document_root": MEDIA_ROOT}),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # 添加该行，为了上传和显示图片

