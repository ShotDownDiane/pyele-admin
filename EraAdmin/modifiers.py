from functools import wraps
from django.http import JsonResponse
from django.utils.log import log_response
'''
修饰器
'''

# 元数据
def meta(title=''):
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):

            return func(request, *args, **kwargs)
        return inner
    return decorator

# 权限处理
def auth(forceLogin=False, authority=None):
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if forceLogin:
                # 是否强制登录
                if not request.AUTH.IsLogin():
                    response = JsonResponse(data={'code':401,'msg':"无访问权限"})
                    response.status_code = 401
                    log_response(
                        'Api Unauthorized (%s): %s', request.method, request.path,
                        response=response,
                        request=request,
                    )
                    return response
                if authority:
                    pass
                    # 判断用户是否有 authority 中的权限项
                    # print("判断用户是否有 authority 中的权限项")

            return func(request, *args, **kwargs)
        return inner
    return decorator
