# -*- coding: utf-8 -*-
import csv
import time
import json
import random
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}


class EastMoney:

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('prefs', {'profile.managed_default_content_settings.images': 2})
        self.browser = webdriver.Chrome(executable_path=chrome_driver_path, options=options)
        self.wait = WebDriverWait(self.browser, timeout=5)

        self.page = 1  # 页面值
        self.csv_head = [['公司名称', '姓名', '性别', '学历', '年龄', '任职时间', '职务', '个人简介']]

    def collect(self):
        """ 遍历并收集公司列表 """
        index_url = 'http://data.eastmoney.com/gstc/'
        self.browser.get(index_url)
        # self.write_to_csv(self.csv_head)
        self.wait.until(ec.presence_of_element_located((By.ID, 'PageNav')))
        # self.jump_page(self.page)
        # time.sleep(3.0)

        while 1:
            # 等待全部信息显示完成
            self.wait.until(ec.presence_of_element_located((By.ID, 'td_1')))
            firms = self.browser.find_elements_by_css_selector('#td_1 > tbody > tr')
            print(f'当前页面:{self.page}, 共{len(firms)}个记录.')

            self.collect_firm_info(firms)
            # 切换至下一页
            if not self.next_page():
                break
            time.sleep(3.0)

    def collect_firm_info(self, firms: list):
        """ 遍历当前页面公司的记录 """
        collect = []
        for firm in firms:
            id_, firm_info = firm.find_elements_by_tag_name('td')[:2]
            firm_name, stock_code = firm_info.find_elements_by_tag_name('a')
            print(f'序号:{id_.text:<5} 名称:{firm_name.text:<10} 代码:{stock_code.text:<6}')

            # 获取完整股票代码, 包括: 前缀 + 数字代码
            full_stock_code = stock_code.get_attribute('href').split('/')[-1][:-5]
            rows = self.collect_management_info(firm_name.text, full_stock_code.upper())
            collect += rows
            time.sleep(3.0)
        # 收集后一并写入csv
        self.write_to_csv(collect)

    def collect_management_info(self, firm_name: str, stock_code: str) -> list:
        """ 利用request获取公司管理层人员信息 """
        proxy_ip = random.choice(proxies)[:-1]
        proxy_ip = {
            'https': 'https://' + proxy_ip  # 或 使用HTTP
        }

        url = f'http://f10.eastmoney.com/CompanyManagement/CompanyManagementAjax?code={stock_code}'
        resp = requests.get(url, headers=headers, proxies=proxy_ip)
        data = json.loads(resp.content.decode('utf-8'))['RptManagerList']

        collect = []
        for p in data:
            row = [firm_name, p['xm'], p['xb'], p['xl'], p['nl'], p['rzsj'], p['zw'], p['jj'].replace('\n', '')]
            collect.append(row)

        print(f'[-]共获取{len(data)}条记录, 成功收集{len(collect)}条.\n')
        return collect

    def next_page(self) -> bool:
        self.page += 1
        page = self.wait.until(ec.presence_of_element_located((By.ID, 'PageCont')))
        next_page = page.find_elements_by_tag_name('a')[-2]
        if next_page.get_attribute('class') == 'nolink':
            # 最后一页
            return False
        else:
            self.browser.execute_script('arguments[0].click();', next_page)
            return True

    def jump_page(self, page_nbr: int):
        """ 跳转至某一页面, 程序中断时可使用 """
        page = self.wait.until(ec.presence_of_element_located((By.ID, 'PageCont')))
        nbr = self.browser.find_element_by_id('PageContgopage')
        nbr.clear()
        nbr.send_keys(page_nbr)
        jump = page.find_elements_by_tag_name('a')[-1]
        self.browser.execute_script('arguments[0].click();', jump)

    def write_to_csv(self, rows: list):
        """ 信息写入本地CSV格式文件 """
        with open('data.csv', 'a', encoding='utf-8') as f:
            csv_file = csv.writer(f)
            csv_file.writerows(rows)


if __name__ == '__main__':
    chrome_driver_path = '/Users/shawnhu/Documents/chromedriver'
    proxies = []  # 配置IP代理池

    em = EastMoney()
    em.collect()
