import re
import lxml
from bs4 import BeautifulSoup
from requests import get

url = 'http://www.zxcs.info/index.php?keyword='

headers = {
    "Host": "www.zxcs.info",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

zd = {}

def get_list(name):
    global zd
    names = []
    lists = []
    urlx = url + name
    a = get(url=urlx,headers=headers)
    bs = BeautifulSoup(a.text, "lxml")
    for div in bs.find_all('dl',id='plist'):
        urls = div.findAll("a",{"href":re.compile("http\:\/\/www\.zxcs\.info\/post\/.....")})
        try:
            lists.append(str(urls[0]['href']))
            names.append(str(urls[0].string))
            zd[str(urls[0].string)] = str(urls[0]['href'])
        except IndexError:
            pass
    return zd

def download(url):
    a = get(url=url,headers=headers)
    bs = BeautifulSoup(a.text, 'lxml')
    for div in bs.find_all('div',class_='filecont'):
        urlx = div.findAll('a',{"target":"_blank","title":"","href":re.compile("\/download\.php\?id\=.....")})
        down_url = "http://www.zxcs.info" + urlx[0]['href']

    b = get(url=down_url,headers=headers)
    soup = BeautifulSoup(b.text, 'lxml')
    for d in soup.find_all('div',class_='panel-body'):
        f_url = d.findAll('a',{"target":"_blank","href":re.compile("http\:\/\/www\.zxcsdbweb\.xyz\/upload.*")})
        try:
            du = (f_url[0]['href'])
        except IndexError:
            pass
    return du


###下面是旧版下载方法，由于传输问题，总是下载失败
def down(url,name):
    headers = {
        "Host": "www.zxcsdbweb.xyz",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    file_download = get(url,timeout=20,headers=headers,stream=True)
    fp = open(name + ".zip",'wb')
    for chunk in file_download.iter_content(chunk_size=1024):   #边下载边存硬盘
        fp.write(chunk)
    fp.close()
    print("下载完了")


