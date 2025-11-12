#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Contact :   liuyuqi.gov@msn.cn
@Time    :   2019/4/8
@License :   Copyright © 2017-2022 liuyuqi. All Rights Reserved.
@Desc    :   main xuexi
'''
import re,json,requests,os
from concurrent.futures import ThreadPoolExecutor
from . import DownloadProgress
from contextlib import closing
from urllib.parse import urlparse, parse_qs

class Xuexi(object):
    ''' xuexi class '''
    
    def __init__(self):
        self.sess= requests.Session()

    def get_video_links(self,url:str) -> list[str]:
        ''' get video links '''
        video = self.sess.get(url=url).content.decode("utf8")
        pattern = r'https://video.xuexi.cn/[^,"]*mp4'
        link = re.findall(pattern, video, re.I)
        link.reverse()
        return link

    def download(self,url:str, file_name:str, type:str = "mp4"):
        ''' download video
         :param url: download url path
          :return: file
         '''
        headers = {
            "Sec-Fetch-Dest": "video",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
            "Referer": "https://www.xuexi.cn/"
        }
        with closing(self.sess.get(url=url, stream=True, headers=headers)) as response:
            chunk_size = 1024
            content_size = int(response.headers['content-length'])
            if type == "mp4":
                file_D = './Video/' + file_name + '.mp4'
            else:
                file_D = './Video/' + file_name + '.mp3'
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
        
    def crawl(self, url:str):
        ''' crawl '''
        pool = ThreadPoolExecutor(max_workers=10)  # 创建一个最大可容纳10个task的线程池
        if (url.startswith("https://www.xuexi.cn/lgpage/detail/index.html")):
            lessonList = self.getLessonListByLgPage(url)
            mlData = json.loads(lessonList)
            for i in range(len(mlData["sub_items"])):
                frst_name = mlData["sub_items"][i]["title"].replace(" ", "")
                # find video
                try:
                    for j in range(len(mlData["sub_items"][i]["videos"][0]["video_storage_info"])):
                        res = mlData["sub_items"][i]["videos"][0]["video_storage_info"][j]["normal"]
                        if ".mp4" in res:
                            break
                    pool.submit(self.download, res, frst_name)
                except Exception as e:
                    pass

                # find voice
                try:
                    for j in range(len(mlData["sub_items"][i]["audios"][0]["audio_storage_info"])):
                        res2 = mlData["sub_items"][i]["audios"][0]["audio_storage_info"][j]["url"]
                        if ".mp3" in res2:
                            break
                    pool.submit(self.download, res2, frst_name, "mp3")
                except Exception as e:
                    pass
        else:
            lessonList = self.getLessonList(url)
            mlData = json.loads(lessonList)
            print("已配置10个线程下载")
            for i in range((len(mlData["fpe1ki18v228w00"]))):
                frst_name = mlData["fpe1ki18v228w00"][i]["frst_name"].replace(
                    '\t', ' ')
                static_page_url = mlData["fpe1ki18v228w00"][i]["static_page_url"]
                # 打开 mp4 视频网页链接
                resData = self.sess.get(static_page_url).content.decode("utf8")
                preUrl = static_page_url.split("/")[3]
                pattern = r'src="./data(.*?)"></script>'
                url = "https://www.xuexi.cn/" + preUrl + \
                    "/data" + re.findall(pattern, resData, re.I)[0]
                res = self.get_video_links(url)[0]
                print("已解析第 %s 个视频的下载地址：%s" % (i, res))
                pool.submit(self.download, res, frst_name)  # 往线程池里面加入一个task
    
    def getLessonListByLgPage(self, url):
        '''
        针对新格式 url 解析视频
         https://www.xuexi.cn/lgpage/detail/index.html?id=3645649255073663875
        '''
        # get  the id from url
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        lesson_id = query_params.get('id', None)[0]
        newUrl = r"https://boot-source.xuexi.cn/data/app/" + lesson_id + ".js"
        resData = self.sess.get(url=newUrl).content.decode("utf8")
        print("已解析视频列表数据...")
        return resData[9:-1]

    def getLessonList(self, url):
        resData = self.sess.get(url=url).content.decode("utf8")
        print("已解析视频列表数据...")
        pattern = r'src="./data(.*?)"></script>'
        preUrl = url.split("/")[3]
        jsonUrl = "https://www.xuexi.cn/" + preUrl + \
            "/data" + re.findall(pattern, resData, re.I)[0]
        resData2 = self.sess.get(url=jsonUrl).content.decode("utf8")
        print("已请求视频列表数据...")
        return resData2[14:-1]