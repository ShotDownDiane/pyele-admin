from datetime import timedelta
import datetime as pyDateTime
from django.contrib import auth

import jwt
from django.db import models
from django.utils import timezone
from django.utils.datetime_safe import datetime
from django.contrib.auth.models import User
from django.db.models import signals
from django.dispatch import receiver
from . import settings
from . import utools
import hashids


class BaseModel(models.Model):
    # 将属性和属性值转换成dict列表生成式
    def toDict(self):
        dictData = dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]])
        for key in dictData:
            if type(dictData[key]) == pyDateTime.datetime:
                dictData[key] = pyDateTime.datetime.strftime(dictData[key], '%Y-%m-%d %H:%M:%S')
        return dictData

    class Meta:
        abstract = True
        pass

    class Attrs:
        abstract = True
        pass


class SysBaseModel(BaseModel):
    class Meta:
        abstract = True
        app_label = 'books'
        pass


class SysUser(SysBaseModel):
    user_id = models.AutoField(primary_key=True, help_text="用户ID")
    username = models.CharField(max_length=100, help_text="账号")
    password = models.CharField(max_length=200, help_text="密码")
    nickname = models.CharField(max_length=200, help_text="昵称")
    avatar = models.CharField(max_length=200, default=None, help_text="头像")
    sex = models.IntegerField(default=None, help_text="性别")
    phone = models.CharField(max_length=200, default=None, help_text="手机号")
    email = models.CharField(max_length=200, default=None, help_text="邮箱")
    email_verified = models.IntegerField(default='0', help_text="邮箱是否验证,0否,1是")
    true_name = models.CharField(max_length=200, default=None, help_text="真实姓名")
    id_card = models.CharField(max_length=200, default=None, help_text="身份证号")
    birthday = models.DateField(default=None, help_text="出生日期")
    introduction = models.CharField(max_length=200, default=None, help_text="个人简介")
    organization_id = models.IntegerField(default=None, help_text="机构id")
    state = models.IntegerField(default='0', help_text="状态,0正常,1冻结")
    deleted = models.IntegerField(default='0', help_text="是否删除,0否,1是")
    delete_time = models.DateTimeField(help_text="删除时间")
    create_time = models.DateTimeField(help_text="注册时间")
    update_time = models.DateTimeField(help_text="修改时间")

    class Meta:
        db_table = 'sys_user'

    class Attrs:
        pk = 'user_id'
        superIds = [1]

    @property
    def token(self):
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        token = jwt.encode({
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow(),
            'data': {
                'username': self.username,
                'userid': self.user_id
            }
        }, settings.SECRET_KEY, algorithm='HS256')
        return token

    def get_current_user_role_ids(self):
        roles = SysUserRole.objects.filter(user_id=self.user_id).all().values_list('role_id', flat=True)
        return roles

    def get_current_user_role(self):
        ids = self.get_current_user_role_ids()
        ret = SysRole.objects.filter(role_id__in=ids).all()
        roles = []
        for item in ret:
            item: SysRole
            roles.append(item.toDict())
        return roles

    def get_current_user_menu_ids(self):
        role_ids = self.get_current_user_role_ids()
        menus = SysRoleMenu.objects.filter(role_id__in=role_ids).values_list('menu_id', flat=True)

        return menus

    def get_current_user_menu(self):
        menu_ids = self.get_current_user_menu_ids()
        ret = SysMenu.objects.order_by("sort_number").filter(menu_id__in=menu_ids, menu_type=0).all()
        menus = []
        for item in ret:
            item: SysMenu
            menus.append(item.toDict())
        return menus

    def get_authorities(self):
        menu_ids = self.get_current_user_menu_ids()
        ret = SysMenu.objects.filter(menu_id__in=menu_ids, menu_type=1).all()
        auths = []
        for item in ret:
            item: SysMenu
            auths.append(item.toDict())
        return auths

    def del_user_roles(self, roleIds):
        if roleIds is None:
            return False
        if roleIds == '*':
            SysUserRole.objects.filter(user_id=self.user_id).delete()
        else:
            SysUserRole.objects.filter(user_id=self.user_id, role_id__in=roleIds).delete()
        return True

    def set_user_roles(self, roleIds):
        active_time = utools.get_current_time()
        dataSet = list()
        for x in range(0, len(roleIds)):
            dataSet.append(
                SysUserRole(user_id=self.user_id, role_id=roleIds[x], create_time=active_time,
                            update_time=active_time))
        SysUserRole.objects.bulk_create(dataSet)

    def getSexName(self):
        maps = ['', '男', '女']
        return maps[self.sex]

    @staticmethod
    def get_user_info(username):
        if username == 'admin':
            return SysUser.objects.get(user_id=1)
        else:
            hash_ = hashids.Hashids(salt=settings.SAFE_SALT, min_length=8)
            user_id = hash_.decode(username)[0]
            return SysUser.objects.get(user_id=user_id)

    def login(self, request):
        user = auth.authenticate(username=self.username, password='123456')
        if user is not None and user.is_active:
            auth.login(request, user)
            return True
        else:
            return False


