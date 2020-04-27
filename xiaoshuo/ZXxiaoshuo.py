import re
import sys

from PyQt5.QtWidgets import QWidget, QDesktopWidget, QApplication, QPushButton, QLineEdit, QListWidget, QLabel
from PyQt5.QtGui import QIcon, QCursor, QPalette, QBrush, QPixmap
from PyQt5.QtCore import QCoreApplication, Qt, QThread
from bs4 import BeautifulSoup
from requests import get
import webbrowser


zd = {}

URL = 'http://www.zxcs.info/index.php?keyword='

headers = {
    "Host": "www.zxcs.info",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

Dict = {}


def get_list(name):
    global Dict
    names = []
    lists = []
    urlx = URL + name
    a = get(url=urlx, headers=headers)
    bs = BeautifulSoup(a.text, "lxml")
    for div in bs.find_all('dl', id='plist'):
        urls = div.findAll("a", {
            "href": re.compile(r"http://www\.zxcs\.info/post/.....")
        })
        try:
            lists.append(str(urls[0]['href']))
            names.append(str(urls[0].string))
            Dict[str(urls[0].string)] = str(urls[0]['href'])
        except IndexError:
            pass
    return Dict


def download(url):
    a = get(url=url, headers=headers)
    bs = BeautifulSoup(a.text, 'lxml')
    for div in bs.find_all('div', class_='filecont'):
        urlx = div.findAll('a', {
            "target": "_blank",
            "title": "",
            "href": re.compile(r"/download\.php\?id=.....")
        })
        down_url = "http://www.zxcs.info" + urlx[0]['href']

    b = get(url=down_url, headers=headers)
    soup = BeautifulSoup(b.text, 'lxml')
    for d in soup.find_all('div', class_='panel-body'):
        f_url = d.findAll('a', {
            "target": "_blank",
            "href": re.compile(r"http://www\.zxcsdbweb\.xyz/upload.*")
        })
        try:
            du = (f_url[0]['href'])
        except IndexError:
            pass
    return du


class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()           # 界面绘制交给InitUi方法
        super(Example, self).__init__()

    def initUI(self):
        self.resize(500, 450)                       # 主窗口大小 宽*高
        self.setMinimumSize(500, 450)
        self.setMaximumSize(500, 450)
        self.setWindowFlag(Qt.FramelessWindowHint)  # 取消边框
        self.setWindowOpacity(0.9)                  # 设置透明度
        self.center()                               # 主窗口位置 居中
        self.setWindowTitle('小说下载')              # 标题
        self.setWindowIcon(QIcon('Icon/002.png'))   # Icon图标

        self.tb = QLineEdit(self)       # 搜索框
        self.tb.resize(300, 30)
        self.tb.move(30, 30)

        self.lab = QLabel("test")
        self.lab.move(65, 100)

        bt1 = QPushButton("搜索", self)  # 搜索按钮
        bt1.resize(60, 30)
        bt1.move(340, 30)

        bt2 = QPushButton("下载", self)  # 下载按钮
        bt2.resize(60, 30)
        bt2.move(410, 30)

        bt3 = QPushButton("×", self)     # 关闭
        bt3.resize(20, 20)
        bt3.move(480, 0)

        self.lb = QListWidget(self)
        self.lb.resize(440, 330)
        self.lb.move(30, 90)

        bt1.clicked.connect(self.get_list)
        bt2.clicked.connect(self.download)
        bt3.clicked.connect(QCoreApplication.instance().quit)

        self.tb.setStyleSheet(
            "QLineEdit{border:0px}"
            "QLineEdit{background-color:#f9f9f9}"
            "QLineEdit{border-radius:3px}"
            # "QLineEdit:hover{box-shadow:2px 2px 3px #999999;}"
        )

        self.lb.setStyleSheet(
            "QListWidget{border:0px}"
            "QListWidget{background-color:#f9f9f9}"
            "QListWidget{border-radius:3px}"
        )

        bt1.setStyleSheet(
            "QPushButton{border:0px}"
            "QPushButton{background-color:#9f9f9f}"
            "QPushButton{border-radius:3px}"
            "QPushButton:hover{background-color:#999}"
        )

        bt2.setStyleSheet(
            "QPushButton{border:0px}"
            "QPushButton{background-color:#9f9f9f}"
            "QPushButton{border-radius:3px}"
            "QPushButton:hover{background-color:#999}"
        )

        bt3.setStyleSheet(
            "QPushButton{background-color:#F0F0F0}"
            "QPushButton:hover{background-color:#9f9f9f}"
            "QPushButton:hover{color:#f9f9f9}"
            "QPushButton{border:0px}"
            "QPushButton:hover{border-radius:10px}"
        )

        self.show()

    def get_list(self):
        global zd
        name = self.tb.text()
        self.tb.clear()
        zd = get_list(name)
        for n in zd.keys():
            self.lb.addItem(n)

    def download(self):
        a = self.lb.selectedItems()
        for i in a:             # 获取的a是个list
            # self.lb.addItem(zd[i.text()])
            u = download(zd[i.text()])
            self.tb.clear()
            # self.tb.setText(u)
            # xiaoshuo.down(u,i.text()) # 下载
            webbrowser.open(u)  # 网页打开

    def center(self):       # 控制窗口显示在屏幕中心的方法
        qr = self.frameGeometry()                           # 获得窗口
        cp = QDesktopWidget().availableGeometry().center()  # 获得屏幕中心点
        qr.moveCenter(cp)                                   # 显示到屏幕中心
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()            # 获取鼠标相对窗口的位置
            event.accept()
            # self.setCursor(QCursor(Qt.OpenHandCursor)) # 更改鼠标图标
    
    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.m_flag:
            self.move(event.globalPos() - self.m_Position)      # 更改窗口位置
            event.accept()
    
    def mouseReleaseEvent(self, event):
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
