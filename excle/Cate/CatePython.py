# encoding=utf-8
# 商品分类表的导入---主
__author__ = 'ximeng'

import sys

from util import CrawlDao, FileUtil

reload(sys)
sys.setdefaultencoding("utf-8")


class Cate:
    def __init__(self):
        self.dao = CrawlDao.CrawlDao()
        self.fileDao = FileUtil.FileDao()
        self.sql_table = 'db_category'
        self.sql_relation_table = 'db_category_relation'
        self.update_sql_string = set()

    # 保存对应关系
    def save_relation(self, cat_name, cat_id, parent_id, sql_table, sql_relation_table, final_id,replace=True):
        # 判断关系表中有无此数据
        sql_string = "select id,cat_name from "+sql_relation_table+" where cat_name ='"+cat_name+"'"
        print '判断关系表中有无此数据:%s' % sql_string
        result_array = self.dao.db.get_data(sql_string)
        if result_array:
            if replace:
                return
            else:
                # 新的parent更新到表中
                for result in result_array:
                    relation_data = dict()
                    relation_data['my_parent_cat_id'] = parent_id
                    where_dict = dict()
                    where_dict['id'] = result['id']
                    self.dao.update_temple(sql_relation_table, relation_data, where_dict)
        else:
            # 存入关系表
            relation_data = dict()
            relation_data['cat_name'] = cat_name
            relation_data['my_cat_id'] = cat_id
            relation_data['my_parent_cat_id'] = parent_id
            exit_sql = "select cat_id,parent_id,keywords,cat_desc,template_file,measure_unit,style,category_thumb,category_img,original_img,category_sn from "
            exit_sql += sql_table+' where cat_id <'+str(final_id)+" and cat_name='"+cat_name+"'"

            # exit_sql += "and is_show = 0"
            print '判断存在不存在的exit_sql：%s' % exit_sql
            data_array = self.dao.db.get_data(exit_sql)
            if data_array:
                for data in data_array:
                    # 存对应关系
                    relation_data['old_cat_id'] = data['cat_id']
                    relation_data['old_parent_cat_id'] = data['parent_id']
                    self.dao.insert_without_exit(sql_relation_table, relation_data, relation_data)
                    # 将老数据中的一些信息 更新到新分类上
                    up_cate_data = dict()
                    up_cate_data['cat_id'] = cat_id
                    up_cate_data['keywords'] = data['keywords']
                    up_cate_data['cat_desc'] = data['cat_desc']
                    up_cate_data['template_file'] = data['template_file']
                    up_cate_data['measure_unit'] = data['measure_unit']
                    up_cate_data['style'] = data['style']
                    up_cate_data['category_thumb'] = data['category_thumb']
                    up_cate_data['category_img'] = data['category_img']
                    up_cate_data['original_img'] = data['original_img']
                    up_cate_data['category_sn'] = data['category_sn']
                    where_dict = dict()
                    where_dict['cat_id'] = cat_id
                    sql_string = self.dao.update_temple(sql_table, up_cate_data, where_dict)
                    self.update_sql_string.add(sql_string)

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
        
    # 主函数
    def main(self, excle, final_id, file_name):
        # 单个excle处理
        data = self.fileDao.open_excel(excle)
        table = data.sheets()[0]
        nrows = table.nrows  # 行数
        ncols = table.ncols  # 列数

        print ('行数：%s ,列数：%s' %(nrows ,  ncols))
        # 第二行开始

        for rownum in range(1, nrows):
            row = table.row_values(rownum)

            parent_id = 0
            cate_data = dict()
            cate_exit_data = dict()
            cate_data['keywords'] = ''
            cate_data['cat_desc'] = ''
            cate_data['template_file'] = ''
            cate_data['measure_unit'] = ''
            cate_data['style'] = ''
            cate_data['category_thumb'] = ''
            cate_data['category_img'] = ''
            cate_data['original_img'] = ''

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

            cate_exit_data['cat_name'] = first_name
            cate_exit_data['level'] = 1
            cate_exit_data['vehicle_code'] = vehicle_code
            # 插入或更新数据
            others_sql = ' and cat_id >'+str(final_id)
            first_cate_id = self.dao.insert_or_update_without_exit(self.sql_table, cate_data, cate_exit_data, 'cat_id', others_sql)
            # ===================================存二级分类==========================
            cate_data['cat_name'] = second_name
            cate_data['parent_id'] = first_cate_id
            cate_data['level'] = 2
            cate_data['code'] = second_code
            if third_name == '':
                cate_data['is_leaf'] = 1

            cate_exit_data['cat_name'] = second_name
            cate_exit_data['level'] = 2
            cate_exit_data['vehicle_code'] = vehicle_code
            # 插入或更新数据
            others_sql = ' and cat_id >'+str(final_id)
            second_cate_id = self.dao.insert_or_update_without_exit(self.sql_table, cate_data, cate_exit_data, 'cat_id', others_sql)

            # ===================================存三级分类==========================
            if third_name != '':
                cate_data['cat_name'] = third_name
                cate_data['parent_id'] = second_cate_id
                cate_data['level'] = 3
                cate_data['is_leaf'] = 1
                cate_data['code'] = third_code

                cate_exit_data['cat_name'] = third_name
                cate_exit_data['level'] = 3
                cate_exit_data['vehicle_code'] = vehicle_code
                # 插入或更新数据
                others_sql = ' and cat_id >'+str(final_id)

                replace = True
                third_cate_id = 0
                #   判断其父id有无改变，若改变了，则在对应表中也要改变
                value_list = list()
                for key, value in cate_exit_data.items():
                    value_list.append(' %s = "%s" ' % (key, str(value)))
                select_sql = 'select cat_id,parent_id from %s where %s' % (self.sql_table, 'and'.join(value_list))
                select_result = self.dao.db.get_data(select_sql)
                if select_result:
                    parent = select_result[0]['parent_id']
                    if parent != second_cate_id:
                        replace = False
                    key_id = select_result[0]['cat_id']
                    where_dict = dict()
                    where_dict['cat_id'] = key_id
                    self.dao.update_temple(self.sql_table, cate_data, where_dict)
                    third_cate_id = key_id
                else:
                    third_cate_id = self.dao.insert_temple(self.sql_table, cate_data)

                if vehicle_code == 'C':
                    if third_name != '':
                        self.save_relation(third_name, third_cate_id, second_cate_id, self.sql_table, self.sql_relation_table, final_id, replace)
                    else:
                        self.save_relation(second_name, second_cate_id, first_cate_id, self.sql_table, self.sql_relation_table,final_id, replace)

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

            if third_name == '':
                part_data['cate_id'] = second_cate_id
                part_data['cate_parent_id'] = first_cate_id
            else:
                part_data['cate_id'] = third_cate_id
                part_data['cate_parent_id'] = second_cate_id

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
        # 结束循环，存update语句于text文件中
        self.save_string_files(file_name)




# 导入excle所在的文件夹

# excle = r'D:\PythonExcle\cate\0603_test.xls'
# # 博士
# final_id = 1233
# # excle = r'D:\PythonExcle\cateExcle-boshi.xlsx'
#
# cate = Cate()
# cate.main(excle, str(final_id))