class SysUserRole(SysBaseModel):
    id = models.AutoField(primary_key=True, help_text="主键id")
    user_id = models.IntegerField(help_text="用户id")
    role_id = models.IntegerField(help_text="角色id")
    create_time = models.DateTimeField(help_text="创建时间", default=timezone.now)
    update_time = models.DateTimeField(help_text="修改时间", auto_now=True)

    class Meta:
        db_table = 'sys_user_role'


class SysRole(SysBaseModel):
    role_id = models.AutoField(primary_key=True, help_text="角色id")
    role_name = models.CharField(max_length=200, help_text="角色名称")
    role_code = models.CharField(max_length=200, default=None, help_text="角色标识")
    comments = models.CharField(max_length=400, default=None, help_text="备注")
    deleted = models.IntegerField(default='0', help_text="是否删除,0否,1是")
    create_time = models.DateTimeField(help_text="创建时间", default=timezone.now)
    update_time = models.DateTimeField(help_text="修改时间", auto_now=True)

    class Meta:
        db_table = 'sys_role'

    class Attrs:
        pk = 'role_id'
        superIds = [1]

    def get_role_auth_ids(self):
        authIds = SysRoleMenu.objects.filter(role_id=self.role_id).all().values_list('menu_id', flat=True)
        return authIds

    def get_role_auth(self):
        authIds = self.get_role_auth_ids()
        ret = SysMenu.objects.filter(menu_id__in=authIds).all()
        authList = []
        for item in ret:
            item: SysMenu
            authList.append(item.toDict())
        return authList

    def del_role_auths(self, authIds):
        if authIds is None:
            return False
        if authIds == '*':
            SysRoleMenu.objects.filter(role_id=self.role_id).delete()
        else:
            SysRoleMenu.objects.filter(role_id=self.role_id, menu_id__in=authIds).delete()
        return True

    def set_role_auths(self, authIds):
        active_time = utools.get_current_time()
        dataSet = list()
        for x in range(0, len(authIds)):
            dataSet.append(
                SysRoleMenu(role_id=self.role_id, menu_id=authIds[x], create_time=active_time,
                            update_time=active_time))
        SysRoleMenu.objects.bulk_create(dataSet)


class SysRoleMenu(SysBaseModel):
    id = models.AutoField(primary_key=True, help_text="主键id")
    role_id = models.IntegerField(help_text="角色id")
    menu_id = models.IntegerField(help_text="菜单id")
    create_time = models.DateTimeField(help_text="创建时间", default=timezone.now)
    update_time = models.DateTimeField(help_text="修改时间", auto_now=True)

    class Meta:
        db_table = 'sys_role_menu'

    class Attrs:
        pk = 'menu_id'
        baseIds = []


class SysMenu(SysBaseModel):
    menu_id = models.AutoField(primary_key=True, help_text="菜单id")
    parent_id = models.IntegerField(default='0', help_text="上级id,0是顶级")
    title = models.CharField(max_length=200, help_text="菜单名称")
    icon = models.CharField(max_length=200, default='', help_text="菜单图标")
    path = models.CharField(max_length=200, default='', help_text="菜单路由关键字,目录为空")
    component = models.CharField(max_length=200, default='', help_text="菜单组件地址,目录为空")
    menu_type = models.IntegerField(default='0', help_text="类型,0菜单,1按钮")
    sort_number = models.IntegerField(default='0', help_text="排序号")
    authority = models.CharField(max_length=200, help_text="权限标识")
    target = models.CharField(max_length=200, default='_self', help_text="打开位置")
    color = models.CharField(max_length=200, help_text="图标颜色")
    uid = models.CharField(max_length=200, help_text="嵌套路由左侧选中")
    hide = models.IntegerField(default='0', help_text="是否隐藏,0否,1是(仅注册路由不显示左侧菜单)")
    deleted = models.IntegerField(default='0', help_text="是否删除,0否,1是")
    create_time = models.DateTimeField(help_text="创建时间", default=timezone.now)
    update_time = models.DateTimeField(help_text="修改时间", auto_now=True)

    class Meta:
        db_table = 'sys_menu'

    class Attrs:
        pk = 'menu_id'
        prohibitDeleteIds = []


class SysLoginRecord(SysBaseModel):
    id = models.AutoField(primary_key=True, help_text="主键id")
    username = models.CharField(max_length=200, help_text="用户账号")
    os = models.CharField(max_length=200, default='', help_text="操作系统")
    device = models.CharField(max_length=200, default='', help_text="设备名")
    browser = models.CharField(max_length=200, default='', help_text="浏览器类型")
    ip = models.CharField(max_length=200, default='', help_text="ip地址")
    oper_type = models.IntegerField(help_text="操作类型,0登录成功,1登录失败,2退出登录,3刷新token")
    comments = models.CharField(max_length=400, default='', help_text="备注")
    create_time = models.DateTimeField(help_text="创建时间", default=timezone.now)
    update_time = models.DateTimeField(help_text="修改时间", auto_now=True)

    class Meta:
        db_table = 'sys_login_record'

    class Attrs:
        pk = 'id'


