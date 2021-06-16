import threading
import time

from django.core.management.base import BaseCommand
from django.core.cache import cache
import EraAdmin.task as task
# 设置彩色字体
import os

if os.name == "nt":
    os.system("")


class Command(BaseCommand):
    QueueList = ['task']

    @staticmethod
    def queueHandle(jtqIndex, queueName):
        jtqName = "监听器: J" + jtqIndex
        print('\033[0;33;40m[%s] 已启动\033[0m' % jtqName, "队列名称：" + queueName + ";")
        checkTime = int(time.time())
        while True:
            try:
                result = task.Task.handleQueue(queue=queueName)
                # 如果没有获取到队列任务，则休眠0.1秒
                if result is None:
                    time.sleep(0.1)
                    continue
                actTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                print('\033[0;34;40m[%s]\033[0m' % jtqName, "%s, 已处理完一个任务" % str(actTime), result)
            except KeyboardInterrupt:
                print('\033[0;31;40m[%s]\033[0m' % jtqName, "已终止监听")
                break
            except BaseException as e:
                print('\033[0;31;40m[%s]\033[0m' % jtqName, "运行出现异常", e)
                # 如果监听器出现异常，则休眠0.5秒
                time.sleep(0.5)
            finally:
                # 每隔20秒检测一次终止命令
                if checkTime + 20 < int(time.time()):
                    checkTime = int(time.time())
                    if cache.get("task_run_state") is None:
                        print('\033[0;31;40m[%s]\033[0m' % jtqName, "收到终止命令,已停止任务处理...")
                        break

    def handle(self, *args, **options):
        # 设置全局状态
        cache.set("task_run_state", 1, timeout=None)
        print('\033[0;32;40m------[PyTask]-------\033[0m')
        print('\033[0;32;40m[Task主进程]\033[0m', "开始执行...")
        startTime = int(time.time())
        threading_list = []
        # 创建子线程
        for i in range(0, len(self.QueueList)):
            p1 = threading.Thread(target=self.queueHandle, args=(str(i + 1), self.QueueList[i],))
            p1.setDaemon(True)
            threading_list.append(p1)
            p1.start()
        print('\033[0;32;40m[Task主进程]\033[0m', "正在监听任务...")
        try:
            # 监听子线程结束
            while True:
                pass
            # for i in range(0, len(self.QueueList)):
            #     threading_list[i].join()
        except KeyboardInterrupt as e:
            print('\033[0;32;40m[Task主进程]\033[0m', "已终止监听...")
        endTime = int(time.time())
        runTime = endTime - startTime
        print('\033[0;32;40m[Task主进程]\033[0m', "执行结束,本次运行了%.2f秒" % runTime)
