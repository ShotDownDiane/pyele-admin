from django.core.paginator import Paginator
from EraAdmin import utools
from EraAdmin.controller import HttpController
import apps.books.models as models


class Books(HttpController):
    def bookList(self):
        page, limit = self.getPageParams()
        title = self.request.GET.get('title', '')

        Novel = models.Novel.objects
        if title:
            Novel = Novel.filter(title__contains=title)

        p = Paginator(Novel.order_by('-novel_id').all(), per_page=limit)
        count = p.count
        data = list(p.page(page))

        def d(item):
            item: models.Novel
            row = item.toDict()
            return row

        utools.each(d=d, s=data)

        return utools.ApiJsonResult(jsonData={'count': count, 'data': data}, hump=True)

    def chapterList(self):
        page, limit = self.getPageParams()
        am_id = self.request.GET.get('am_id', '')
        name = self.request.GET.get('name', '')
        NovelChapter = models.NovelChapter.objects.filter(am_id=am_id)
        if name:
            NovelChapter = NovelChapter.filter(name__contains=name)

        p = Paginator(NovelChapter.order_by('-novel_id').all(), per_page=limit)
        count = p.count
        data = list(p.page(page))

        def d(item):
            item: models.Novel
            row = item.toDict()
            return row

        utools.each(d=d, s=data)

        return utools.ApiJsonResult(jsonData={'count': count, 'data': data}, hump=True)
