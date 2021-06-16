import hashlib
import json
import os
import random
import re
import shutil
import string
import time
import types
from collections import ChainMap
from datetime import datetime
import pytz
import requests
from django.shortcuts import HttpResponse
from django.http import JsonResponse, HttpResponseRedirect
from urllib.parse import urlencode
from django.shortcuts import render


def md5(s):
    my_md5 = hashlib.md5()
    my_md5.update(s.encode("utf8"))
    return my_md5.hexdigest()


def jsonMerge(json_array):
    return dict(ChainMap(*json_array))


def ApiJsonResult(code=0, msg="", data=None, jsonData=None, hump=False):
    if jsonData is None:
        jsonData = {}
    result = jsonMerge([jsonData, {"code": code, "msg": msg, "data": data}])
    if hump:
        result = camel_dict(result)
    return JsonResponse(result)


def redirect(url, params=None):
    if type(params) == list:
        redirect_url = url + urlencode(params)
    else:
        redirect_url = url
    return HttpResponseRedirect(redirect_url)


def HtmlResult(content):
    return HttpResponse(content)


def view(request, tpl, data=None):
    return render(request, tpl, data)


def template(tpl, app=None):
    root = os.getcwd()
    if app:
        tpl = os.path.join(root, "apps", app, "templates", tpl)
    else:
        tpl = os.path.join(root, "templates", tpl)

    content = ''
    with open(tpl,mode='r', encoding='utf-8') as file_obj:
        for line in file_obj:
            content += line
    return HtmlResult(content)


def json_encode(data):
    """ json对象转json字符串
    """
    return json.dumps(data)


def json_decode(s):
    """ 字符串转json对象
    """
    return json.loads(s)


def utc_to_local(utc_time_str, utc_format='%Y-%m-%dT%H:%M:%S.%fZ'):
    """ utc时间转换
    """
    local_tz = pytz.timezone('Asia/Shanghai')
    local_format = "%Y-%m-%d %H:%M:%S"
    utc_dt = datetime.strptime(utc_time_str, utc_format)
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    time_str = local_dt.strftime(local_format)
    return datetime.fromtimestamp(int(time.mktime(time.strptime(time_str, local_format))))


def http_request(url):
    return requests.get(url, stream=True)


def download(url, save_path):
    res = requests.get(url, stream=True)
    if res.status_code == 200:
        # 判断文件是否存在
        if not os.path.exists(save_path):
            dir_path = os.path.dirname(save_path)
            # 判断目录是否存在
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            # 创建文件
            f = open(save_path, 'wb')
            f.write(res.content)
            f.close()
            return save_path
    return False


def moveFile(srcfile, dstfile):
    if not os.path.isfile(srcfile):
        return False
    else:
        fpath, fname = os.path.split(dstfile)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        shutil.move(srcfile, dstfile)
        return dstfile


def copyFile(srcfile, dstfile):
    if not os.path.isfile(srcfile):
        return False
    else:
        fpath, fname = os.path.split(dstfile)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        shutil.copyfile(srcfile, dstfile)
        return dstfile


def convert_path(path: str) -> str:
    return path.replace(r'\/'.replace(os.sep, ''), os.sep)


def hump2underline(hunp_str):
    p = re.compile(r'([a-z]|\d)([A-Z])')
    sub = re.sub(p, r'\1_\2', hunp_str).lower()
    return sub


def underline2hump(underline_str):
    sub = re.sub(r'(_\w)', lambda x: x.group(1)[1].upper(), underline_str)
    return sub


def underline_dict(params):
    new_params = params
    if isinstance(params, dict):
        new_params = {}
        for k, v in params.items():
            new_params[hump2underline(k)] = underline_dict(params[k])
    elif isinstance(params, list):
        new_params = []
        for param in params:
            new_params.append(underline_dict(param))
    return new_params


def camel_dict(params):
    new_params = params
    if isinstance(params, dict):
        new_params = {}
        for k, v in params.items():
            new_params[underline2hump(k)] = camel_dict(params[k])
    elif isinstance(params, list):
        new_params = []
        for param in params:
            new_params.append(camel_dict(param))
    return new_params


def each(d, s):
    i = 0
    for item in s:
        s[i] = d(item)
        i = i + 1
    return s


def object_set_attrs(obj, params, attrs=None):
    if type(attrs) == list:
        for value in params:
            if value in attrs:
                obj.__setattr__(value, params[value])
    else:
        for value in params:
            obj.__setattr__(value, params[value])
    return obj


def generate_tree(source, id="id", pid="pid", child="children", parent=0):
    tree = []
    for item in source:
        if item[pid] == parent:
            item[child] = generate_tree(source, id, pid, child, item[id])
            tree.append(item)
    return tree


def get_current_time(formats="%Y-%m-%d %H:%M:%S"):
    return datetime.now().strftime(formats)


def array_filter(data, filters=None):
    if type(filters) == list:
        data = filter(lambda id: id not in filters, data)
    if isinstance(filters, types.FunctionType):
        data = filter(filters, data)
    return data


def get_random_str(length=8):
    return ''.join(random.sample(string.ascii_letters + string.digits, length))
