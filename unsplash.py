# -*- coding:utf-8 -*-
import argparse
import urllib.parse
from contextlib import closing
from collections import OrderedDict

import requests
import lxml.html
from tqdm import tqdm


etree = lxml.html.etree

URL = 'https://unsplash.com/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}


def parse_query(element):
    # 解析query
    odict = OrderedDict()
    link = element.xpath('@srcset')[0].split(',')[0].strip()[:-3]
    base, queries = urllib.parse.splitquery(link)
    for query in queries.split('&'):
        k, v = query.split('=')
        if k != 'h':
            odict[k] = v
    return base, odict


def download(element, dst, width, dpr):
    base, odict = parse_query(element)
    if int(odict['w']) >= width:
        odict['w'] = f'{width}'
    odict['dpr'] = f'{dpr}'
    download_url = base + '?' + '&'.join(f'{k}={v}' for k, v in odict.items())

    # 开始下载
    print('start downloading image from unsplash.')
    # print(download_url)
    with closing(requests.get(download_url, headers=headers, stream=True)) as resp:
        chunk_size = 1024
        content_size = int(resp.headers['content-length'])
        with open(dst + str(hex(id(resp))) + '.jpg', 'wb') as file:
            for data in tqdm(resp.iter_content(chunk_size=chunk_size), total=round(content_size//chunk_size)):
                file.write(data)


def parse_unsplash(dst, width, dpr):
    response = requests.get(URL, headers=headers)

    html = etree.HTML(response.content)
    # 获取 Photos of the Day 封面图片
    route = html.xpath('//div[@data-test="editorial-route"]')[0]
    div1 = route.xpath('div')[0]
    div2 = div1.xpath('div')[0]
    div3 = div2.xpath('div')[0]
    pics = div3.xpath('picture')[0]
    sources = pics.xpath('source')
    download(sources[0], dst, width, dpr)
    print('done!')


def parse_args():
    parser = argparse.ArgumentParser()
    # 下载路径
    parser.add_argument('--dst', '-d',
                        default='./', help='download path')
    # 宽, 高度自适应
    parser.add_argument('--width', '-w',
                        default='1920', help='image width pixel')
    # 设备像素比
    parser.add_argument('--dpr', '-p',
                        default='1', help='device pixel ratio - (1x, 2x)')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    dst = args.dst
    dpr = int(args.dpr)
    width = int(args.width)
    assert dpr in (1, 2)
    assert width >= 50
    parse_unsplash(dst, width, dpr)
