# encoding=utf-8
# 分类映射对应---人工处理的对应关系
__author__ = 'ximeng'

import sys

from util import CrawlDao, FileUtil
reload(sys)
sys.setdefaultencoding("utf-8")


class CateMatch():
    def __init__(self, *name, **kwargs):
        self.dao = CrawlDao.CrawlDao()
        # 数据初始化
        self.fileDao = FileUtil.FileDao()

    def main(self, excle, final_id):
        # 单个excle处理
        data = self.fileDao.open_excel(excle)
        table = data.sheets()[0]
        nrows = table.nrows  # 行数
        ncols = table.ncols  # 列数

        for rownum in range(0, nrows):
            row = table.row_values(rownum)

            old_name = row[0].strip().replace(" ", "").replace("（", "(").replace("）", ")")
            new_name = row[1].strip().replace(" ", "").replace("（", "(").replace("）", ")")

            sql_string = "select cat_id,parent_id from db_category where cat_id <= '"+final_id+"' and cat_name = '"+old_name+"'"
            data = self.dao.db.get_data(sql_string)
            if data:
                old_id = data[0]['cat_id']
                old_parent_id = data[0]['parent_id']
            else:
                print 'old_name:%s' % old_name
                continue

            sql_string = "select cat_id,parent_id from db_category where cat_id > '"+final_id+"'  and level = 3 and vehicle_code = 'C'and cat_name ='"+new_name+"'"
            data = self.dao.db.get_data(sql_string)
            if data:
                cat_id = data[0]['cat_id']
                parent_id = data[0]['parent_id']
            else:
                sql_string = "select cat_id,parent_id from db_category where cat_id > '"+final_id+"'  and vehicle_code = 'X'and cat_name ='"+new_name+"'"
                data = self.dao.db.get_data(sql_string)
                if data:
                    cat_id = data[0]['cat_id']
                    parent_id = data[0]['parent_id']
                else:
                    print 'new_name:%s' % new_name
                    continue
            # 存入关系表
            relation_data = dict()
            relation_data['cat_name'] = new_name
            relation_data['my_cat_id'] = cat_id
            relation_data['my_parent_cat_id'] = parent_id
            relation_data['old_cat_id'] = old_id
            relation_data['old_parent_cat_id'] = old_parent_id
            self.dao.insert_without_exit('db_category_relation', relation_data, relation_data)


# final_id = '1233'
# excle = r'D:\PythonExcle\cate\cate20150526.xlsx'
# catMatch = CateMatch()
# catMatch.main(excle, final_id)