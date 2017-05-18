# encoding=utf-8
# 将库表的老的cateId替换为新的cateId
__author__ = 'ximeng'

import sys

from util import CrawlDao, FileUtil
reload(sys)
sys.setdefaultencoding("utf-8")





class OldToNewCate():
    def __init__(self):
        self. fileDao = FileUtil.FileDao()
        self.dao = CrawlDao.CrawlDao()
        # 获得新老的对应关系
        relation_sql_string = 'select my_cat_id,old_cat_id from db_category_relation'
        result_array = self.dao.db.get_data(relation_sql_string)

        self.relation_table = {}
        for relation_result in result_array:
            self.relation_table[int(relation_result['old_cat_id'])] = int(relation_result['my_cat_id'])

    def main(self, excle):

        # 单个excle处理
        data = self.fileDao.open_excel(excle)
        table = data.sheets()[0]
        nrows = table.nrows  # 行数
        ncols = table.ncols  # 列数

        print ('行数：%s ,列数：%s' %(nrows, ncols))
        # 遍历数据第二行开始
        for rownum in range(1, nrows):
            row = table.row_values(rownum)

            table_name = str(row[1]).strip()
            id_name = str(row[2]).strip()

            # 查询该表所有的cate_id
            # db_favourable_activity 特殊，单独处理
            if table_name != 'db_favourable_activity':
                select_cate_string = "select "+id_name+" from "+table_name+" group by "+id_name
                result_array = self.dao.db.get_data(select_cate_string)
                if result_array:
                    for result_data in result_array:
                        if result_data[id_name] is None:
                            continue
                        old_cate_id = int(result_data[id_name])
                        if old_cate_id in self.relation_table.keys():
                            new_cat_id = self.relation_table.get(old_cate_id)
                            # 执行更新
                            update_sql_string = 'update '+table_name+' set '+id_name+' ='+str(new_cat_id)+' where '+id_name+' = '+str(old_cate_id)
                            print 'update %s sql_string:%s' % (table_name, update_sql_string)
                            self.dao.db.update_data(update_sql_string)
            else:
                select_cate_string = "select city_id,sort_cat_ids from db_favourable_activity "
                result_array = self.dao.db.get_data(select_cate_string)
                if result_array:
                    for result_data in result_array:
                        replace = False
                        cate_string = ''
                        old_array = str(result_data['sort_cat_ids']).strip().replace("，", ",").split(",")
                        for old_cate_id in old_array:
                            if old_cate_id in self.relation_table.keys():
                                replace = True
                                new_cat_id = self.relation_table.get(old_cate_id)
                                cate_string += ' '+new_cat_id
                            else:
                                cate_string += ' '+old_cate_id
                        cate_string.strip().replace(" ", ",")
                        # 执行更新
                        if replace:
                            update_sql_string = "update db_favourable_activity set sort_cat_ids ='"+cate_string+"' where city_id= "+str(result_data['city_id'])
                            print 'update %s sql_string:%s' % (table_name, update_sql_string)
                            self.dao.db.update_data(update_sql_string)


oldToNew = OldToNewCate()
excle = r'D:\PythonExcle\cate\updateCateInsteadOld.xls'
oldToNew.main(excle)


