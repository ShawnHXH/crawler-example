# -*- coding:utf-8 -*-
import time
import math

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException


class XueXiTong:

    def __init__(self):
        options = webdriver.ChromeOptions()
        # 设置为开发者模式, 防止被网站识别出来使用了selenium
        options.add_experimental_option('excludeSwitches', ['enable-automation'])

        self.browser = webdriver.Chrome(executable_path=chrome_driver_path, options=options)
        self.wait = WebDriverWait(self.browser, timeout=10)  # 超时时长为10s

    def login(self):
        """ 登录学习通(超星) """
        login_url = 'http://passport2.chaoxing.com/login?fid=&refer=http://i.mooc.chaoxing.com'
        self.browser.get(login_url)
        # 等待账号输入框出现 输入账号
        xxt_user = self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'zl_input')))
        xxt_user.send_keys(username)
        # 等待密码输入框出现 输入密码
        xxt_pwd = self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'zl_input2')))
        xxt_pwd.send_keys(password)
        # 等待验证码图像出现 (手动)输入验证码
        xxt_code = self.wait.until(ec.presence_of_element_located((By.ID, 'numcode')))
        xxt_code.click()
        # 等待登录按钮出现 点击登录
        submit = self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, '.zl_btn > .zl_btn_right')))
        timeout = 9  # 拥有输入验证码的时间
        for i in range(timeout):
            js = f'document.getElementsByTagName("h2")[0].innerHTML="请输入验证码, {timeout-i}秒后自动登录"'
            self.browser.execute_script(js)
            time.sleep(1.0)
        submit.click()
        # 获取登录后的信息
        name = self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, '#space_nickname > .personalName')))
        print('登录成功, 欢迎', name.get_attribute('title'))

    def study(self):
        """ 自动延续播放学习通视频 """
        self.open_class()
        self.open_lesson()
        cur_count = 0
        pre_title = ''
        cur_page = 1
        while True:
            # 记录当前位置
            cur_title = self.find_title()
            if pre_title == cur_title:
                cur_page += 1
            else:
                pre_title = cur_title
                cur_page = 1
            print('当前页面:', cur_title, cur_page)
            # 寻找学习任务
            cur_count += (1 if self.traverse() else 0)
            if not self.next_page():
                print('课程全部结束!')
                break
            if limit != -1 and cur_count == limit:
                print('此次任务结束!')
                break
            time.sleep(1.5)

    def open_class(self):
        """ 定位并打开课程 """
        # 等待所有元素加载完成
        self.wait.until(ec.presence_of_all_elements_located)
        self.browser.switch_to.frame('frame_content')
        # 定位课程名称
        classes = self.browser.find_elements_by_css_selector('.Mconright.httpsClass > .clearfix > a')
        for cls in classes:
            name = cls.get_attribute('title')
            if classname in name or classname == name:
                print('课程定位成功:', name)
                # 如果直接使用click, url则不会更新
                self.browser.get(cls.get_attribute('href'))
                break

    def open_lesson(self):
        """ 定位到并打开未学习的课程 """
        timeline = self.wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'timeline')))
        # 由icon元素确定该节是否学习
        lessons = timeline.find_elements_by_class_name('icon')
        # 找到一节未学习的课程, 已做选择优化
        enter_point = None
        enter_point_url = None
        distance = 0
        threshold = 3
        for lesson in lessons:
            tag = lesson.find_element_by_tag_name('em').get_attribute('class')
            if tag == 'orange':
                if enter_point is None or distance > threshold:
                    enter_point = lesson
                    distance = 0
                else:
                    root = enter_point.find_element_by_xpath('.//..')  # 章节根节点
                    link = root.find_element_by_css_selector('.articlename > a')  # 章节链接
                    cnum = root.find_element_by_class_name('chapterNumber')  # 章节数
                    print('未完成章节定位成功:', cnum.text, link.get_attribute('title'))
                    enter_point_url = link.get_attribute('href')
                    break
            else:
                distance += 1
        if enter_point_url is not None:
            self.browser.get(enter_point_url)
        else:
            print('没有待完成课程, 即将结束任务...')
            exit(-1)

    def next_page(self) -> bool:
        """ 切换到下一页, 返回是否有下一页 """
        # 定位'下一页'按钮
        next_buttons = self.browser.find_elements_by_css_selector('#mainid.main > .tabtags > .orientationright')
        if len(next_buttons) == 1:
            # 页面拥有一个'下一页'按钮时, 就是唯一的按钮
            next_button = next_buttons[0]
        else:
            # 页面拥有许多'下一页'按钮时, 但只有 style="display: block" 的才显示.
            next_button = list(filter(lambda btn: 'display: block' in btn.get_attribute('style'), next_buttons))[0]
        # 判断是否为最后一个按钮
        if 'gray' in next_button.get_attribute('class'):
            return False
        # 此按钮没有链接, 而是直接为JS代码(onclick).
        self.browser.execute_script(next_button.get_attribute('onclick'))
        # 等待元素更新
        self.browser.implicitly_wait(1.0)
        return True

    def find_title(self):
        """ 寻找当前页面的标题 """
        title = self.browser.find_element_by_css_selector('#mainid.main > h1')
        return title.text

    def traverse(self) -> bool:
        """ 遍历学习任务结点, 返回是否学习完成 """
        status = True
        # 每一个页面都拥有一个iframe元素
        self.browser.switch_to.frame('iframe')
        self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'div.ans-cc')))
        try:
            # 寻找未完成的任务结点
            nodes = self.browser.find_elements_by_xpath('//div[@class="ans-attach-ct"]')
            for i, node in enumerate(nodes, start=1):
                # 拥有此class的iframe元素表示视频
                frame = node.find_element_by_css_selector('iframe.ans-attach-online.ans-insertvideo-online')
                self.play_video(frame, i)
        except NoSuchElementException:
            status = False
        finally:
            # 退出到最外层页面
            self.browser.switch_to.default_content()
            return status

    def play_video(self, video_frame, video_id):
        """ 播放视频型学习任务结点 """
        self.browser.switch_to.frame(video_frame)
        print('[*] 准备播放第', video_id, '个视频')
        video = self.browser.find_element_by_id('video')
        video.click()
        # 等待视频加载完全后, 重新获取元素
        self.wait.until(lambda web: web.find_element_by_class_name('vjs-duration-display').text != '0:00')
        video = self.browser.find_element_by_id('video')
        # 设置播放选项, 得到剩余播放时间
        rest = self.play_video_settings(video, max_speed=True)
        print('[*] 播放预计在', rest, 's 后完成...')
        time.sleep(rest)
        # 退出当前iframe
        self.browser.switch_to.parent_frame()
        print('[*] 播放完成, 3s后自动切换...')
        time.sleep(3.0)

    def play_video_settings(self, video, max_speed: bool = True):
        """ 设置播放视频选项, 返回视频播放的剩余时间 """
        speed = 1.0  # 默认视频倍速
        if max_speed:
            speed_btn = video.find_element_by_class_name('vjs-playback-rate')
            speeds = video.find_elements_by_css_selector('.vjs-playback-rate > .vjs-menu > '
                                                         '.vjs-menu-content  > .vjs-menu-item')
            # 视频倍速有: 1x 1.25x 1.5x 2x
            boost = 0.125
            for _ in range(len(speeds)-1):
                speed_btn.click()
                boost *= 2
                speed = 1.0 + boost
        all_time = video.find_element_by_class_name('vjs-duration-display').text
        cur_time = video.find_element_by_class_name('vjs-current-time-display').text
        res_time = self.time_to_seconds(all_time) - self.time_to_seconds(cur_time)
        return math.ceil(res_time / speed)

    @classmethod
    def time_to_seconds(cls, time_str: str) -> float:
        """ 将 h:m:s 形式的时间转换为秒 """
        seconds = [(int(t) if t else 0) * 60.0 ** i
                   for i, t in enumerate(time_str.split(':')[::-1])]
        return sum(seconds)


if __name__ == '__main__':
    chrome_driver_path = 'chromedriver的路径'
    username = '学习通账号'
    password = '学习通密码'
    classname = '学习通课程名称(全称或一段连续名称)'
    limit = -1  # 最大观看页数, -1为不限

    xxt = XueXiTong()
    xxt.login()
    xxt.study()
