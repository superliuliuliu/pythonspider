# coding = utf-8
"""
进行百度的模拟登陆过程
较模拟登陆新浪微博的不同点在于实现了图形验证码的识别
目的在于巩固爬虫知识
"""

import requests
import rsa
import json
import math
import random
import time
import base64
from urllib import parse
import urllib

"""
random()函数
功能：返回一个随机生成的随机数范围在[0,1)
需要注意的是random()不能够直接调用需要 通过random静态对象调用
--------------------------------------------------------------
hex()函数
功能：将10进制数字转换16进制数字（字符形式）
使用 hex(x) 其中x为10进制数
--------------------------------------------------------------
floor()函数
功能：返回数字的下含整数
常用在random中
--------------------------------------------------------------
js： 函数 toString()
功能： 将一个Number对象转换为字符对象 并返回
toString(radix)
radix 可选的数字范围在[2,36]用来表示规定数字的基数 选10时则可以忽略 经常利用该函数进行进位制的转换
--------------------------------------------------------------
append(obj)函数
功能：在列表的末尾添加新的对象
注意append操作的对象是列表
--------------------------------------------------------------
js getTime()函数
功能：返回距1970年1月1返回距1970年1月1日的毫秒数
注意调用该函数的对象是一个时间对象
"""
# 登录用的headers
headers = {
    'Host': 'passport.baidu.com',
    'Referer': 'https://www.baidu.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36'
}
# 创建一个session 以便在访问会话时带上cookies
session = requests.session()
session.get("https://passport.baidu.com/v2/?login", headers=headers)

