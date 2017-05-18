# encoding=utf-8
# 临时处理轮胎无规格型号

__author__ = 'zxg'

import sys
import json

from util import CrawlDao,HttpUtil

reload(sys)
sys.setdefaultencoding("utf-8")

dao = CrawlDao.CrawlDao()

commodity_goods_sql = "select id,goods_code from db_monkey_commodity_goods where part_name = \"轮胎\" and isdelete = 0 "
print 'luntai 获得数据:%s' % commodity_goods_sql
result_array = dao.db.get_data(commodity_goods_sql)
index = 0
if result_array:
    for result in result_array:
        id = result['id']
        goods_code = result['goods_code']

        where_dict = dict()
        where_dict['id'] = id

        goods_sql = "select goods_format from db_goods where new_goods_sn = '"+goods_code+"'"
        final_result = dao.db.get_data(goods_sql)

        if len(final_result) > 1:
            print 'what?'
        if final_result:
            goods_format = final_result[0]['goods_format']

            goos_data = dict()
            goos_data['goods_format'] = goods_format
            dao.update_temple('db_monkey_commodity_goods',goos_data,where_dict)

        else:
            print "wrong，no format:%s" % goods_code
