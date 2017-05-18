# encoding=utf-8
# 商用车对应关系建立起来
__author__ = 'ximeng'

import sys

from util import CrawlDao
reload(sys)
sys.setdefaultencoding("utf-8")

dao = CrawlDao.CrawlDao()


class CateLCVRelation():
    def __init__(self):
        self.dao = CrawlDao.CrawlDao()


    def main(self, final_id, old__parent_name, new_parent_name):
        # 获得新的商用车二级目录
        new_table = dict()

        LCV_sql_string = "select cat_id from db_category where cat_name = '"+new_parent_name+"' and vehicle_code = 'X' and cat_id >"+str(final_id)
        new_LCV_data = dao.db.get_data(LCV_sql_string)
        if new_LCV_data:
            new_LCV_id = new_LCV_data[0]['cat_id']
        else:
            print 'not have LVC in new category'
            exit()
        new_LCV_sql_string = "select cat_id,cat_name from db_category where parent_id = "+str(new_LCV_id)
        new_dataArray = dao.db.get_data(new_LCV_sql_string)
        if new_dataArray:
            for new_data in new_dataArray:
                new_table[new_data['cat_name']] = int(new_data['cat_id'])

        # 获得老商用车的一级目录
        LCV_sql_string = "select cat_id from db_category where cat_name = '"+old__parent_name+"' and cat_id <="+str(final_id)
        old_LCV_data = dao.db.get_data(LCV_sql_string)
        if old_LCV_data:
            old_LCV_id = old_LCV_data[0]['cat_id']
        else:
            print 'not have LVC in old category'
            exit()
        # 将商用车的二级目录对应到新的分类上
        old_LCV_sql_string = "select cat_id,cat_name from db_category where parent_id = "+str(old_LCV_id)
        old_dataArray = dao.db.get_data(old_LCV_sql_string)
        if old_dataArray:
            for old_data in old_dataArray:
                old_name = old_data['cat_name']
                old_id = old_data['cat_id']
                if old_name in new_table.keys():
                    new_id = new_table.get(old_name)

                    # 存入关系表
                    relation_data = dict()
                    relation_data['cat_name'] = old_name
                    relation_data['my_cat_id'] = new_id
                    relation_data['my_parent_cat_id'] = new_LCV_id
                    relation_data['old_cat_id'] = old_id
                    relation_data['old_parent_cat_id'] = old_LCV_id
                    dao.insert_without_exit('db_category_relation', relation_data, relation_data)
        print 'end LCVRelation'

# final_id = str(1233)
# new_parent_name = '商用车'
# old__parent_name = '商用车'
# lcv_relation = CateLCVRelation()
# lcv_relation.main(final_id,old__parent_name,new_parent_name)
