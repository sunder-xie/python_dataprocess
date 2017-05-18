# encoding=utf-8
__author__ = 'ximeng'

import urllib2
import urllib
import cookielib
import random
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from useragent import RotateUserAgentMiddleware


# http传输请求
class HttpUtil:
    def __init__(self):
        self.cookie_jar = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_jar))
        user_agent = random.choice(RotateUserAgentMiddleware.user_agent_list)
        if user_agent:
            self.headers = [('User-agent', user_agent)]

    # http_get请求，返回字符串结果，测试通过
    def http_get(self, url):
        result = ""
        try:
            print 'get url:%s' % url
            # 设置url格式，将空格转成%20，部分不转
            # url = urllib2.quote(url, safe=':\'/?&=()')
            url = str(url).replace(' ', '').replace(' ', '').replace(' ', '')
            result = urllib2.urlopen(url).read()
            print 'get url:%s' % url
        except Exception, e:
            print "Exception : %s" % e
        return result

    # http_post请求，返回字符串结果，测试 通过
    def http_post(self, url="", value=None):

        # result = ""
        # try:
        #     params = urllib.urlencode(value)
        #     my_request = urllib2.Request(url = url,data = params, headers = self.headers)
        #     result = self.opener.open(my_request).read()
        # except Exception, e:
        #     print "Exception : ", e
        # return result
        result = ""
        try:
            urllib2.install_opener(self.opener)
            data = urllib.urlencode(value)
            req = urllib2.Request(url, data)
            req.add_header('Content-type', 'application/x-www-form-urlencoded')
            req.add_header('Accept', 'text/plain')
            response = urllib2.urlopen(req, timeout=1200)       # 发送页面请求,20min（1200s）超时
            result = response.read()                    # 获取服务器返回的页面信息
        except Exception, e:
            print "Exception : ", e
        return result