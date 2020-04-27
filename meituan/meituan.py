# -*- coding:utf-8 -*-
import os
import csv
import time
import json
import argparse

import requests
from tqdm import tqdm
from lxml.html import etree


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
csv_headers = ['name', 'avgScore', 'avgPrice', 'address', 'phone', 'openTime', 'longitude', 'latitude', 'hasFoodSafeInfo']


def get_cities(city_cap):
    city_url = 'https://www.meituan.com/changecity/'
    response = requests.get(city_url, headers=headers)
    html = etree.HTML(response.content)
    # 寻找城市标签
    if city_cap == '*':
        cities = html.xpath('//span[@class="cities"]/a')
    else:
        areas = html.xpath(f'//div[@class="city-area" and @id="city-{city_cap.upper()}"]')[0]
        cities = areas.xpath('./span[@class="cities"]/a')
    print(f"以拼音首字母'{city_cap.upper()}'开头的共有{len(cities)}个城市.")
    # 生成每个城市的名称和网站链接
    for city in cities:
        name = city.xpath('./text()')[0]
        href = city.xpath('@href')[0]
        yield name, href


def parse_meituan_infos(html, key):
    # 美团的美食网页与店铺网页存放信息的位置一样，都在JS代码的深处
    # 经验上, 该信息节点放在倒数第二个
    node: str = html.xpath('//script/text()')[-2]
    # 剔除JS代码部分即得到JSON可解析的部分
    node = node.lstrip('window._appState = ').rstrip(';')
    node_json = json.loads(node)
    # 返回需要的键值部分
    return node_json.get(key)


def get_shop_infos(shop_url) -> list:
    # 采集的信息包括:
    # 店铺名称  平均评分   人均消费   地址       电话    营业时间     经度         维度        是否有食品安全档案
    # name     avgScore  avgPrice  address   phone   openTime   longitude    latitude   hasFoodSafeInfo
    # 返回csv的一行数据
    response = requests.get(shop_url, headers=headers)
    html = etree.HTML(response.content)
    # parse_meituan_infos(html, 'recommended')  此键存储店铺的推荐菜品
    infos = parse_meituan_infos(html, 'detailInfo')

    return [infos['name'], infos['avgScore'], infos['avgPrice'],
            infos['address'], infos['phone'], infos['openTime'],
            infos['longitude'], infos['latitude'], infos['hasFoodSafeInfo']]


def parse_meituan_food(city_cap, food_type, dst):
    # 美团针对不同城市有不同的网址
    for city_name, city_url in get_cities(city_cap):
        # 一个城市对应一个csv,先写入头部
        with open(os.path.join(dst, city_name + '.csv'), 'w') as file:
            csv_file = csv.writer(file)
            csv_file.writerow(csv_headers)
        # 记录当前店铺数
        cur_count = 0
        # 记录当前页数
        cur_page = 1
        while True:
            # 用于收集数据行
            lines = []
            # 针对不同的美食种类有不同的链接
            base_url = f'https:{city_url}/meishi/'
            page_url = base_url + f'{food_type + "/" if food_type != "*" else ""}' + f'pn{cur_page}/'
            response = requests.get(page_url, headers=headers)
            html = etree.HTML(response.content)
            # 键'poiLists'存放了当前页面中所有店铺的基本信息
            infos = parse_meituan_infos(html, 'poiLists')
            print(f'正在采集第{cur_page}页内容...')
            if infos is None:
                print('解析出错, 不存在键值"poiLists"')
                return
            else:
                total = int(infos['totalCounts'])
                shops = infos['poiInfos']
                # 获取每个店铺的信息
                for shop in tqdm(shops, total=len(shops)):
                    line = get_shop_infos(f'{base_url}{shop["poiId"]}/')
                    lines.append(line)
                    time.sleep(2.0)
                # 当累计店面数量达到总数时停止
                cur_count += len(shops)
                print(f"当前城市:{city_name:4}, 当前页数:{cur_page:<3}, 当前店铺:{cur_count:<5}/{total:5}")
                if cur_count == total:
                    break
                else:
                    cur_page += 1
            # 每更新一个页面写入一次数据
            with open(os.path.join(dst, city_name + '.csv'), 'a') as file:
                csv_file = csv.writer(file)
                csv_file.writerows(lines)
            # 休眠
            time.sleep(2.0)
        time.sleep(3.0)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--city', '-c',
                        default='*', help='所有符合此拼音首字母的城市，默认全部')
    parser.add_argument('--food', '-f',
                        default='*', help='美食种类，默认全部')
    parser.add_argument('--out', '-o',
                        default='./', help='将采集的信息(CSV)保存至此目录，默认当前目录')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    city = args.city
    food = args.food
    out = args.out

    assert len(city) == 1 and city.lower() in '*abcdefghijklmnopqrstuvwxyz'
    # 美食种类(参数代码):
    # 蛋糕甜点(c11), 火锅(c17), 自助餐(c40), 小吃快餐(c36), 日韩料理(c28),
    # 西餐(c35), 烧烤(c54), 东北菜(c20003), 川湘菜(c55), 江浙菜(c56), 粤菜(c57),
    # 西北菜(c58), 咖啡酒吧(c41), 云贵菜(c60), 东南亚菜(c62), 海鲜(c63), 台湾、客家菜(c227),
    # 粥(c229), 蒙菜(c232), 新疆菜(c233), 京鲁菜(c59)
    assert food in ('c11', 'c17', 'c40', 'c36', 'c28', 'c35', 'c54', 'c20003', 'c55', 'c56', 'c57'
                    'c58', 'c41', 'c60', 'c62', 'c63', 'c227', 'c229', 'c232', 'c233', 'c59', '*')

    parse_meituan_food(city, food, out)
