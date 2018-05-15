# coding = utf-8
import random
import time
from urllib import parse

# 得到codestring函数

def get_dv():
    dv = "tk" + str(random.random()) + str(int(time.time()* 1000))
    dv = dv + "@"
    url_data = parse.quote(dv)
    print(url_data)


verfy = input(u"请输入你看到的验证码：")
print(verfy)
