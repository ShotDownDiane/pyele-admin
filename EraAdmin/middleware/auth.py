import hashids
from django.utils.deprecation import MiddlewareMixin
from EraAdmin import settings, models, utools
import jwt


class AuthMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        return response

    def process_request(self, request):
        Authorization = request.META.get("HTTP_AUTHORIZATION", "")
        iAuth = AUTH()
        if Authorization:
            if request.user:
                if request.user.username:
                    if request.user.username == 'admin':
                        user_id = 1
                    else:
                        hash_ = hashids.Hashids(salt=settings.SAFE_SALT, min_length=8)
                        user_id = hash_.decode(request.user.username)[0]

                    # 获取用户信息
                    def getUserInfo(uid):
                        return models.SysUser.objects.get(user_id=uid)

                    iAuth.setUserID(user_id)
                    iAuth.setUserInfo(user_info=getUserInfo)

        request.AUTH = iAuth


class AUTH:
    __UUID = None
    __USER_ID = None
    __USER_INFO = None
    __GET_USER_INFO = None

    def __init__(self):
        def getInfo(id):
            return {}

        self.__GET_USER_INFO = getInfo

    def setUserID(self, user_id):
        self.__USER_ID = user_id

    def getUserID(self):
        return self.__USER_ID

    def setUserInfo(self, user_info):
        if callable(user_info):
            self.__GET_USER_INFO = user_info
        else:
            self.__USER_INFO = user_info

    def IsLogin(self):
        if self.__USER_ID:
            return True
        else:
            return False

    def getUserInfo(self, key=None):
        info = self.__USER_INFO
        if info is None:
            info = self.__GET_USER_INFO(self.__USER_ID)
        if key:
            try:
                if key in info:
                    return info[key]
                else:
                    return None
            except TypeError as e:
                print("ERROR: [middleware@auth.getUserInfo] 不支持的取值方式", str(e))
                raise e
        else:
            return info
