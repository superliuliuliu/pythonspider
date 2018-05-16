# coding = utf-8
"""
weibo 的模拟登陆功能实现
实现了获取最热话题的内容 以及该话题的讨论量
获取最新的6条微博的发送方  微博内容  以及该微博的当前点赞数
"""
import requests
import rsa
import json
import re
import binascii
import urllib
import urllib.parse
import base64
import http.cookiejar
import urllib.request
from bs4 import BeautifulSoup

"""登陆"""
LOGIN_PRE = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_=1525409261135'
LOGIN = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
session = requests.session()


class Launcher:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    # 对用户名进行加密
    def get_encrypted_name(self):
        username_url = urllib.parse.quote(self.username)
        username_encrypted = base64.b64encode(bytes(username_url, encoding='utf-8'))
        return username_encrypted.decode('utf-8')

    # 获取原始数据  nonce servertime pub_key
    def get_pre_login_info(self):
        response = session.get(LOGIN_PRE)
        json_data = re.findall(r'(?<=\().*(?=\))', response.text)[0]
        data_raw = json.loads(json_data)
        return data_raw

    # 对用户密码进行加密   rsa加密
    def get_encrypted_pw(self, data):
        rsaPublickey = int(data['pubkey'], 16)
        key = rsa.PublicKey(rsaPublickey, 65537)
        message = str(data['servertime'])+'\t'+str(data['nonce'])+'\n'+str(self.password)
        sp = binascii.b2a_hex(rsa.encrypt(message.encode(encoding="utf-8"), key))
        return sp

    # 创建浏览器向服务器提交的数据表单
    def create_post_data(self, data):
        post_data = {
            "entry": "weibo",
            "gateway": "1",
            "from": "",
            "savestate": "7",
            "useticket": "1",
            "pagerefer": "https://www.baidu.com/link?url=QyLggbqlJR3jrGL3UzhtBv0UZfrvbrQZiX08Qc30B7O&wd=&eqid=98aa3c4300097588000000035aed9deb",
            "vsnf": "1",
            "su": self.get_encrypted_name(),
            "service": "miniblog",
            "servertime": data['servertime'],
            "nonce": data['nonce'],
            "pwencode": "rsa2",
            "rsakv": data['rsakv'],
            "sp": self.get_encrypted_pw(data=data),
            "sr": "1360*768",
            "encoding": "UTF-8",
            "url": "http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
            "returntype": "META"
        }
        data = urllib.parse.urlencode(post_data).encode('utf-8')
        return data

    # 保存cookie
    def enableCookies(self):
        cookie_container = http.cookiejar.CookieJar()
        cookie_support = urllib.request.HTTPCookieProcessor(cookie_container)
        opener = urllib.request.build_opener(cookie_support, urllib.request.HTTPHandler)
        urllib.request.install_opener(opener)

        # 得到微博热门主题的信息
    def gethotinfo(self, final):
        scriptcontent = re.findall(r'<script>(.*?)<\/script>', final)
        for i, item in enumerate(scriptcontent):
            if i == 2:
                usenamescript = item
            elif i == 16:
                hotmessage = item
        data_user = json.loads(usenamescript[8:-1])
        tree = data_user['html']
        soup = BeautifulSoup(tree, 'lxml')
        username = soup.find(name='em', attrs={'class': 'W_ficon ficon_user S_ficon'}).nextSibling
        print(u"欢迎%s, 登陆lgy编写微博模拟程序!" % username.text)
        data_hot = json.loads(hotmessage[8:-1])
        hot_html = data_hot['html']
        soup2 = BeautifulSoup(hot_html, 'lxml')
        hotmessagenumber = soup2.find_all(name='span', attrs={'class': 'total S_txt2'})
        hotmessageinfo = soup2.find_all(name='a', attrs={'class': 'S_txt1', 'target': '_blank'})
        print('----------------------------------------------------')
        print(u"热门话题   阅读量")
        for i in range(0, 8):
            print(hotmessageinfo[i + 1].text, hotmessagenumber[i].text)

    # 得到模拟登陆账号上的好友发布的五条最新微博  并按照一定的格式输出
    def getweiboinfo(self, final):
        scriptcontent = re.findall(r'<script>(.*?)<\/script>', final)
        for i, item in enumerate(scriptcontent):
            if i == 10:
                weiboinfo = item
        weiboinfojson = json.loads(weiboinfo[8:-1])
        weiboinfohtml = weiboinfojson['html']
        print('----------------------------------------------------')
        print(u"输出最新微博的发布者    发布内容 ")
        soup = BeautifulSoup(weiboinfohtml, 'lxml')
        sender = soup.find_all(name='div', attrs={'class': 'WB_info'})
        agreenumber = soup.find_all(name='em', attrs={'class':'W_ficon ficon_praised S_txt2'})
        content = soup.find_all(name='div', attrs={'class':'WB_text W_f14'})
        print(u"微博实时更新（最新6条")
        for i in range(0,6):
            print(u"发送者：%s" % sender[i].text)
            print(u"weibo内容：%s" % content[i].text)
            print(u"点赞数：%s" % agreenumber[i].nextSibling.text)
            print('----------------------------------------------------')

    # 登陆模块
    def login(self):
        self.enableCookies()
        data_raw = self.get_pre_login_info()
        data = self.create_post_data(data_raw)
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36"
        }
        request = urllib.request.Request(url=LOGIN, data=data, headers=headers)
        response = urllib.request.urlopen(request)
        content = response.read().decode('GBK')
        url1 = re.findall(r'location\.replace\(\'(.*?)\'\)', content)[0]
        request = urllib.request.Request(url1)
        response = urllib.request.urlopen(request)
        page = response.read().decode('utf-8')
        str = re.findall(r'"userdomain":"(.*?)"', page)[0]
        url2 = 'https://weibo.com/'+str
        request = urllib.request.Request(url2)
        response = urllib.request.urlopen(request)
        final = response.read().decode('utf-8')
        self.gethotinfo(final)
        self.getweiboinfo(final)


if __name__ == '__main__':
    a = Launcher('username', 'passward')
    a.login()
