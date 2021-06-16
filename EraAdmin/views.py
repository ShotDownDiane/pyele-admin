from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render

# Create your views here.
from . import utools
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
from . import models, modifiers
import base64


def test(request):
    if request.session.has_key('username'):
        return utools.ApiJsonResult(0, "", [
            request.session['username'],
            request.session['user_id']
        ])
    else:
        return utools.ApiJsonResult(1)


def frontend(request, action):
    if action == 'serve':
        print("运行")
    return utools.HtmlResult("ok")


@require_POST
@csrf_exempt
def login(request):
    username = request.POST.get("username", "")
    password = request.POST.get("password", "")
    code = request.POST.get("code", "")
    remember = request.POST.get("remember")
    sysUser = models.SysUser.objects.get(username=username)
    if not CaptchaStore.objects.filter(response=code, hashkey=request.POST.get('key', '')):
        return utools.ApiJsonResult(1, "验证码错误")

    if sysUser is None:
        return utools.ApiJsonResult(1, "用户名或密码错误")
    if not check_password(password, sysUser.password):
        return utools.ApiJsonResult(1, "用户名或密码错误")
    if sysUser.state == 1:
        return utools.ApiJsonResult(1, "账号已被冻结")
    if not sysUser.login(request):
        return utools.ApiJsonResult(1, "登录失败,错误码 ER401")

    token_type = "Bearer"
    access_token = sysUser.token
    request.session['username'] = username
    request.session['user_id'] = sysUser.user_id
    return utools.ApiJsonResult(0, "登录成功", None, {
        "access_token": access_token,
        "token_type": token_type
    })


# 生成验证码
@require_GET
def captcha(request):
    mode = request.GET.get('mode', 'base64')
    hashKey = CaptchaStore.generate_key()
    image_url = captcha_image_url(hashKey)
    if mode == 'url':
        return utools.ApiJsonResult(jsonData={'key': hashKey, 'image_url': image_url})
    if mode == 'base64':
        base64_data = base64.b64encode(
            utools.http_request("http://" + request.META['HTTP_HOST'] + image_url).content).decode('utf8')
        return utools.ApiJsonResult(data="data:image/png;base64," + base64_data, jsonData={'key': hashKey})
    return utools.ApiJsonResult(code=1, msg="mode只支持[url,base64]参数", jsonData={'text': ''})


class Main:
    @staticmethod
    @modifiers.auth(forceLogin=True)
    def menu(request):
        sysUser: models.SysUser = request.AUTH.getUserInfo()
        data = utools.generate_tree(source=sysUser.get_current_user_menu(), id="menu_id", pid="parent_id",
                                    child="children")
        return utools.ApiJsonResult(data=data, hump=True)

    @staticmethod
    @modifiers.auth(forceLogin=True)
    def user(request):
        sysUser: models.SysUser = request.AUTH.getUserInfo()
        data = sysUser.toDict()
        data['authorities'] = sysUser.get_authorities()
        data['roles'] = sysUser.get_current_user_role()
        return utools.ApiJsonResult(data=data, hump=True)

    @staticmethod
    @csrf_exempt
    @require_http_methods(['PUT'])
    @modifiers.auth(forceLogin=True)
    def password(request):
        data = request.input()
        sysUser: models.SysUser = request.AUTH.getUserInfo()
        if not check_password(data['oldPsw'], sysUser.password):
            return utools.ApiJsonResult(1, "旧密码不正确")
        if data['newPsw'] == data['oldPsw']:
            return utools.ApiJsonResult(1, "新旧密码一致,无需修改")
        sysUser.password = make_password(data['newPsw'])
        sysUser.save()
        return utools.ApiJsonResult(msg="修改成功")


class OAuth:
    @staticmethod
    @csrf_exempt
    @require_http_methods(['GET'])
    def info(request):
        if not request.user.username:
            return utools.ApiJsonResult(code=80001, msg="请先登录")
        user = models.SysUser.get_user_info(username=request.user.username)
        return utools.ApiJsonResult(data=user.toDict())

    @staticmethod
    @csrf_exempt
    @require_http_methods(['GET'])
    def to_login(request):
        return utools.HtmlResult('')
        # return utools.redirect('http://localhost:8080/')
