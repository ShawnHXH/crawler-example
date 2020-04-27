import requests
import lxml
from bs4 import BeautifulSoup
import re
import time
import threading

l = []      #url-list
count = 0   #线程总数
t = []      #线程
nr = []     #内容
ls = []     #临时
tit = ""    #标题
yanshi = 0  #每章下载完毕后的延时

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0'}

#获取章节链接
def get_urls(url):
    global ls,tit
    a = requests.get(url=url,headers=headers)
    bs = BeautifulSoup(a.content,'lxml')
    print(a.status_code)
    tit = bs.h1.string.strip() + ".txt"

    num = 0
    urls = bs.findAll("a",{"style":"","href":re.compile("^\d+\.html$")})   #找到所有章杰的urls
    for url in urls:        #前12个移除，因为是最新的

        # if num < 12:
        #     num = num + 1
        # else:
        #     ls.append(str(url["href"]))         #章节urls 加入到 ls 列表中
        
        ls.append(str(url["href"]))           #如果页面开始前12章不是最新的，可以将30-33行注释掉。35行取消注释。

    print("章节urls获取成功:")
    print(ls[0],ls[1])

#url拼接
def download_urls(url):
    global l
    for line in ls:
        l.append(url + line)
    print("url拼接成功:")
    print(l[0],l[1])

#内容list的长度
def nr_len():
    global nr
    a = len(l)
    while a > 0:
        nr.append("")
        a = a - 1
    print("nr长度定义成功")

#下载
def down(url,num,no):   #url=章节链接  num=线程数  no=第几个线程
    global nr
    a = requests.get(url=url,headers=headers)
    bs = BeautifulSoup(a.content,'lxml')
    b = bs.find_all('div',id="content") 
    text = "\n\n" + bs.h1.string + "\n\n" + str(b[0]).replace('<br/>','\n')[20:-162:]   #内容分割，头部切掉20个字符，尾部切掉162个字符  此处自行计算
    nr[int(num)] = text
    print("第" + num + "章下载完成")
    num = int(num) + count
    try:
        nr[num] = ''
        t[int(no)] = threading.Thread(target=down, args=(l[num],str(num),no))
        t[int(no)].start()
        # print("线程" + no +"传递出去了")
        time.sleep(yanshi)  #延时
    except IndexError:
        print("线程" + no + "结束运行")

#起点
def xc(num):
    global t,count
    count = num
    i = 0
    while num > 0 :
        num = num - 1
        t.append("")
        t[i] = threading.Thread(target=down, args=(l[i],str(i),str(i)))
        t[i].start()
        print("线程" + str(i) + "启动")
        i = i + 1

def main(url,ci):

    get_urls(url)       #得到所有章节的url
    download_urls(url)  #拼接
    nr_len()            #内容list的长度
    xc(ci)              #线程

    xunhuan = True
    while xunhuan:
        time.sleep(1)
        p = 0
        huozhe = 0
        while p < count:
            if t[p].isAlive() == False:
                p = p + 1
            else:
                huozhe = 1
        if huozhe == 0:
            dn = open(tit,'w',encoding='utf-8')
            for line in nr:
                dn.write(line)
            dn.close()
            input("下载完成\n按任意键退出")
            xunhuan = False
        elif huozhe == 1:
            print("正在下载")

yanshi = 0  #延时
main("https://www.biqugg.com/xs/1/",5)

#   注释
#   27 行为正则表达式，可自行更改以适应不同的网站。
#   63 行为对页面抓取到的小说内容进行裁剪，切去头部和尾部h5代码，可自行更改以适应不同的网站。

#   使用方法   
#   延时 yanshi 默认为 0 ,未防止被网站ban掉IP，请自行更改延时，虽然不改也没什么事就对了。
#   main("网址",使用线程数)