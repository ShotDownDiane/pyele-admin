import time
import random
import string
from abc import ABCMeta, abstractmethod
from django_redis import get_redis_connection
import redis
from . import utools


class Task(metaclass=ABCMeta):
    # Task构造函数
    def __init__(self):
        self._class = self.__get_subclass_name__()
        self._pubdate = str(time.time())
        self._taskid = ''.join(random.sample(string.ascii_letters + string.digits, 15))

    # 批量设置对象属性
    def __setattrs__(self, data):
        for key, value in data.items():
            self.__setattr__(key, value)
        return self

    # 初始化构造
    @staticmethod
    def init(data):
        if '_class' not in data:
            return False
        return eval(data['_class'])(**data).__setattrs__(data)

    # 获取当前类名称
    def __get_subclass_name__(self):
        return self.__class__.__name__

    # 定义任务处理方法
    @abstractmethod
    def handle(self):
        pass

    # 定义任务异常处理方法
    @abstractmethod
    def exceptionHandle(self, e):
        pass

    # 推送到队列中
    def pushQueue(self, queue='task', lock_name=False):
        data = self.__dict__
        cache: redis.client.StrictRedis = get_redis_connection()
        if lock_name:
            if cache.sadd(queue + ":lock", lock_name) == 0:
                return [False, "任务已存在"]
            data['_lockname'] = lock_name
        try:
            cache.lpush(queue, utools.json_encode(data))
            return [True, "任务推送成功"]
        except BaseException as e:
            if lock_name:
                cache.srem(queue + ":lock", lock_name)
            return [False, e]

    @staticmethod
    def handleQueue(queue='task'):
        cache: redis.client.StrictRedis = get_redis_connection()
        data = cache.rpop(queue)
        if data is None:
            return None
        JsonData = utools.json_decode(data)
        task: Task = Task.init(JsonData)
        try:
            result = task.handle()
        except BaseException as e:
            print("[处理任务过程中抛出异常]: ", e)
            try:
                task.exceptionHandle(e)
            except BaseException as err:
                print("[通知给异常处理器时抛出错误]", err)
            finally:
                result = [False, e]
        finally:
            if '_lockname' in JsonData:
                cache.srem(queue + ":lock", JsonData['_lockname'])
        return [True, result]


class Test(Task):
    def exceptionHandle(self, e):
        print("任务出现异常")
        pass

    def handle(self):
        print("输出：", self.msg)
        pass

    msg = None

    def __init__(self, msg, **task):
        if not task:
            super(Test, self).__init__()
        self.msg = msg
