### 超星学习通自动播放学习视频✨
- 名称: `xuexitong.py`
- 用法:
  1. 安装谷歌浏览器
  2. 下载Chrome Driver, 版本为对应浏览器版本 [官方地址](http://chromedriver.storage.googleapis.com/index.html) | [淘宝镜像](http://npm.taobao.org/mirrors/chromedriver/)
  3. 更改 `xuexitong.py` 中的值:
     ```
     chrome_driver_path = '下载的chrome driver的路径'
     username = '学习通账号'
     password = '学习通密码'
     classname = '学习通课程名称(全称或一段连续名称)'
     limit = -1  # 最大观看页数, -1为不限
     ```
  4. 启动脚本 `python xuexitong.py`
- 注意:
  - 验证码需手动输入, 输入后等待自动登录
  - 此脚本基于Selenium完成, 完全模拟用户操作, 经测试无封号风险
  - 有时视频加载时间过长可能会跳过播放, 更换一个稳定的网络或重试即可
  - 若不幸有意外发生, 后果请自行承担
- 效果:
  - 支持未完成任务点定位, 自动切换视频
  - 支持最快倍速播放