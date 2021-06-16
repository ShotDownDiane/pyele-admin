from . import utools


class HttpController:
    request = None

    def __init__(self, request):
        self.request = request
        self.init()

    def init(self):
        pass

    def CURD_DELETE(self, model, filters=None, ids=None, pk=None):
        names = locals()
        # 解释主键
        if not pk:
            if hasattr(model.Attrs, 'pk'):
                pk = model.Attrs.pk
            else:
                pk = 'id'
        # 如果存在filters，直接使用filters筛选
        if filters:
            model = model.objects.filter(filters)
        if ids:
            model = model.objects.filter(**{pk + "__in": ids})

        return model.delete()

    def CURD_SAVE(self, model, data):
        utools.object_set_attrs(model, data, False)
        model.save(data)

    def getPageParams(self, page=1, limit=20):
        """
            获取分页参数
            :param page:
            :param limit:
            :return:
        """
        return int(self.request.GET.get('page', page)), int(self.request.GET.get('limit', limit))
