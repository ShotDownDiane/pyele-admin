from django.shortcuts import render

# Create your views here.
from EraAdmin import utools, models
from EraAdmin.oauth import OAuth
from apps.books.config import config


def auth_user(request):
    SysUser: models.SysUser = request.AUTH.getUserInfo()

    return utools.ApiJsonResult(data=SysUser.toDict())


def auth(request):
    uri = OAuth(config).get_auth_uri(state=utools.get_random_str(),
                                     redirect_uri="http://127.0.0.1:8100/books/auth/callback")
    return utools.redirect(uri)


def auth_callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    if error:
        result = {
            'error': error,
            'error_msg': '授权被拒绝'
        }
    else:
        result = OAuth(config).get_token(code)

    print("授权Token结果：", result)
    result['success'] = True
    if 'error' in result:
        result['success'] = False
        if result['error'] == 'invalid_grant':
            result['error_msg'] = '无效的授权凭证'
    if result['success']:
        result['user'] = dict()
        template = './common/OAUTH-AuthorizationSuccessful.html'
    else:
        template = './common/OAUTH-AuthorizationFail.html'
    result['state'] = state
    return utools.view(request, tpl=template, data=result)
