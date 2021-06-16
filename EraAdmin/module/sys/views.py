from django.contrib.auth.hashers import make_password
from django.views.decorators.http import require_GET, require_http_methods
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from EraAdmin import utools, models, modifiers
from EraAdmin.controller import HttpController


class User:

    @staticmethod
    @csrf_exempt
    @require_GET
    @modifiers.meta(title="查询用户列表")
    @modifiers.auth(forceLogin=True, authority="AdminUser:query_user_list")
    def list(request):
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        # 查询条件
        username = request.GET.get('username', '')
        nickname = request.GET.get('nickname', '')
        sex = request.GET.get('sex', None)
        organizationId = request.GET.get('organizationId')
        sysUser = models.SysUser.objects
        if username:
            sysUser = sysUser.filter(username__contains=username)
        if nickname:
            sysUser = sysUser.filter(nickname__contains=nickname)
        if sex:
            sysUser = sysUser.filter(sex=sex)
        if organizationId:
            sysUser = sysUser.filter(organization_id=organizationId)
        # 得到查询结果
        p = Paginator(sysUser.order_by('-user_id').all(), per_page=limit)
        count = p.count
        data = list(p.page(page))

        # 对查询结果进行数据处理
        def d(item):
            item: models.SysUser
            row = item.toDict()
            row['sexName'] = item.getSexName()
            row['roles'] = item.get_current_user_role()
            return row

        utools.each(d=d, s=data)

        return utools.ApiJsonResult(jsonData={'count': count, 'data': data}, hump=True)

    @staticmethod
    @csrf_exempt
    @require_http_methods(['PUT', 'POST', 'GET'])
    @modifiers.meta(title="保存用户信息")
    @modifiers.auth(forceLogin=True, authority="AdminUser:save_user")
    def save(request):
        if request.method == 'GET':
            username = request.GET.get('username', '')
            if username == '':
                return utools.ApiJsonResult(code=1, msg="请输入用户账号")
            data = list(
                models.SysUser.objects.filter(username=username).all().values('username', 'user_id', 'nickname'))
            return utools.ApiJsonResult(data=data)
        params = utools.json_decode(request.body.decode())
        if 'userId' in params:
            sysUser = models.SysUser.objects.get(user_id=params['userId'])
        else:
            sysUser = models.SysUser()
        utools.object_set_attrs(obj=sysUser, params=params,
                                attrs=['username', 'nickname', 'sex', 'email', 'birthday', 'introduction', 'phone'])
        if 'organizationId' in params:
            sysUser.organization_id = params['organizationId']
        active_time = utools.get_current_time()
        # 最后修改时间
        sysUser.update_time = active_time
        if request.method == 'POST':
            # 创建时间
            sysUser.create_time = active_time
            # 邮箱未验证
            sysUser.email_verified = 0
            # 状态正常
            sysUser.state = 0
            # 设置密码
            sysUser.password = make_password(params['password'])
            # 保存
            sysUser.save()
            # 设置用户角色
            sysUser.set_user_roles(roleIds=params['roleIds'])
            return utools.ApiJsonResult(msg="添加成功")
        if request.method == 'PUT':
            sysUser.save()
            sysUser.del_user_roles(roleIds='*')
            sysUser.set_user_roles(roleIds=params['roleIds'])
            return utools.ApiJsonResult(msg="修改成功")

    @staticmethod
    @csrf_exempt
    @require_http_methods(['PUT'])
    @modifiers.meta(title="修改用户状态")
    @modifiers.auth(forceLogin=True, authority="AdminUser:set_state")
    def state(request, user_id):
        sysUser = models.SysUser.objects.get(user_id=user_id)
        if sysUser.state:
            sysUser.state = 0
        else:
            sysUser.state = 1
        sysUser.save()
        return utools.ApiJsonResult(msg="设置成功")

    @staticmethod
    @csrf_exempt
    @require_http_methods(['PUT'])
    @modifiers.meta(title="修改用户密码")
    @modifiers.auth(forceLogin=True, authority="AdminUser:reset_password")
    def psw(request, user_id):
        params = utools.json_decode(request.body.decode())
        sysUser = models.SysUser.objects.get(user_id=user_id)
        sysUser.password = make_password(params['password'])
        sysUser.save()
        return utools.ApiJsonResult(msg="修改成功")

    @staticmethod
    @csrf_exempt
    @require_http_methods(['DELETE'])
    @modifiers.meta(title="删除用户")
    @modifiers.auth(forceLogin=True, authority="AdminUser:delete_user")
    def delete(request, user_id):
        if int(user_id) in models.SysUser.Attrs.superIds:
            return utools.ApiJsonResult(code=1, msg="无权删除该账号")
        HttpController(request).CURD_DELETE(models.SysUser, ids=[user_id])
        return utools.ApiJsonResult(msg="删除成功")

    @staticmethod
    @csrf_exempt
    @require_http_methods(['DELETE'])
    @modifiers.meta(title="批量删除用户")
    @modifiers.auth(forceLogin=True, authority="AdminUser:batch_delete_user")
    def batch_delete(request):
        ids = list(utools.array_filter(data=request.input(), filters=models.SysUser.Attrs.superIds))
        if len(ids) > 0:
            HttpController(request).CURD_DELETE(models.SysUser, ids=ids)
        else:
            return utools.ApiJsonResult(code=1, msg="内置角色不允许删除")
        return utools.ApiJsonResult(msg="删除成功")


