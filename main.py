# -*- coding: utf-8 -*-
'''
@Auther :liuyuqi.gov@msn.cn
@date :2019/4/8
'''
__author__ = "liuyuqi"

import json
import os,sys
import re
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing

import requests

import DownloadProgress
import user_agent


# src = "D:/PycharmProjects/crawl_xuexi/"
# os.chdir(src)


def get_video_links(url):
    video = requests.get(url=url, headers=user_agent.getheaders()).content.decode("utf8")
    pattern = r'https://video.xuexi.cn/[^,"]*mp4'
    link = re.findall(pattern, video, re.I)
    link.reverse()
    return link


def downloadVideo(url, file_name):
    '''
    下载视频
    :param url: 下载url路径
    :return: 文件
     '''
    with closing(requests.get(url=url, stream=True)) as response:
        chunk_size = 1024
        content_size = int(response.headers['content-length'])
        file_D = './Video/' + file_name + '.mp4'
        if (os.path.exists(file_D) and os.path.getsize(file_D) == content_size):
            print('跳过' + file_name)
        else:
            progress = DownloadProgress.DownloadProgress(file_name, total=content_size, unit="KB",
                                                         chunk_size=chunk_size,
                                                         run_status="正在下载", fin_status="下载完成")
            with open(file_D, "wb") as file:
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)
                    progress.refresh(count=len(data))


def crawl(url):
    lessonList = getLessonList(url)
    mlData = json.loads(lessonList)
    pool = ThreadPoolExecutor(max_workers=10)  # 创建一个最大可容纳10个task的线程池
    print("已配置10个线程下载")
    for i in range((len(mlData["fpe1ki18v228w00"]))):
        frst_name = mlData["fpe1ki18v228w00"][i]["frst_name"].replace('\t', ' ')
        static_page_url = mlData["fpe1ki18v228w00"][i]["static_page_url"]
        # 打开 mp4 视频网页链接
        resData = requests.get(static_page_url, headers=user_agent.getheaders()).content.decode("utf8")
        preUrl = static_page_url.split("/")[3]
        pattern = r'src="./data(.*?)"></script>'
        url = "https://www.xuexi.cn/" + preUrl + "/data" + re.findall(pattern, resData, re.I)[0]
        res = get_video_links(url)[0]
        print("已解析第 %s 个视频的下载地址：%s" % (i, res))
        future1 = pool.submit(downloadVideo,
                              res, frst_name)  # 往线程池里面加入一个task


def getLessonList(url):
    resData = requests.get(url=url, headers=user_agent.getheaders()).content.decode("utf8")
    print("已解析视频列表数据...")
    pattern = r'src="./data(.*?)"></script>'
    preUrl = url.split("/")[3]
    jsonUrl = "https://www.xuexi.cn/" + preUrl + "/data" + re.findall(pattern, resData, re.I)[0]
    resData2 = requests.get(url=jsonUrl, headers=user_agent.getheaders()).content.decode("utf8")
    print("已请求视频列表数据...")
    return resData2[14:-1]


if __name__ == '__main__':
    start_time = time.time()
    if not os.path.exists("Video"):
        os.mkdir("Video")
    url = input(
        "请输入“学习慕课”下面的免费课程链接：（eg：https://www.xuexi.cn/9f584b49d8a7386a4cf248ce16f5e667/9b0f04ec6509904be734f5f609a3604a.html）")
    crawl(url)
    print("last time: {} s".format(time.time() - start_time))
