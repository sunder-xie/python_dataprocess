# encoding=utf-8
# 2015.12.01 将整理出来的分类映射 映射到mapping 中
__author__ = 'zxg'

import sys

from util import CrawlDao, FileUtil, StringUtil

reload(sys)
sys.setdefaultencoding("utf-8")


class DataTOOnline:
    def __init__(self):
        self.dao = CrawlDao.CrawlDao()
        self.fileDao = FileUtil.FileDao()
        self.stringUtil = StringUtil.StringUtil()

        self.table_mapping = 'db_category_mapping'

        self.vehicle_dict = {"商用车": "H", "乘用车": "C"}
        # 新分类的
        self.cate_dict = dict()
        cate_sql = "select cat_id,cat_name,vehicle_code,cat_level,parent_id from db_category_new "
        cate_array = self.dao.db.get_data(cate_sql)
        for cate_data in cate_array:
            cat_id = str(cate_data['cat_id'])
            cat_name = str(cate_data['cat_name'])
            cat_level = str(cate_data['cat_level'])
            vehicle_code = str(cate_data['vehicle_code'])
            parent_id = str(cate_data['parent_id'])
            key = cat_name + "_" + cat_level + "_" + parent_id

            if cat_level == '3':
                key += "_" + vehicle_code
            self.cate_dict[key] = cat_id

        # 老cate的图片数据
        self.old_cat_dict = dict()
        old_cat_sql = "select cat_name,category_thumb from db_category where cat_id < 2999 and parent_id = 0 and is_deleted = 'N'"
        old_cate_array = self.dao.db.get_data(old_cat_sql)
        for old_cate_data in old_cate_array:
            cat_name = str(old_cate_data['cat_name'])
            category_thumb = str(old_cate_data['category_thumb'])
            self.old_cat_dict[cat_name] = category_thumb

    # 乘用车或商用车处理
    def table_do(self, table):

        n_rows = table.nrows  # 行数
        n_cols = table.ncols  # 列数

        print ('行数：%s ,列数：%s' % (n_rows, n_cols))
        # 第二行开始
        for row_num in range(1, n_rows):
            row = table.row_values(row_num)

            first_cate_name = str(row[0].strip())
            second_cate_name = str(row[1].strip())
            third_cate_name = str(row[2].strip())
            vehicle_name = str(row[3].strip())
            first_mapping_name = str(row[4].strip())
            first_sort_order = str(row[5]).strip().replace(".0", "")
            second_mapping_name = str(row[6].strip())
            second_sort_order = str(row[7]).strip().replace(".0", "")

            if first_sort_order == '':
                continue

            # 获得三级cat——id
            vehicle_code = self.vehicle_dict[vehicle_name]

            first_id = self.cate_dict[first_cate_name + "_1_" + "0"]
            second_id = self.cate_dict[second_cate_name + "_2_" + first_id]
            third_key = third_cate_name + "_3_" + str(second_id) +"_"+vehicle_code

            if third_key not in self.cate_dict.keys():
                print third_key
            third_id = self.cate_dict[third_key]

            if first_mapping_name == '车身构件':
                category_thumb = self.old_cat_dict['车身']
            else:
                category_thumb = self.old_cat_dict[first_mapping_name]

            print category_thumb
            first_data = {
                'cat_name_mapping': first_mapping_name,
                'cat_mapping_level': 1,
                'vehicle_code': vehicle_code,
                "category_thumb": category_thumb,
                "category_img": "",
                "original_img": "",
                "sort_order": first_sort_order
            }
            first_mapping_id = self.dao.insert_without_exit(self.table_mapping, first_data, first_data)

            if second_sort_order == '':
                second_sort_order = '0'
            second_data = {
                'cat_name_mapping': second_mapping_name,
                'cat_mapping_level': 2,
                'vehicle_code': vehicle_code,
                "category_thumb": "",
                "category_img": "",
                "original_img": "",
                "sort_order": second_sort_order,
                "parent_id": first_mapping_id,
                'cat_id':third_id,
                'cat_name':third_cate_name
            }
            self.dao.insert_without_exit(self.table_mapping, second_data, second_data)

    def main(self, excle_name):
        # 单个excle处理
        data = self.fileDao.open_excel(excle_name)
        # 映射
        table = data.sheets()[0]

        self.table_do(table)


excle_file = r'/Users/zxg/Documents/work/PythonExcle/标准分类体系excle/销售分类映射射.xlsx'

test = DataTOOnline()
test.main(excle_file)
