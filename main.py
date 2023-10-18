# -*- coding: utf-8 -*-
'''
@Auther :liuyuqi.gov@msn.cn
@date :2019/4/8
'''
__author__ = "liuyuqi"

import time,os ,sys 
from crawl_xuexi import Xuexi

def banner():
    print("""
    _   _   _   _   _   _   _   _   _   _   _   _   _   _   _  
   / \ / \ / \ / \ / \ / \ / \ / \ / \ / \ / \ / \ / \ / \ / \ 
  ( X | u | e | x | i | . | c | n |   | v | i | d | e | o | s )
   \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ 
    """)
    print("Author: liuyuqi")

if __name__ == '__main__':
    banner()
    start_time = time.time()
    if not os.path.exists("Video"):
        os.mkdir("Video")
    if len(sys.argv) == 2:
        url = sys.argv[1]
    else:
        url = input(
            "请输入“学习慕课”下面的免费课程链接：（eg：https://www.xuexi.cn/9f584b49d8a7386a4cf248ce16f5e667/9b0f04ec6509904be734f5f609a3604a.html）")
    xuexi=Xuexi()
    xuexi.crawl(url)
    print("last time: {} s".format(time.time() - start_time))
