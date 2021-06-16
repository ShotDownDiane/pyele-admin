""" 路由 """
import types
from django.http import Http404
from EraAdmin.app import AppRequest
from EraAdmin.utools import md5, jsonMerge
from django.urls import re_path, path
from functools import partial
import importlib


class RuleItem:
    def __init__(self, _rule, _route, method='*', kwargs=None, name=None):
        self.rule = _rule
        self.route = _route
        self.method = method
        if kwargs is None:
            kwargs = {}
        self.kwargs = kwargs
        self.name = name

    def getPath(self):
        ruleKey = self.getRuleKey()
        # 保存路由
        ruleList[ruleKey] = self
        # 注册路由映射
        self.setRuleMap(ruleKey)
        return re_path(
            route=self.rule,
            view=RouteHandle.dispatch,
            kwargs={
                "ruleKey": ruleKey
            },
            name=self.name
        )
        pass

    def setRuleMap(self, key):
        method = self.method
        if method == '*':
            for i in ruleMap:
                ruleMap[i].append(key)
            return True
        elif type(method) == str:
            method = [method]
        for i in range(len(method)):
            ruleMap[method[i]].append(key)
        return True

    def getRuleKey(self):
        return md5(self.rule)
        pass


ruleList = {}
ruleMap = {
    'GET': [],
    'POST': [],
    'DELETE': [],
    'PUT': []
}


class RouteHandle:
    def __init__(self):
        pass

    @staticmethod
    def dispatch(request, ruleKey, **kwargs):

        appRequest = AppRequest(request=request)
        if ruleKey not in ruleList:
            return Http404("没有找到路由")

        ruleObj: RuleItem = ruleList[ruleKey]

        if request.method in ruleMap:
            if ruleKey not in ruleMap[request.method]:
                raise Http404("请求类型不正确, 仅支持 " + ', '.join(ruleObj.method) + ' 类型的请求')

        kwargs = jsonMerge([kwargs, ruleObj.kwargs])
        route = ruleObj.route
        if type(route) == str:
            try:
                appName, appPath = route.split('@')
                a = appPath.split('.')
                action = a.pop()
                controller = a.pop()
                a.insert(0, 'module')
                r = importlib.import_module(appName + '.' + '.'.join(a))
                if not hasattr(r, controller):
                    raise Http404("控制器%s不存在" % controller)
                Object = getattr(r, controller)(appRequest)
                if not hasattr(Object, action):
                    raise Http404("方法%s不存在" % action)
                actionObject = getattr(Object, action)
                return actionObject(**kwargs)
            except ImportError as e:
                print("[RouteHandle] ImportError", e)
                raise Exception("模块载入错误: " + str(e))
        elif isinstance(ruleObj.route, types.FunctionType):
            return ruleObj.route(appRequest, **kwargs)
        pass


def rule(rulePath, route, method='*', kwargs=None, name=None):
    return RuleItem(rulePath, route, method, kwargs, name).getPath()


get = partial(rule, method=['GET'])

post = partial(rule, method=['POST'])

put = partial(rule, method=['PUT'])

delete = partial(rule, method=['DELETE'])


class APP:
    def __init__(self, name):
        self.name = name

    def path(self, path):
        return self.name + '@' + path
