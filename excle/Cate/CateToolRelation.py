# encoding=utf-8
# 工具对应关系建立起来
__author__ = 'ximeng'

import sys

from util import CrawlDao
reload(sys)
sys.setdefaultencoding("utf-8")



class CateTool():
    def __init__(self):
        self.dao = CrawlDao.CrawlDao()

    def main(self, final_id, old__parent_name):
        # 获得老设备工具的一级目录
        LCV_sql_string = "select cat_id from db_category where cat_name = '"+old__parent_name+"' and cat_id <="+str(final_id)
        old_LCV_data = self.dao.db.get_data(LCV_sql_string)
        if old_LCV_data:
            old_LCV_id = old_LCV_data[0]['cat_id']
        else:
            print 'not have LVC in old category'
            exit()
        # 将设备工具的二级目录对应到新的分类上
        old_LCV_sql_string = "select cat_id,cat_name from db_category where parent_id = "+str(old_LCV_id)
        old_dataArray = self.dao.db.get_data(old_LCV_sql_string)
        if old_dataArray:
            for old_data in old_dataArray:
                old_name = old_data['cat_name']
                old_id = old_data['cat_id']
                if old_name in (u'设备', u'工具'):
                    print 'It is %s' % old_name
                    continue
                if old_name == u'万能表':
                    old_name = '万用表'
                # 存入关系表
                relation_data = dict()
                relation_data['cat_name'] = old_name
                relation_data['old_cat_id'] = old_id
                relation_data['old_parent_cat_id'] = old_LCV_id

                exit_sql = "select cat_id,parent_id from db_category where cat_id >"+str(final_id)+" and cat_name ='"+old_name+"' and vehicle_code = 'X' and level = 3"
                # exit_sql += "and is_show = 0"
                print '判断存在不存在的exit_sql：%s' % exit_sql

                dataARRAY = self.dao.db.get_data(exit_sql)
                if dataARRAY:
                    for data in dataARRAY:
                        relation_data['my_cat_id'] = data['cat_id']
                        relation_data['my_parent_cat_id'] = data['parent_id']
                        self.dao.insert_without_exit('db_category_relation', relation_data, relation_data)
                else:
                    print "%s:新分类中无法匹配" % old_name


        print 'the end~~~ ToolRelation'


#
# final_id = '1233'
# new_parent_name = '设备工具'
# old__parent_name = '汽保产品'
#
# cateTool = CateTool()
# cateTool.main(final_id, old__parent_name, new_parent_name)