class Role:
    @staticmethod
    @csrf_exempt
    @require_GET
    @modifiers.meta(title="查询角色列表")
    @modifiers.auth(forceLogin=True)
    def list(request):
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        # 查询条件
        role_name = request.GET.get('roleName', '')
        role_code = request.GET.get('roleCode', '')
        comments = request.GET.get('comments', None)
        SysRole = models.SysRole.objects
        if role_name:
            SysRole = SysRole.filter(role_name__contains=role_name)
        if role_code:
            SysRole = SysRole.filter(role_code__contains=role_code)
        if comments:
            SysRole = SysRole.filter(comments__contains=comments)

        p = Paginator(SysRole.order_by('-role_id').all(), per_page=limit)
        count = p.count
        data = list(p.page(page))

        def d(item):
            item: models.SysRole
            row = item.toDict()
            return row

        utools.each(d=d, s=data)

        return utools.ApiJsonResult(jsonData={'count': count, 'data': data}, hump=True)

    @staticmethod
    @csrf_exempt
    @require_http_methods(['PUT', 'POST', 'GET'])
    @modifiers.meta(title="")
    @modifiers.auth(forceLogin=True)
    def index(request):
        if request.method == 'GET':
            return Role.list(request)
        data = utools.underline_dict(request.input())
        if request.method == 'POST':
            HttpController(request).CURD_SAVE(models.SysRole(), data)
            return utools.ApiJsonResult(msg="保存成功")
        if request.method == 'PUT':
            role_id = data['role_id']
            del data['role_id']

            sysRole = models.SysRole.objects.get(role_id=role_id)
            utools.object_set_attrs(sysRole, data)
            sysRole.save()
            return utools.ApiJsonResult(msg="修改成功")

    @staticmethod
    @csrf_exempt
    @require_http_methods(['DELETE'])
    @modifiers.meta(title="删除角色")
    @modifiers.auth(forceLogin=True, authority="AdminUser:delete_role")
    def delete(request, role_id):
        if int(role_id) in models.SysRole.Attrs.superIds:
            return utools.ApiJsonResult(code=1, msg="内置角色不允许删除")
        HttpController(request).CURD_DELETE(models.SysRole, ids=[role_id])
        return utools.ApiJsonResult(msg="删除成功")

    @staticmethod
    @csrf_exempt
    @require_http_methods(['DELETE'])
    @modifiers.meta(title="批量删除角色")
    @modifiers.auth(forceLogin=True, authority="AdminUser:batch_delete_role")
    def batch_delete(request):
        ids = list(utools.array_filter(data=request.input(), filters=models.SysRole.Attrs.superIds))
        if len(ids) > 0:
            HttpController(request).CURD_DELETE(models.SysRole, ids=ids)
        else:
            return utools.ApiJsonResult(code=1, msg="内置角色不允许删除")
        return utools.ApiJsonResult(msg="删除成功")

    @staticmethod
    @csrf_exempt
    @require_http_methods(['GET'])
    @modifiers.meta(title="查询角色权限")
    @modifiers.auth(forceLogin=True, authority="AdminUser:query_role_auth")
    def menu(request):
        roleId = request.GET.get('roleId')
        sysRole = models.SysRole.objects.get(role_id=roleId)
        authIds = list(sysRole.get_role_auth_ids())
        menuList = list(models.SysMenu.objects.all())
        data = []
        for item in menuList:
            row = item.toDict()
            if int(row['menu_id']) in authIds:
                row['checked'] = True
            else:
                row['checked'] = False
            data.append(row)
        return utools.ApiJsonResult(data=data, hump=True)

    @staticmethod
    @csrf_exempt
    @require_http_methods(['PUT'])
    @modifiers.meta(title="修改角色权限")
    @modifiers.auth(forceLogin=True, authority="AdminUser:set_role_auth")
    def saveMenu(request, role_id):
        SysRole = models.SysRole.objects.get(role_id=role_id)
        SysRole.del_role_auths(authIds='*')
        SysRole.set_role_auths(authIds=request.input())
        return utools.ApiJsonResult(msg="修改成功")


