import threading
from queue import Queue
import requests
from bs4 import BeautifulSoup
import re

CRAW_EXIT = False #采集队列标识，如果为False，表示队列为空，页码全部被采集

#数据采集的线程类
class ThreadCrawl(threading.Thread):
    def _init_(self, threadName, pageQueue, dataQueue):
        threading.Thread._init_(self)
        self.threadName = threadName
        self.PageName = pageQueue
        self.dataQueue = dataQueue

        #请求头
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'}

    def run(self):
        print('启动' + self.threadName)
        while not CRAW_EXIT:
            try:
                page = self.pageQueue.get(False)
                url = 'http://book.zongheng.com/store/b0/c0/b0/u0/p{}/v0/s9/t0/u0/i1/ALL.html'.format(page)
                content = requests.get(url,headers=self.headers).content
                self.dataQueue.put(content)
            except  Exception:
                print('线程采集错误')
        print('结束：' + self.threadName)


PARSE_EXIT = False #解析队列表标识，如果为true，表示数据队列为空，全部数据解析完成
#线程解析类
class ThreadParse(threading.Thread):
    def _init_(self, threadName, dataQueue, books, lock):
        threading.Thread._init_(self)
        self.threadName = threadName
        self.dataQueue = dataQueue
        self.books = books
        self.lock = lock


    def run(self):
        print('启动：' + self.threadName)
        while not PARSE_EXIT:
            try:
                content = self.dataQueue.get(False)
                self.parse(content)
            except Exception:
                print('线程解析失败')
        print('结束' + self.threadName)


    def parse(self,content):
        
        soup = BeautifulSoup(content,'html5lib')
        store_collist = soup.find('div', class_='store_collist')
        pattern = re.compile(r'bookbox.f(.)')
        book_list = store_collist.find_all('div',class_=pattern)
        
        for item in book_list:
             book = {}
             book['img'] = item.find('div',class_='bokking').find('img')['src'] #图片
             book['name'] = item.find('div',class_='bookname').find('a').text
             book['intro'] = item.find('div',class_='bookintro').text #简介

             with self.lock:
                  self.books.append(book)

def main(pages):

    #页码队列
    pageQueue = Queue(pages)
    for i in range(1,pages + 1):
        pageQueue.put(i)
    
    #存放最终数据的列表
    books = []

    #数据队列，每项内容的是content，即采集类对象获取到的网页源码
    dataQueue = Queue()

    #线程互斥锁
    lock = threading.Lock()

    #采集线程的名字列表
    crawNames = ['采集1#','采集2#','采集3#','采集4#']
    
    #线程采集对象列表
    threadCrawls= []
    for threadName in crawNames:
        crawl = ThreadCrawl(threadName, pageQueue, dataQueue)#初始化采集线程对象
        crawl.start() #采集线程对象启动
        threadCrawls.append(crawl)

   
    #解析线程的名字列表
    parseNames = ['解析1#','解析2#','解析3#','解析4#']
    
    #线程解析对象列表
    ThreadParses = []
    for parseName in parseNames:
        parse = ThreadParse(parseName, dataQueue, books, lock)
        parse.start()
        ThreadParses.append(parse)
    
    while not pageQueue.empty():
        pass
    
    global CRAW_EXIT
    CRAW_EXIT = True
    print('页码队列为空')
    for thread in threadCrawls:
        thread.join() #子线程阻塞主线程，主线程等待子线程结束
    
    while not dataQueue.empty():
        pass

    global PARSE_EXIT
    PARSE_EXIT = True
    print('数据队列dataQueue为空')
    for thread in ThreadParses:
        thread.join()

    print(len(books),books[-1])

if __name__ == "__main__":
    try:
        pages = int(input('请输入要爬取多少页'))
    except Exception:
        print('请输入一个大于0的整数')

    main(pages)
            
