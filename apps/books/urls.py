from django.urls import include

from EraAdmin import route
from . import views
from . import apps

p = route.APP(apps.BooksConfig.name).path

urlpatterns = [
    route.get('auth/$', views.auth),
    route.get('auth/callback', views.auth_callback),
    route.get('auth/user', views.auth_user),
    # 前台接口
    route.get('api/get_books_list$', p('books.Books.bookList')),
    route.get('api/get_chapter_list$', p('books.Books.chapterList')),
    # 后台首页地址
    route.get('^admin$', p('admin.Index.index')),
    route.get('^admin/components', p('admin.Index.components')),
    route.path('admin/api/', include([
        route.get('auth/user', views.auth_user)
    ]))
]