class SysOrganization(SysBaseModel):
    organization_id = models.AutoField(primary_key=True, help_text="机构id")
    parent_id = models.IntegerField(default='0', help_text="上级id,0是顶级")
    organization_name = models.CharField(max_length=200, help_text="机构名称")
    organization_full_name = models.CharField(max_length=200, default='', help_text="机构全称")
    organization_code = models.CharField(max_length=200, default='', help_text="机构代码")
    organization_type = models.CharField(max_length=200, default='', help_text="机构类型")
    leader_id = models.IntegerField(default=None, help_text="负责人id")
    sort_number = models.IntegerField(default='1', help_text="排序号")
    comments = models.CharField(max_length=400, default=None, help_text="备注")
    deleted = models.IntegerField(default='0', help_text="是否删除,0否,1是")
    create_time = models.DateTimeField(help_text="创建时间", default=timezone.now)
    update_time = models.DateTimeField(help_text="修改时间", auto_now=True)

    class Meta:
        db_table = 'sys_organization'

    class Attrs:
        pk = 'organization_id'


class SysDictionary(SysBaseModel):
    dict_id = models.AutoField(primary_key=True, help_text="字典id")
    dict_code = models.CharField(max_length=100, help_text="字典标识")
    dict_name = models.CharField(max_length=200, help_text="字典名称")
    sort_number = models.IntegerField(default='1', help_text="排序号")
    comments = models.CharField(max_length=400, default=None, help_text="备注")
    deleted = models.IntegerField(default='0', help_text="是否删除,0否,1是")
    create_time = models.DateTimeField(help_text="创建时间", default=timezone.now)
    update_time = models.DateTimeField(help_text="修改时间", auto_now=True)

    class Meta:
        db_table = 'sys_dictionary'

    class Attrs:
        pk = 'dict_id'

    @staticmethod
    def get_data(dict_code):
        dictModel = SysDictionary.objects.get(dict_code=dict_code)
        return SysDictionaryData.objects.filter(dict_id=dictModel.dict_id).all()


class SysDictionaryData(SysBaseModel):
    dict_data_id = models.AutoField(primary_key=True, help_text="字典项id")
    dict_id = models.IntegerField(default='0', help_text="字典id")
    dict_data_code = models.CharField(max_length=100, help_text="字典项标识")
    dict_data_name = models.CharField(max_length=200, help_text="字典项名称")
    sort_number = models.IntegerField(default='1', help_text="排序号")
    comments = models.CharField(max_length=400, default=None, help_text="备注")
    deleted = models.IntegerField(default='0', help_text="是否删除,0否,1是")
    create_time = models.DateTimeField(help_text="创建时间", default=timezone.now)
    update_time = models.DateTimeField(help_text="修改时间", auto_now=True)

    class Meta:
        db_table = 'sys_dictionary_data'

    class Attrs:
        pk = 'dict_data_id'


class SysOperRecord(SysBaseModel):
    id = models.AutoField(primary_key=True, help_text="主键id")
    user_id = models.IntegerField(default=None, help_text="用户id")
    model = models.CharField(max_length=200, help_text="模块")
    description = models.CharField(max_length=200, help_text="方法")
    url = models.CharField(max_length=200, default='string', help_text="请求地址")
    request_method = models.CharField(max_length=200, default=None, help_text="请求方式")
    oper_method = models.CharField(max_length=200, default=None, help_text="调用方法")
    param = models.CharField(max_length=2000, default=None, help_text="请求参数")
    result = models.CharField(max_length=2000, default=None, help_text="返回结果")
    ip = models.CharField(max_length=200, default=None, help_text="ip地址")
    comments = models.CharField(max_length=2000, default=None, help_text="备注")
    spend_time = models.IntegerField(default=None, help_text="执行耗时,单位毫秒")
    state = models.IntegerField(default='0', help_text="状态,0成功,1异常")
    create_time = models.DateTimeField(help_text="创建时间", default=timezone.now)
    update_time = models.DateTimeField(help_text="修改时间", auto_now=True)

    class Meta:
        db_table = 'sys_oper_record'


@receiver(signals.post_save, sender=SysUser)
def sys_user_notify(instance, created, **kwargs):
    if created:
        # 随机生成账号
        # username = {''.join(random.choices(string.ascii_letters + string.digits, k=8)) for i in range(1)}.pop()
        hash_ = hashids.Hashids(salt=settings.SAFE_SALT, min_length=8)
        username = hash_.encode(instance.user_id)
        User.objects.create_user(username=username, password="era.123456")


@receiver(signals.post_delete, sender=SysUser)
def sys_user_notify(instance, **kwargs):
    hash_ = hashids.Hashids(salt=settings.SAFE_SALT, min_length=8)
    username = hash_.encode(instance.user_id)
    User.objects.filter(username=username).delete()