# 创建一个登陆类
class Launcher:

    def __init__(self,username,password):
        self.username = username
        self.password = password
    # 获得登陆所需的gid编码 gid编码的获取方式从js代码之中得知
    def get_gid(self):
        # gid编码的初始形式
        gid = "xxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"
        # gid代码的转换过程
        gid = list(gid)
        for i in range(len(gid)):
            if gid[i] in "xy":
                r = int(16 * random.random())
                if gid[i] in "x":
                    gid[i] = hex(r).replace("0x",'').upper()
                else:
                    gid[i] = hex(3 & r | 8).replace("0x",'').upper()
            else:
                pass
        return ''.join(gid)
    # 构建callback数据  对此数据的获得 比较麻烦 经过多次的抓包分析 发现callback数据有一个公共点都含有bd__cbs__
    # 根据这个在js代码中搜索上述向发现构造callback的代码段 此种包含js代码中的toString()函数 具体分析见上文注释
    def get_callback(self):
        prefix = "bd__cbs__"
        r = math.floor(random.random() * 2147483648)
        # 下面进行将上面产生的随机数转换16进制 来满足js代码中的toString(36)
        loopabc = '0123456789abcdefghijklmnopqrstuvwxyz'
        a = []
        while r != 0:
            a.append(loopabc[r % 36])
            r = r // 36
        # 倒序
        a.reverse()
        return prefix+''.join(a)

    # login中需要的callback
    def get_callback1(self):
        prefix = "parent.bd__pcbs__"
        r = math.floor(random.random() * 2147483648)
        # 下面进行将上面产生的随机数转换16进制 来满足js代码中的toString(36)
        loopabc = '0123456789abcdefghijklmnopqrstuvwxyz'
        a = []
        while r != 0:
            a.append(loopabc[r % 36])
            r = r // 36
        # 倒序
        a.reverse()
        return prefix+''.join(a)

    # 获取token数据 从js代码中获取  注意整个访问过程中 只生成一次token 该token数据一一直使用直至登陆结束
    def get_token(self):
        # 构建一个新的url 然后从这个url返回的数据中获取token数据
        callback =self.get_callback()
        gid = self.get_gid()
        global init_time
        # init_time 参数的获取方法同样由js代码规定 python中返回的是浮点数秒
        init_time = str(int(time.time() * 1000))
        params = {
            'tpl': 'mn',
            'apiver': 'v3',
            'tt': init_time,
            'class': 'login',
            'gid': gid,
            'loginversion': 'v4',
            'logintype': 'dialogLogin',
            'traceid': '',
            'callback': callback
        }
        token_url = "https://passport.baidu.com/v2/api/?getapi&{}".format(urllib.parse.urlencode(params))
        token_html = session.get(url=token_url, headers=headers)
        token_content = token_html.text.replace(callback,'')
        token_content = eval(token_content)
        return(token_content['data']['token'])

    # 获取pubkey 和 key
    def get_key(self, token):
        callback = self.get_callback()
        gid = self.get_gid()
        init_time = str(int(time.time() * 1000))
        params = {
            'token': token,
            'tpl': 'mn',
            'apiver': 'v3',
            'tt': init_time,
            'gid': gid,
            'loginversion': 'v4',
            'traceid': '',
            'callback': callback
        }
        pubkey_url = "https://passport.baidu.com/v2/getpublickey?{}".format(urllib.parse.urlencode(params))
        # 更换headers信息中的referer
        headers['Referer'] = 'https://www.baidu.com/?tn=78000241_9_hao_pg'
        pubkey_html = session.get(url=pubkey_url, headers=headers)
        pubkey_content = pubkey_html.text.replace(callback,'')
        pubkey_content =eval(pubkey_content)
        return(pubkey_content['pubkey'],pubkey_content['key'])

    # 对用户提交的表单密码进行加密
    def get_encrypted_pw(self,pubkey):
        pub = rsa.PublicKey.load_pkcs1_openssl_pem(pubkey.encode("utf-8"))
        password= self.password.encode("utf-8")
        psword = rsa.encrypt(password, pub)
        psword = base64.b64encode(psword)
        return psword.decode("utf-8")

    # 获取dv值用于获得下文中的codestring
    def get_dv(self):
        dv = "tk" + str(random.random()) + str(int(time.time()* 1000))
        dv = dv + "@"
        dv = dv + "ssl0Ty7kIgrmtCBCj0CIu79iXBCihUr6hU9ZH~G945JKi3pkrl763w76rgrmtCBCj0CIu79iXBCihUr6hU9ZH~G945JKi3pkrzr64w76JgrmtCBCj0CIu79iXBCihUr6hU9ZH~G945JKi3pkrjr~Hw76ogrmtCBCj0CIu79iXBCihUr6hU9ZH~G945JKi3pkC~r67w76CgrmtCBCj0CIu79iXBCihUr6hU9ZH~G945JKi3pkC-r6Lwhl0A~r~o~pkBj7mltr~BZpunh6IPABCiU9ih6CuwtruXUGRXfPsHzC941Nyn3BWnMUq__y~~Ow~IsuWdOhIlirAlzpkJi-lvPsglp12b71Blr1q~76Bb56rtrkJir6Cz71ryr1B~5kVbrB__il0K~O0n-D0repzXZPZDMJRuYG0CMJyXTp~X-N1--5kqzr62ZrHwtrHXQJKXUDsDgPKjIGKGYNRHIElvrmllpkVy7Slyr~Dgr6ryrmlZ71Vgr6ryrmltr~JlpkDz5q__"
        return dv

    # 获取codestring  在url=https://passport.baidu.com/v2/api/?logincheck&token=...下得到需要获取dv值
    def get_codingstring(self,token):
        callback = self.get_callback()
        params = {
        'token': token,
        'tpl': 'mn',
        'apiver': 'v3',
        'tt': int(time.time() * 1000),
        'sub_source': 'leadsetpwd',
        'username': self.username,
        'loginversion': 'v4',
        'dv': self.get_dv(),
        'traceid': '',
        'callback': callback
        }
        code_url = "https://passport.baidu.com/v2/api/?logincheck&{}".format(urllib.parse.urlencode(params))
        headers['Referer'] = 'https://www.baidu.com/?tn=78000241_9_hao_pg'
        code_html = session.get(url=code_url, headers=headers)
        codestring = code_html.text.replace(callback,'')
        codestring = eval(codestring)
        codestring = codestring['data']['codeString']
        return codestring

    # 获取验证码图片 利用上面获得codestring参数构建新的url地址
    def get_image(self, token,codestring):
        headers1 = {
            'Host': 'passport.baidu.com',
            'Referer': 'https://www.baidu.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36'
        }
        image_url = "https://passport.baidu.com/cgi-bin/genimage?" + codestring#self.get_codingstring(token)
        headers['Referer'] = 'https://www.baidu.com/?tn=78000241_9_hao_pg'
        cha_page = session.get(image_url, headers=headers)
        with open("cha"+str(math.floor(random.random()*100))+".png", 'wb') as f:
            f.write(cha_page.content)
            f.close()
        try:
            im = Image.open("cha.jpg")
            im.show()
            im.close()
        except Exception as e:
            print(u"请到当前目录下，找到验证码后输入")

    # 登陆模块
    def login(self):
        # 需要注意的是在这里提交表单的callback和前面提交的callback格式并不一样
        login_url = "https://passport.baidu.com/v2/api/?login"
        callback = self.get_callback1()
        token = self.get_token()
        pubkey,key = self.get_key(token)
        gid = self.get_gid()
        codestring = self.get_codingstring(token)
        dv = self.get_dv()
        self.get_image(token,codestring=codestring)
        verify = input(u"请输入你看到的验证码：")
        data = {
        'staticpage': 'https://www.baidu.com/cache/user/html/v3Jump.html',
        'charset': 'UTF-8',
        'token': token,
        'tpl': 'mn',
        'subpro': '',
        'apiver': 'v3',
        'tt': int(time.time() * 1000),
        'codestring': codestring,
        'safeflg': 0,
        'u': 'https://www.baidu.com/?tn=78000241_9_hao_pg',
        'isPhone': '',
        'detect': 1,
        'gid': gid,
        'quick_user': 0,
        'logintype': 'dialogLogin',
        'logLoginType': 'pc_loginDialog',
        'idc': '',
        'loginmerge': 'true',
        'splogin': 'rate',
        'username': self.username,
        'password': self.get_encrypted_pw(pubkey=pubkey),
        'verifycode': verify,
        'mem_pass': 'on',
        'rsakey': key,
        'crypttype': 12,
        'ppui_logintime': 23677,
        'countrycode': '',
        'loginversion': 'v4',
        'dv': dv,
        'callback': callback
        }
        headers['Referer'] = 'https://www.baidu.com/?tn=78000241_9_hao_pg'
        login_html = session.get(login_url, data=data, headers=headers)
        print(login_html.cookies)
        html_index = session.get('http://tieba.baidu.com/home/main?id=0eec4c656d757933337fa7&fr=userbar&red_tag=m1226874909')
        with open("tieba.html", 'wb') as f:
            f.write(html_index.content)
            f.close()

# 执行主程序
if  __name__ == '__main__':
    a = Launcher('15837562085','734190426l')
    print(u"欢迎%s,您正在使用lgy编写的模拟登陆百度程序！"% a.username)
    a.login()
