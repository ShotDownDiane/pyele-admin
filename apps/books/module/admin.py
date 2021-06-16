from EraAdmin import utools
from EraAdmin.controller import HttpController


class Index(HttpController):
    def index(self):
        return utools.template('index.html', 'books')
    def components(self):
        tpl = self.request.path_info.split('/books/admin/components/')
        return utools.template(tpl[1], 'books')
