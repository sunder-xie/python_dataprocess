# encoding=utf-8
# 临时处理oe码，将oe码保存至after_oe字段
__author__ = 'ximeng'

import json
import sys

from util import CrawlDao
reload(sys)
sys.setdefaultencoding("utf-8")

table = 'db_pool_goods'

dao = CrawlDao.CrawlDao()
goods_sql_string = 'select Id,oe_num from '+table + '  order by Id'
goods_data_array = dao.db.get_data(goods_sql_string)
if goods_data_array:
    for goods_data in goods_data_array:
        Id = goods_data['Id']
        oe_num = str(goods_data['oe_num'])
        after_oe_num = oe_num.strip().replace('-', '').replace(',', '').replace('.', '').replace('/', '').replace('*', '').replace('\\', '')

        good = dict()
        good['after_oe'] = after_oe_num
        wheredict = dict()
        wheredict['Id'] = Id
        dao.update_temple(table, good, wheredict)
else:
    print 'not have goods_sql_string in db_pool_goods'
    exit()