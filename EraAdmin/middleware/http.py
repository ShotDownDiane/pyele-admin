from django.utils.deprecation import MiddlewareMixin
import EraAdmin.utools as utools


class HttpMiddleware(MiddlewareMixin):
    INPUT = None

    def process_request(self, request):
        # 注册
        self.register(request).boot()
        pass

    def process_response(self, request, response):
        return response

    def register(self, request):
        if request.body:
            try:
                self.INPUT = utools.json_decode(request.body.decode())
            except ValueError as e:
                pass
        # 注册input函数
        request.input = self.get_body_inputs
        return self
    def boot(self):
        pass

    def get_body_inputs(self, name=None, default=None):
        if name:
            if name in self.INPUT:
                return self.INPUT[name]
            return default
        else:
            return self.INPUT
