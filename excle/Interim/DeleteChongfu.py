# encoding=utf-8
# 删除重复数据
__author__ = 'ximeng'

import json
import sys

from util import CrawlDao
reload(sys)
sys.setdefaultencoding("utf-8")

table = 'db_pool_goods_car'

have_list = list()

select_sql_string = 'select id, goods_oe_num ,car_id from db_pool_goods_car group by  goods_oe_num,car_id having count(*)>1 order by id'
dao = CrawlDao.CrawlDao()
result_data_array = dao.db.get_data(select_sql_string)
if result_data_array:
    for result_data in result_data_array:
        id = str(result_data['id'])
        oe = str(result_data['goods_oe_num'])
        car_id = str(result_data['car_id'])
        # 查找该 oe和car对应的多条数据，跳过这一条
        sql_string = "select id from db_pool_goods_car dpgc where  goods_oe_num ='"+oe+"' and car_id ="+car_id+" and id !="+id
        data_array = dao.db.get_data(sql_string)
        if data_array:
            for result in data_array:
                car = dict()
                car['isdelete'] = 1
                wheredict = dict()
                wheredict['Id'] = result['id']
                dao.update_temple(table, car, wheredict)

