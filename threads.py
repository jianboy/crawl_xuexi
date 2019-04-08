# -*- coding: utf-8 -*-
'''
多线程下载多文件;多线程分段下载单文件.
@Auther :liuyuqi.gov@msn.cn
@date :2019/4/8
'''
__author__ = "liuyuqi"

from threading import Lock
from threading import Thread

threadLock = Lock()
threads = []


class MyThread(Thread):
    def __init__(self, name, func, *args, lock=False):
        Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
        self.lock = lock

    def run(self):
        print("开启： " + self.name)
        if self.lock:
            threadLock.acquire()
            self.func(*self.args)
            threadLock.release()
        else:
            self.func(*self.args)