class Menu:
    @staticmethod
    @csrf_exempt
    @require_GET
    @modifiers.meta(title="菜单列表")
    @modifiers.auth(forceLogin=True)
    def list(request):
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 500))
        # 查询条件
        authority = request.GET.get('authority', '')
        title = request.GET.get('title', '')
        path = request.GET.get('path', None)
        SysMenu = models.SysMenu.objects
        if authority:
            SysMenu = SysMenu.filter(authority__contains=authority)
        if title:
            SysMenu = SysMenu.filter(title__contains=title)
        if path:
            SysMenu = SysMenu.filter(path__contains=path)

        p = Paginator(SysMenu.order_by('sort_number').all(), per_page=limit)
        count = p.count
        data = list(p.page(page))

        def d(item):
            item: models.SysMenu
            row = item.toDict()
            return row

        utools.each(d=d, s=data)

        return utools.ApiJsonResult(jsonData={'count': count, 'data': data}, hump=True)

    @staticmethod
    @csrf_exempt
    @require_http_methods(['PUT', 'POST', 'GET'])
    @modifiers.meta(title="")
    @modifiers.auth(forceLogin=True)
    def index(request):
        if request.method == 'GET':
            return Menu.list(request)
        data = utools.underline_dict(request.input())
        if request.method == 'POST':
            HttpController(request).CURD_SAVE(models.SysMenu(), data)
            return utools.ApiJsonResult(msg="保存成功")
        if request.method == 'PUT':
            menu_id = data['menu_id']
            del data['menu_id']
            SysMenu = models.SysMenu.objects.get(menu_id=menu_id)
            utools.object_set_attrs(SysMenu, data)
            SysMenu.save()
            return utools.ApiJsonResult(msg="修改成功")

    @staticmethod
    @csrf_exempt
    @require_http_methods(['DELETE'])
    @modifiers.meta(title="删除菜单")
    @modifiers.auth(forceLogin=True, authority="AdminUser:delete_menu")
    def delete(request, menu_id):
        if int(menu_id) in models.SysMenu.Attrs.prohibitDeleteIds:
            return utools.ApiJsonResult(code=1, msg="该菜单不允许删除")
        HttpController(request).CURD_DELETE(models.SysMenu, ids=[menu_id])
        return utools.ApiJsonResult(msg="删除成功")


