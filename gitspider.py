# coding = utf-8

import requests
from lxml import html

LOGIN_URL = 'https://github.com/login'
SESSION_URL = 'https://github.com/session'

s = requests.session()
r = s.get(LOGIN_URL)

#获取浏览器返回的HTML文本
tree = html.fromstring(r.text)
# 利用lxml中的xpath 获取有用的待提交的data信息
el = tree.xpath('//input[@name="authenticity_token"]')[0]

authenticity_token = el.attrib['value']

# 构建数据信息
data = {
    'commit': 'Sign in',
    'utf8': '✓',
    'authenticity_token': authenticity_token,
    'login': '734190426@qq.com',
    'password': '734190426l'
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36'
}

r = s.post(SESSION_URL, data=data, headers=headers)
#print(r.text)
tree = html.fromstring(r.text)
print(tree)
el = tree.xpath('//ul[@class="mini-repo-list"]')[0]
print(el)
