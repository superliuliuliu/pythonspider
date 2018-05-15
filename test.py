# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re
import json


with open('test.html',encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'lxml')
div = soup.find(name='div', attrs={'class': 'WB_global_nav WB_global_nav_v2 WB_global_nav_alpha UI_top_hidden '})
print(div.text)


def get_codestring():
    params = {
        "token": self.token,
        "tpl": "mn",
        "apiver": "v3",
        "tt": int(time.time() * 1000),
        "sub_source": "leadsetpwd",
        "username": "15837562085",
        "loginversion": "v4",
        "dv": "dv值",
        "traceid": "",
        "callback": self.get_callback()
   }
   url = "https://passport.baidu.com/v2/api/?logincheck&{}".format(urllib.parse.urlencode(params))
   resq = self.session.get(url)
   link = re.compile('"codeString".*?"(.*?)",')
   groups = link.search(resq.text)
   codeString = groups.group(1)
   print("codeString: ", codeString)
   return codeString
