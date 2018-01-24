# 头脑王者

免责声明：仅供研究使用，请勿进行非法用途。

头脑王者开房答题抓题库, 参考项目 [lyh2668/TNWZ](https://github.com/lyh2668/TNWZ)，实现
Pyhton版本的头脑王者抓题目，暂时不支持排位自动答题。

## 环境要求

- Python 3+
- mongodb

## 安装和使用

以下过程为 macOS 和 iPhone 下，其他环境为未测试。

0. 安装环境

```sh
# mongodb
brew install mongodb
mongod

# clone项目
git clone https://github.com/qiwihui/tnwz.git
cd tnwz

# 安装依赖
pip3 install -r requirements.txt

# 填写两个用户的uid和token

```

1. 先获取题库（可直接导入本项目题库）

```sh
# 模拟开房对战
python3 tnwz.py

# 导出题库
# mongoexport --db tnwzDB --collection Quizzes --out Quizzes.json

# 或者使用项目自带题库
mongoimport --db tnwzDB --collection Quizzes --file Quizzes_20180121.json
```

2. 答题

**需要手机和电脑上安装并信任证书**

```sh
mitmweb -s tnwz_hack.py --web-iface 0.0.0.0 --port 8001
```

手机上设置代理为电脑的ip和8001端口，同时进入头脑王者答题时要出现登录过程才可以，否则会报错。

答题时随机选择答案即可，程序会修改为题库中正确的答案。