class Organization:
    @staticmethod
    @csrf_exempt
    @require_GET
    @modifiers.meta(title="组织机构列表")
    @modifiers.auth(forceLogin=True)
    def list(request):
        # 查询条件
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 500))

        SysOrganization = models.SysOrganization.objects

        p = Paginator(SysOrganization.order_by('organization_id').all(), per_page=limit)
        count = p.count
        data = list(p.page(page))

        def d(item):
            item: models.SysOrganization
            row = item.toDict()
            return row

        utools.each(d=d, s=data)

        return utools.ApiJsonResult(jsonData={'count': count, 'data': data}, hump=True)

    @staticmethod
    @csrf_exempt
    @require_http_methods(['PUT', 'POST', 'GET'])
    @modifiers.meta(title="")
    @modifiers.auth(forceLogin=True)
    def index(request):
        if request.method == 'GET':
            return Organization.list(request)
        data = utools.underline_dict(request.input())
        if request.method == 'POST':
            HttpController(request).CURD_SAVE(models.SysOrganization(), data)
            return utools.ApiJsonResult(msg="保存成功")
        if request.method == 'PUT':
            organization_id = data['organization_id']
            del data['organization_id']
            SysMenu = models.SysOrganization.objects.get(organization_id=organization_id)
            utools.object_set_attrs(SysMenu, data)
            SysMenu.save()
            return utools.ApiJsonResult(msg="修改成功")

    @staticmethod
    @csrf_exempt
    @require_http_methods(['DELETE'])
    @modifiers.meta(title="删除机构")
    @modifiers.auth(forceLogin=True, authority="AdminUser:delete_organization")
    def delete(request, organization_id):
        HttpController(request).CURD_DELETE(models.SysOrganization, ids=[organization_id])
        return utools.ApiJsonResult(msg="删除成功")


class Dictdata:

    @staticmethod
    @csrf_exempt
    @require_GET
    @modifiers.meta(title="字典项列表")
    @modifiers.auth(forceLogin=True)
    def list(request):
        # 查询条件
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 500))
        dict_id = int(request.GET.get('dictId'))
        keywords = request.GET.get('keywords')

        dataModel = models.SysDictionaryData.objects.filter(dict_id=dict_id)
        if keywords:
            dataModel = dataModel.filter(dict_data_name__contains=keywords)

        p = Paginator(dataModel.order_by('sort_number').all(), per_page=limit)
        count = p.count
        data = list(p.page(page))

        def d(item):
            item: models.SysDictionaryData
            row = item.toDict()
            return row

        utools.each(d=d, s=data)

        return utools.ApiJsonResult(jsonData={'count': count, 'data': data}, hump=True)

    @staticmethod
    @csrf_exempt
    @require_http_methods(['PUT', 'POST', 'GET'])
    @modifiers.meta(title="")
    @modifiers.auth(forceLogin=True)
    def index(request):
        if request.method == 'GET':
            dictCode = request.GET.get('dictCode', '')
            ret = models.SysDictionary.get_data(dictCode)
            data = []
            for item in ret:
                item: models.SysDictionaryData
                data.append(item.toDict())
            return utools.ApiJsonResult(data=data, hump=type)
        data = utools.underline_dict(request.input())
        if request.method == 'POST':
            HttpController(request).CURD_SAVE(models.SysDictionaryData(), data)
            return utools.ApiJsonResult(msg="保存成功")
        if request.method == 'PUT':
            dict_data_id = data['dict_data_id']
            del data['dict_data_id']
            SysDictionaryData = models.SysDictionaryData.objects.get(dict_data_id=dict_data_id)
            utools.object_set_attrs(SysDictionaryData, data)
            SysDictionaryData.save()
            return utools.ApiJsonResult(msg="修改成功")

    @staticmethod
    @csrf_exempt
    @require_http_methods(['DELETE'])
    @modifiers.meta(title="删除字典")
    @modifiers.auth(forceLogin=True, authority="AdminUser:delete_dict_data")
    def delete(request, dict_data_id):
        HttpController(request).CURD_DELETE(models.SysDictionaryData, ids=[dict_data_id])
        return utools.ApiJsonResult(msg="删除成功")

    @staticmethod
    @csrf_exempt
    @require_http_methods(['DELETE'])
    @modifiers.meta(title="批量删除字典")
    @modifiers.auth(forceLogin=True, authority="AdminUser:delete_dict_data")
    def batch_delete(request):
        HttpController(request).CURD_DELETE(models.SysDictionaryData, ids=request.input())
        return utools.ApiJsonResult(msg="删除成功")


