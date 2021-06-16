from django.urls import re_path, path, include
from EraAdmin.module.sys import views as Sys_Views
import EraAdmin.route as route
urlpatterns = [
    route.get('sys/config/get_email_config', 'EraAdmin@sys.views.Config.get_email_config'), 
    path('sys/', include([
        path('user', Sys_Views.User.save),
        path('user/page', Sys_Views.User.list),
        path('user/batch', Sys_Views.User.batch_delete),
        re_path(r'user/(?P<user_id>\w+)$', Sys_Views.User.delete),
        re_path(r'user/state/(?P<user_id>\w+)$', Sys_Views.User.state),
        re_path(r'user/psw/(?P<user_id>\w+)$', Sys_Views.User.psw),
        path('role', Sys_Views.Role.index),
        path('role/page', Sys_Views.Role.list),
        path('role/batch', Sys_Views.Role.batch_delete),
        path('role/menu', Sys_Views.Role.menu),
        re_path(r'role/menu/(?P<role_id>\w+)$', Sys_Views.Role.saveMenu),
        re_path(r'role/(?P<role_id>\w+)$', Sys_Views.Role.delete),
        path('menu', Sys_Views.Menu.index),
        re_path(r'menu/(?P<menu_id>\w+)$', Sys_Views.Menu.delete),
        path('organization', Sys_Views.Organization.index),
        re_path(r'organization/(?P<organization_id>\w+)$', Sys_Views.Organization.delete),
        path('dictdata', Sys_Views.Dictdata.index),
        path('dictdata/page', Sys_Views.Dictdata.list),
        path('dictdata/batch', Sys_Views.Dictdata.batch_delete),
        re_path(r'dictdata/(?P<dict_data_id>\w+)$', Sys_Views.Dictdata.delete),
        path('dict', Sys_Views.Dict.index),
        re_path(r'dict/(?P<dict_id>\w+)$', Sys_Views.Dict.delete),
        path('loginRecord/page', Sys_Views.loginRecord.list),
        path('operRecord/page', Sys_Views.operRecord.list),
    ]))
]
