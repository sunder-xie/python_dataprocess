# encoding=utf-8
# 商品分类表的导入---油品跟保养件特殊
__author__ = 'ximeng'

import json
import sys

from util import CrawlDao, FileUtil
reload(sys)
sys.setdefaultencoding("utf-8")


class CateSpecial():
    def __init__(self, *name, **kwargs):
        self.dao = CrawlDao.CrawlDao()
        # 数据初始化
        self.fileDao = FileUtil.FileDao()
        self.update_sql_string = set()

    # 保存set于文本中
    def save_string_files(self, file_name):
        read_file = open(file_name, "r")
        content = read_file.read()
        read_file.close()

        fo = open(file_name, "w+")
        print "Name of the file: ", fo.name

        # fo.seek(0, 2)
        for q in self.update_sql_string:
            content += q+';\n'
        fo.writelines(content)
        fo.close()
    # 按行处理-第二行开始
    def main_process(self,table, nrows, final_id):
        for rownum in range(1, nrows):
            row = table.row_values(rownum)
            parent_id = 0
            cate_data = dict()
            cate_exit_data = dict()

              # 桑军excle 1.0
            # vehicle_code = row[0].strip().replace(" ", "")
            # first_name = row[1].strip().replace(" ", "")
            # first_code = row[2].strip().replace(" ", "")
            # second_name = row[3].strip().replace(" ", "")
            # second_code = row[4].strip().replace(" ", "")
            # third_name = row[5].strip().replace(" ", "")
            # third_code = row[6].strip().replace(" ", "")
            #
            # part_name = row[7].strip().replace(" ", "")
            # part_code = row[8].strip().replace(" ", "")
            # sum_code = vehicle_code+first_code+second_code+third_code+part_code
            #
            # label_name = row[10].strip().replace(" ", "")
            # aliss_name_array = row[11].strip().replace(" ", "")
            # 桑军excle 1.0 修改版
            first_name = row[0].strip().replace(" ", "").replace("（", "(").replace("）", ")")
            second_name = row[1].strip().replace(" ", "").replace("（", "(").replace("）", ")")
            third_name = row[2].strip().replace(" ", "").replace("（", "(").replace("）", ")")
            part_name = row[3].strip().replace(" ", "").replace("（", "(").replace("）", ")")
            sum_code = row[4].strip().replace(" ", "")
            label_name = row[5].strip().replace(" ", "").replace("（", "(").replace("）", ")")
            aliss_name_array = row[6].strip().replace(" ", "").replace("（", "(").replace("）", ")")

            is_kind = row[7].strip().replace(" ", "").replace("（", "(").replace("）", ")")
            if is_kind == 'A':
                cat_kind = '0'
            else:
                cat_kind = '1'

            first_code = sum_code[1:2]
            second_code = sum_code[2:4]
            third_code = sum_code[4:7]
            part_code = sum_code[7:]

            vehicle_code = sum_code[0:1]

            # 零件名为空时，取上级存
            if part_name == '':
                part_name = third_name
            if third_name == '':
                part_name = second_name

            cate_data['vehicle_code'] = vehicle_code
            cate_data['cat_kind'] = cat_kind
            # ==========================存一级分类===============================
            cate_data['cat_name'] = first_name
            cate_data['parent_id'] = parent_id
            cate_data['level'] = 1
            cate_data['code'] = first_code
            cate_data['vehicle_code'] = vehicle_code

            cate_exit_data['cat_name'] = first_name
            # 插入或更新数据
            others_sql = ' and cat_id <'+str(final_id)
            data = self.dao.boolean_exit("db_category", cate_exit_data,  'cat_id', others_sql)
            if data:
                key_id = data[0]['cat_id']
                where_dict = dict()
                where_dict['cat_id'] = key_id
                update_string = self.dao.update_temple("db_category", cate_data, where_dict)
                self.update_sql_string.add(update_string)
                first_cate_id = key_id
            else:
                print '==================not have this old cate : %s===========================' % first_name
                # exit()
                # TODO 临时
                cate_data['style'] = ''
                cate_data['category_thumb'] = ''
                cate_data['category_img'] = ''
                cate_data['original_img'] = ''
                primary_key_id = self.dao.insert_or_update_without_exit("db_category", cate_data, cate_data, 'cat_id')
                first_cate_id = primary_key_id
            # ===================================存二级分类==========================
            cate_data['cat_name'] = second_name
            cate_data['parent_id'] = first_cate_id
            cate_data['level'] = 2
            cate_data['code'] = second_code
            cate_data['vehicle_code'] = vehicle_code
            if third_name == '':
                cate_data['is_leaf'] = 1

            cate_exit_data['cat_name'] = second_name
            cate_exit_data['parent_id'] = first_cate_id
            # 插入或更新数据
            data = self.dao.boolean_exit("db_category", cate_exit_data, 'cat_id')
            if data:
                key_id = data[0]['cat_id']
                where_dict = dict()
                where_dict['cat_id'] = key_id
                update_string = self.dao.update_temple("db_category", cate_data, where_dict)
                self.update_sql_string.add(update_string)
                second_cate_id = key_id
            else:
                cate_data['style'] = ''
                cate_data['category_thumb'] = ''
                cate_data['category_img'] = ''
                cate_data['original_img'] = ''
                primary_key_id = self.dao.insert_temple("db_category", cate_data)
                second_cate_id = primary_key_id
            # ==============================存零件名称表========================
            part_data = dict()
            part_exit_data = dict()

            part_exit_data['sum_code'] = sum_code
            part_exit_data['code'] = part_code

            part_data['part_name'] = part_name
            part_data['code'] = part_code
            part_data['sum_code'] = sum_code

            part_data['aliss_name_text'] = aliss_name_array.replace("、", ",")
            part_data['label_name_text'] = label_name

            part_data['cate_id'] = second_cate_id
            part_data['cate_parent_id'] = first_cate_id

            part_id = self.dao.insert_or_update_without_exit("db_category_part", part_data, part_exit_data)

            # ============================存标签表==========================
            if label_name != '':
                label_data = dict()
                label_data['label_name'] = label_name
                label_id = self.dao.insert_without_exit("db_category_label", label_data, label_data)

                # 二者的对应关系
                label_part_data = dict()
                label_part_data['label_id'] = label_id
                label_part_data['part_id'] = part_id
                self.dao.insert_without_exit("db_category_part_label", label_part_data, label_part_data)

    # 主处理函数
    def main(self, excle, final_id, file_name):
        print '===============start CateSpecial==================='
        # 单个excle处理
        data = self.fileDao.open_excel(excle)
        table = data.sheets()[0]
        nrows = table.nrows  # 行数
        ncols = table.ncols  # 列数

        print ('行数：%s ,列数：%s' %(nrows, ncols))

        # 第二行开始的后面所有
        self.main_process(table, nrows, final_id)
        print '===============end CateSpecial==================='
        # 保存更新操作
        self.save_string_files(file_name)

# excle = r'D:\PythonExcle\cate\0603_test.xls'
# final_id = str(1233)
#
# cateSpecial = CateSpecial()
# cateSpecial.main(excle, final_id)