class Dict:
    @staticmethod
    @csrf_exempt
    @require_GET
    @modifiers.meta(title="字典列表")
    @modifiers.auth(forceLogin=True)
    def list(request):
        # 查询条件
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 500))

        SysDictionary = models.SysDictionary.objects

        p = Paginator(SysDictionary.order_by('-sort_number').all(), per_page=limit)
        count = p.count
        data = list(p.page(page))

        def d(item):
            item: models.SysDictionary
            row = item.toDict()
            return row

        utools.each(d=d, s=data)

        return utools.ApiJsonResult(jsonData={'count': count, 'data': data}, hump=True)

    @staticmethod
    @csrf_exempt
    @require_http_methods(['PUT', 'POST', 'GET'])
    @modifiers.meta(title="")
    @modifiers.auth(forceLogin=True)
    def index(request):
        if request.method == 'GET':
            return Dict.list(request)
        data = utools.underline_dict(request.input())
        if request.method == 'POST':
            HttpController(request).CURD_SAVE(models.SysDictionary(), data)
            return utools.ApiJsonResult(msg="保存成功")
        if request.method == 'PUT':
            dict_id = data['dict_id']
            del data['dict_id']
            SysDictionary = models.SysDictionary.objects.get(dict_id=dict_id)
            utools.object_set_attrs(SysDictionary, data)
            SysDictionary.save()
            return utools.ApiJsonResult(msg="修改成功")

    @staticmethod
    @csrf_exempt
    @require_http_methods(['DELETE'])
    @modifiers.meta(title="删除字典")
    @modifiers.auth(forceLogin=True, authority="AdminUser:delete_dict")
    def delete(request, dict_id):
        HttpController(request).CURD_DELETE(models.SysDictionary, ids=[dict_id])
        return utools.ApiJsonResult(msg="删除成功")


class loginRecord:
    @staticmethod
    @csrf_exempt
    @require_GET
    @modifiers.meta(title="登录日志")
    @modifiers.auth(forceLogin=True)
    def list(request):
        # 查询条件
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 500))
        # 查询条件
        username = request.GET.get('username', '')
        nickname = request.GET.get('nickname', '')
        createTimeStart = request.GET.get('createTimeStart', None)
        createTimeEnd = request.GET.get('createTimeEnd', None)
        SysLoginRecord = models.SysLoginRecord.objects
        if username:
            SysLoginRecord = SysLoginRecord.filter(username__contains=username)
        # if nickname:
        #     SysLoginRecord = SysLoginRecord.filter(nickname__contains=nickname)

        p = Paginator(SysLoginRecord.order_by('-id').all(), per_page=limit)
        count = p.count
        data = list(p.page(page))

        def d(item):
            item: models.SysLoginRecord
            row = item.toDict()
            return row

        utools.each(d=d, s=data)

        return utools.ApiJsonResult(jsonData={'count': count, 'data': data}, hump=True)


class operRecord:
    @staticmethod
    @csrf_exempt
    @require_GET
    @modifiers.meta(title="操作日志")
    @modifiers.auth(forceLogin=True)
    def list(request):
        # 查询条件
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 500))
        # 查询条件
        username = request.GET.get('username', '')
        nickname = request.GET.get('nickname', '')
        createTimeStart = request.GET.get('createTimeStart', None)
        createTimeEnd = request.GET.get('createTimeEnd', None)
        SysOperRecord = models.SysOperRecord.objects
        if username:
            SysOperRecord = SysOperRecord.filter(username__contains=username)
        # if nickname:
        #     SysOperRecord = SysOperRecord.filter(nickname__contains=nickname)

        p = Paginator(SysOperRecord.order_by('-id').all(), per_page=limit)
        count = p.count
        data = list(p.page(page))

        def d(item):
            item: models.SysLoginRecord
            row = item.toDict()
            return row

        utools.each(d=d, s=data)

        return utools.ApiJsonResult(jsonData={'count': count, 'data': data}, hump=True)


class Config(HttpController):
    def get_email_config(self):
        import EraAdmin.common as common

        print(common.sys_config_data('sysmailbox'))

        return utools.ApiJsonResult(jsonData={'count': 0, 'data': []}, hump=True)
