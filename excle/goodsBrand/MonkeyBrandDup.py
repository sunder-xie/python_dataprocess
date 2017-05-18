# encoding=utf-8
# monkey项目品牌中英重复去重
import re

__author__ = 'zxg'

import sys

from util import CrawlDao

reload(sys)
sys.setdefaultencoding("utf-8")


class SqlToMonkey:
    def __init__(self):
        self.dao = CrawlDao.CrawlDao()

    def main(self):
        sql_string = "select id,name_ch,name_en from db_monkey_commodity_brand"
        print 'monkeyBrand获得数据:%s' % sql_string
        result_array = self.dao.db.get_data(sql_string)
        if result_array:
            for result in result_array:
                id = result['id']
                name_ch = result['name_ch']
                name_en = result['name_en']

                if name_ch == name_en:
                    where_dict = dict()
                    where_dict['id'] = id

                    monkey_brand_data = dict()
                    # 判断中文
                    zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')
                    match = zh_pattern.search(name_ch)
                    if match:
                        print u'name_ch中有中文：%s' % name_ch
                        monkey_brand_data['name_ch'] = name_ch
                        monkey_brand_data['name_en'] = ''
                    else:
                        print u'name_ch中无中文：%s' % name_ch
                        monkey_brand_data['name_ch'] = ''
                        monkey_brand_data['name_en'] = name_en

                    self.dao.update_temple('db_monkey_commodity_brand',monkey_brand_data,where_dict)


sql = SqlToMonkey()
sql.main()