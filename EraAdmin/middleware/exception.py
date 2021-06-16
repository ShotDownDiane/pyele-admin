from django.utils.deprecation import MiddlewareMixin
import requests


class ExceptionMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):
        print("发生异常：{}".format(exception), request)
        print("发送异常报告……")
        # 通知错误
        # res = requests.get("http://127.0.0.1:8001/home/{}".format(exception))
        # if res.status_code != 200:
        #     print("异常通知失败！")
