from django.utils.deprecation import MiddlewareMixin


class FormatMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        return response
