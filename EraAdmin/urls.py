"""EraAdmin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from functools import partial

from django.conf.urls import url
from django.contrib import admin
from django.urls import path, re_path, include

from . import views
from . import route

urlpatterns = [
    # 后台系统
    url(r'^django-admin/', admin.site.urls),
    # 授权中心 , 文档 https://www.jianshu.com/p/d8cef5049856
    re_path(r'^oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('oauth/info', views.OAuth.info),
    path('accounts/login/', views.OAuth.to_login),
    # 验证码
    re_path(r'^captcha-image', include("captcha.urls")),
    # EraAdmin管理系统
    path('admin/api/login', views.login),
    path('admin/api/captcha', views.captcha),
    path('admin/api/main/menu', views.Main.menu),
    path('admin/api/main/user', views.Main.user),
    path('admin/api/main/password', views.Main.password),
    path('admin/api/', include('EraAdmin.module.urls')),
    # book 站
    path('books/', include('apps.books.urls')),
    # path('frontend/', views.frontend),
    route.get('test/$', views.test),
    # route.get(r'test/(?P<dict_id>\w+)$', views.test, kwargs={'name':'233'}),
    # re_path(r'dict/(?P<dict_id>\w+)$', views.test),
    # route.get('test1', 'EraAdmin@sys.views.Test.prt'),
    # Route.get('test1', include("captcha.urls")),
]
