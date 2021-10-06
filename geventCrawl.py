from _typeshed import Self
from threading import main_thread
from gevent.hub import MAIN_THREAD_IDENT
import requests
from queue import Queue
from bs4 import BeautifulSoup
import re
import time
import gevent

class Spider:
    def __init__(self):
        self.headers ={'user-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36'
}
        #基准网址
        self.base_url = 'https://search.51job.com/list/000000,000000,0000,00,9,99,java,2,'+str()+'.html'
        #数据队列
        self.dataQueue = Queue()
        #统计数量
        #self.count = 0
        #数据列表
        self.jobs = []

    #获取一页数据的方法
    def get_page_job(self, url):
        content = requests.get(url, headers=self.headers).content

        #d对页面数据进行解析
        soup = BeautifulSoup(content,'html5lib')#将解析的文档放在soup变量里

        jobs_list = soup.find('div',class_='leftbox')#找到那个新闻所在的div
        pattern = re.complie(r'j_(.)')
        joblist_box = jobs_list.find_all('div',class_='pattern')

        jobs = []
        for joblist in joblist_box:
            job = {}
            job['name'] = joblist.find('div',class_='e').find('span')
            job['address'] = joblist.find('div',class_='e').find('span').find('p').text
            jobs.append[job]
            Self.dataQueue.put(job)

    def start_work(self,pageNum):
        job_list = []
        for page in range(1, pageNum+1):
            url = self.base_url.format(page)
            #创建携程任务
            job = gevent.spawn(self.get_page_jobs, url)
            #把所有协程任务加入任务列表
            job_list.append(job)

        #等待所有协程执行完毕
        gevent.joinall(job_list)

        while not self.dataQueue.empty():
            book = self.dataQueue.get()
            self.news.append(job)

if __name__ =="__main__":
    pages = int(input('请输入页码:'))
    t1 = time.time()
    spider = Spider()
    spider.start_work(pages)
    print(len(spider.jobs))
    t2 = time.time()
    print(t2 - t1)
