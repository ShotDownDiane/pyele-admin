# pyeleadmin

一个Python后台的eleadmin后台管理模板

# elaeadmin

##### EleAdminPro使用Vue3、AntDesignVue，适合前后端分离的项目， 使用当前主流的前端技术栈：Webpack、NPM、Vue、VueX、VueRouter、VueCLI、Axios、Less等， 是工程化、模块化、组件化的前端框架。


# 技术栈
##### 环境组件
```
# pip install Django
# pip install pymysql
# pip install requests_html
# pip install django-oauth-toolkit==1.2.0
# pip install django-simple-captcha
# pip install pyjwt
# pip install django-cors-headers
# pip install django-redis
# 创建超级管理员 python manage.py createsuperuser
```

# 目录结构
```
apps  应用列表
├─application           应用目录（可设置）
│  ├─templates          模板目录
│  ├─module             模块目录
│  │  ├─views.py        模块视图文件
│  ├─admin.php          django-admin
│  ├─apps.php           应用注册
│  ├─config.php         应用配置
│  ├─tests.php          应用测试
│  ├─urls.php           路由配置
│  ├─views.php          应用视图
│  └─models.php         应用模型
├─static                WEB部署目录（对外访问目录）
│  ├─common             公共静态目录
├─EraAdmin              框架系统目录
│  ├─middleware         中间件
│  ├─management         命令行
│  ├─models             应用模型
│  ├─modifiers          修饰器库
│  ├─oauth.php          oauth库
│  ├─task.php           任务库
│  ├─common.php         公共库
│  └─utools.php         工具库
```

##### django 后台地址 http://127.0.0.1:8100/django-admin/
##### pyeleadmin 后台地址 http://127.0.0.1:8100/pyele-admin/


##### 预览图

![Image](http://era.didili.cn/dist/images/1.png)

![Image](http://era.didili.cn/dist/images/2.png)

![Image](http://era.didili.cn/dist/images/3.png)