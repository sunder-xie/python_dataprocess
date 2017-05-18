# encoding=utf-8
# 2015.12.21 导入碰撞等级于数据库
__author__ = 'zxg'

import sys

from util import CrawlDao, FileUtil, StringUtil

reload(sys)
sys.setdefaultencoding("utf-8")


class CrashIn:
    def __init__(self):
        self.dao = CrawlDao.CrawlDao("modeldatas")
        self.fileDao = FileUtil.FileDao()

        self.part_code_id_dict = dict()
        part_sql = "select id,sum_code from db_category_part where is_deleted = 'N'"
        for part_data in self.dao.db.get_data(part_sql):
            self.part_code_id_dict[str(part_data['sum_code'])] = int(part_data['id'])

    def main(self, excle_name):
        # 单个excle处理
        data = self.fileDao.open_excel(excle_name)
        first_table = data.sheets()[0]
        first_rows = first_table.nrows  # 行数
        first_cols = first_table.ncols  # 列数

        second_table = data.sheets()[1]
        second_rows = second_table.nrows  # 行数
        second_cols = second_table.ncols  # 列数

        # 处理第二个 sheet的碰撞基础数据
        crash_dict = dict()
        for row_num in range(1, second_rows):
            row = second_table.row_values(row_num)

            crash_code = row[0].strip()
            crash_place = row[1].strip()
            crash_degree = row[2].strip()
            crash_data = {
                'crash_code': crash_code,
                'crash_place': crash_place,
                'crash_degree': crash_degree,
            }
            crash_id = self.dao.insert_without_exit("db_category_crash", crash_data, {'crash_code': crash_code})
            crash_dict[crash_code] = int(crash_id)

        # 处理第一个sheet中的碰撞数据
        insert_list = list()
        for row_num in range(1, first_rows):
            row = first_table.row_values(row_num)

            sum_code = row[10].strip()
            crash_array_str = str(row[14]).strip()

            part_id = self.part_code_id_dict[sum_code]

            while len(crash_array_str) > 0:
                crash_code = crash_array_str[0:2]
                crash_id = crash_dict[crash_code]
                insert_list.append({'part_id': part_id, "crash_id": crash_id})

                crash_array_str = crash_array_str[2:]

        self.dao.insert_batch_temple("db_category_crash_part_relation", insert_list)

excle_file = r'/Users/zxg/Documents/work/PythonExcle/标准分类体系excle/配件标准模板v106版（碰撞+车类）.xlsx'
crash = CrashIn()
crash.main(excle_file)