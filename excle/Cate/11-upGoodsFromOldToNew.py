# encoding=utf-8
# 2015.12.02 整理的商品对应新分类生成up sql，生成relation
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

        # p_id+code : id
        self.cate_id_dict = dict()
        # self.cate_name_dict = dict()
        cate_sql = 'SELECT cat_id,cat_name,cat_code,parent_id,vehicle_code,cat_level FROM db_category_dian WHERE cat_id > 2999 '
        cate_array = self.dao.db.get_data(cate_sql)
        for cate_data in cate_array:
            cat_id = str(cate_data['cat_id'])
            cat_code = str(cate_data['cat_code'])
            parent_id = str(cate_data['parent_id'])
            cat_level = str(cate_data['cat_level'])
            vehicle_code = str(cate_data['vehicle_code'])

            key = str(parent_id) + "_" + str(cat_code)
            if cat_level == '3':
                key += "_" + vehicle_code
            self.cate_id_dict[key] = cat_id
            # self.cate_name_dict[cat_id] = str(cate_data['cat_name'])

        # g_id:old_cat_id
        self.goods_dict = dict()
        goods_sql = "select cat_id,goods_id from db_goods where seller_id = 1"
        goods_array = self.dao.db.get_data(goods_sql)
        for goods_data in goods_array:
            self.goods_dict[str(goods_data['goods_id'])] = str(goods_data['cat_id'])


    def main(self, excel_name, write_update_file):
        # 单个excle处理
        data = self.fileDao.open_excel(excel_name)
        #
        table = data.sheets()[0]

        n_rows = table.nrows  # 行数
        n_cols = table.ncols  # 列数

        print ('行数：%s ,列数：%s' % (n_rows, n_cols))
        # 第二行开始
        update_list = list()
        insert_list = list()
        update_list.append("select @now_time := now();")

        cat_dict = dict()
        for row_num in range(1, n_rows):
            row = table.row_values(row_num)

            goods_id = str(row[0]).strip().replace(".0", "")
            vehicle_name = str(row[6]).strip().replace(".0", "")
            sum_code = str(row[15]).strip().replace(".0", "")
            # third_name = row[13].strip().replace("）", ")").replace("（", "(")

            first_code = sum_code[0:1]
            second_code = sum_code[1:3]
            third_code = sum_code[3:6]

            first_id = self.cate_id_dict["0_" + first_code]
            second_id = self.cate_id_dict[first_id + "_" + second_code]

            vehicle_code = 'C'
            if vehicle_name == '乘用车':
                vehicle_code = 'C'
            elif vehicle_name == '商用车':
                vehicle_code = 'H'

            third_key = second_id + "_" + third_code + "_" + vehicle_code
            if third_key not in self.cate_id_dict.keys():
                third_key = second_id + "_" + third_code + "_" + "H"



            if third_key not in self.cate_id_dict.keys():
                print sum_code

            third_id = self.cate_id_dict[third_key]

                # cat_name = self.cate_name_dict[third_id]


            if goods_id not in self.goods_dict.keys():
                print goods_id
                continue
                # old_cat_id = '0'
            else:
                old_cat_id = self.goods_dict[goods_id]
            relation_data = {
                'goods_id': goods_id,
                'old_cat_id': old_cat_id,
                'new_third_cat_id': third_id
            }
            insert_list.append(relation_data)

            if len(insert_list) > 10000:
                self.dao.insert_batch_temple("db_category_goods_relation_temp",insert_list)
                insert_list = list()
            # self.dao.insert_without_exit("db_category_relation", relation_data, relation_data)

            if third_id in cat_dict.keys():
                id_list = list(cat_dict[third_id])
            else:
                id_list = list()
            id_list.append(goods_id)
            cat_dict[third_id] = id_list


        for third_id in cat_dict.keys():
            id_list = list(cat_dict[third_id])
            string = "update db_goods set cat_id = " + third_id + ",gmt_modified = @now_time where goods_id in (" + ",".join(id_list) + ");"
            update_list.append(string)

            # print third_id
        if len(insert_list) > 1:
            self.dao.insert_batch_temple("db_category_goods_relation_temp",insert_list)
        # file_object = open(write_update_file, 'w')
        #
        # try:
        #     file_object.writelines("\n".join(update_list))
        # finally:
        #     file_object.close()



excle_file = r'/Users/zxg/Documents/work/PythonExcle/标准分类体系excle/电商商品转换-20151207.xlsx'
# excle_file = r'/Users/zxg/Documents/work/PythonExcle/标准分类体系excle/test.xlsx'
write_update_file = r'/Users/zxg/Documents/work/淘气档口/新老分类替换/updateGoodsCate.txt'
test = DataTOOnline()
test.main(excle_file, write_update_file)
