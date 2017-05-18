# encoding=utf8
import sys

__author__ = 'zxg'

from util import CrawlDao
from util.pinying.pinyin import PinYin

crawlDao = CrawlDao.CrawlDao('dev_dataserver')
pinyinDO = PinYin()

pinyinDO.load_word()
# string = "前保险杠"
# first_ch = string.decode('utf-8')[0:1].encode('utf-8')
# print first_ch
# print pinyinDO.firstLetter(string)

cat_sql = "select cat_name,cat_id from center_category where is_deleted= 'N'"
cat_array = crawlDao.db.get_data(cat_sql)
for cat_data in cat_array:
    cat_id = str(cat_data['cat_id'])
    cat_name = str(cat_data['cat_name'])

    first_letter = pinyinDO.firstLetter(cat_name)
    crawlDao.update_temple("center_category", {'first_letter': first_letter}, {'cat_id': cat_id})
