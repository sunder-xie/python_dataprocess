# encoding=utf-8

__author__ = 'zxg'


import sys
import pexpect


reload(sys)
sys.setdefaultencoding("utf-8")


password = 'password'
expect_list = ['(yes/no)', 'password:']

p = pexpect.spawn('ssh username@localhost ls')
try:
    while True:
        idx = p.expect(expect_list)
        print p.before + expect_list[idx],
        if idx == 0:
            print "yes"
            p.sendline('yes')
        elif idx == 1:
            print password
            p.sendline(password)
except pexpect.TIMEOUT:
    print >>sys.stderr, 'timeout'
except pexpect.EOF:
    print p.before
    print >>sys.stderr, '<the end>'