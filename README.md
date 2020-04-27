# 一些有趣的Python爬虫实例🐛
平时制作(不断更新)的一些有趣的小爬虫，代码中含有丰富的中文注释。

#### 开始前
1. 确保安装所需库 `pip install -r requirements`
2. 确保稳定的网络连接
3. 此仓库仅用于参考交流学习

### Unsplash每日推荐美图🏞
- 名称: `unsplash.py`
- 用法: `python unsplash.py`
- 参数: 
```
--dst     -d   下载目录，默认当前目录
--width   -w   指定宽度像素，其高度自适应，默认1920px
--dpr     -p   设备像素比(1或2)，默认1
```
- 注意: 有时因为网络问题，会发生连接中断或长时间未响应

### 美团美食的店铺信息🍱
- 名称: `meituan.py`
- 用法: `python meituan.py`
- 参数:
```
--city    -c   所有符合此拼音首字母(A-Z)的城市，默认全部(*)
--food    -f   美食种类，默认全部(*)
--out     -o   将采集的信息以CSV格式保存至此目录，默认当前目录
```
- 注意:
  ```
  美食种类包括: 蛋糕甜点(c11), 火锅(c17), 自助餐(c40), 小吃快餐(c36), 日韩料理(c28), 西餐(c35), 烧烤(c54), 东北菜(c20003), 川湘菜(c55), 江浙菜(c56), 粤菜(c57), 西北菜(c58), 咖啡酒吧(c41), 云贵菜(c60), 东南亚菜(c62), 海鲜(c63), 台湾、客家菜(c227), 粥(c229), 蒙菜(c232), 新疆菜(c233), 京鲁菜(c59)
  保存CSV头部: name(店铺名称), avgScore(平均评分), avgPrice(平均消费), address(店铺地址), phone(店铺热线), openTime(营业时间), longitude(经度), latitude(维度), hasFoodSafeInfo(是否持有食品安全声明), 【可选】recommended(推荐菜品)
  ```
- 效果:
![meituan](./img/meituan.png)

### 知轩藏书查询下载📚
- 名称: `xiaoshuoGUI.py`
- 用法: `python xiaoshuoGUI.py`
- 注意: 下载方式为默认浏览器的下载工具
- 效果:
![xiaoshuo](./img/xiaoshuo.png)

### 超星学习通自动播放学习视频✨
- 名称: `xuexitong.py`
- 用法:
  - 安装谷歌浏览器
  - 下载Chrome Driver, 版本为对应浏览器版本 [官方地址](http://chromedriver.storage.googleapis.com/index.html) | [淘宝镜像](http://npm.taobao.org/mirrors/chromedriver/)
  - 更改 `xuexitong.py` 中的值:
  ```
    chrome_driver_path = '下载的chrome driver的路径'
    username = '学习通账号'
    password = '学习通密码'
    classname = '学习通课程名称(全称或一段连续名称)'
    limit = -1  # 最大观看页数, -1为不限
  ```
  - 启动脚本 `python xuexitong.py`
- 注意:
  - 此脚本基于Selenium完成, 完全模拟用户操作, 经测试无封号风险
  - 有时视频加载时间过长可能会跳过播放, 更换一个稳定的网络或重试即可
  - 若不幸有意外发生, 请自行承担

### 笔趣阁小说下载📚
- 名称: `BQxiaoshuo.py`
- 用法: `python BQxiaoshuo.py`
- 参数:
```
--yanshi  每章下载完后的延时，防止访问过快导致IP被封禁，默认为0(目前未遇到被封IP的情况)
--url     小说链接，代码中已给出示例
--num     线程数，默认为5，如需提高下载速度请自行更改
```
- 注意: 
  - 采用多线程逐章下载，适用于在网络上找不到整本的小说下载。
  - 适用于www.biqugg.com及类似页面结构的小说网站

#### 喜欢吗
- 😍 喜欢的话, 欢迎一起贡献
- 😍 喜欢的话, 点击一颗星星
- 😍 喜欢的话, 打赏一杯奶茶
![weixinzhifu](./img/vxqr.jpg)
