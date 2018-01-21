# 头脑王者

免责声明：仅供研究使用，请勿进行非法用途。

头脑王者开房答题抓题库, 参考项目 [lyh2668/TNWZ](https://github.com/lyh2668/TNWZ)，实现
Pyhton版本的头脑王者抓题目，暂时不支持排位自动答题。

## 环境要求

- Python 3+
- mongodb

## 安装和使用

macOS

```sh
# mongodb
brew install mongodb
mongod

# clone项目
git clone https://github.com/qiwihui/tnwz.git
cd tnwz

# 安装依赖
pip install -r requirements.txt

# 填写两个用户的uid和token

# 模拟开房对战
python3 tnwz.py
```