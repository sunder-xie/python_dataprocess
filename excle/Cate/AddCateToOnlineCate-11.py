# encoding=utf-8
# 2015.11.26 尾部添加数据到电商分类表中
__author__ = 'zxg'

import sys

from util import CrawlDao, FileUtil, StringUtil

reload(sys)
sys.setdefaultencoding("utf-8")


class DataTOOnline:
    def __init__(self):
        self.dao = CrawlDao.CrawlDao()

        self.sql_category_online_table = 'db_category_dian'
        self.sql_category_data_table = 'db_category_data'
        self.sql_category_cat_label_table = 'db_category_cat_label'

        # 新增的数据 id:cate
        self.new_data_dict = dict()
        # pid: list(id)
        self.new_data_pid_dict = dict()
        new_data_sql = "select cat_id,cat_name,parent_id,cat_kind,cat_level,code,vehicle_code from " + self.sql_category_data_table + " where is_deleted= 'N'"
        new_data_array = self.dao.db.get_data(new_data_sql)
        for new_data in new_data_array:
            cat_id = int(new_data['cat_id'])
            parent_id = int(new_data['parent_id'])
            cate_map = {
                'cat_name': new_data['cat_name'],
                'cat_kind': new_data['cat_kind'],
                'cat_level': new_data['cat_level'],
                'cat_code': new_data['code'],
                'vehicle_code': new_data['vehicle_code'],
                'category_thumb': '',
                'category_img': '',
                'original_img': '',
                'style': ''
            }
            self.new_data_dict[cat_id] = cate_map
            if parent_id in self.new_data_pid_dict.keys():
                cat_list = list(self.new_data_pid_dict[parent_id])
                cat_list.append(cat_id)
                self.new_data_pid_dict[parent_id] = cat_list
            else:
                cat_list = list()
                cat_list.append(cat_id)
                self.new_data_pid_dict[parent_id] = cat_list

                # part_lable:cat_id:label
                # self.cat_label_dict = self.get_cat_label()

                # self.label_id_name_dict = {'1': u'字标', '2': u'灯泡', '3': u'四滤'}

    # def get_cat_label(self):
    #     cat_label_dict = dict()
    #
    #     part_id_dict = dict()
    #     part_sql = "select id,third_cate_id from db_category_part where is_deleted = 'N'"
    #     part_data_array = self.dao.db.get_data(part_sql)
    #     for part_data in part_data_array:
    #         part_id_dict[part_data['id']] = part_data['third_cate_id']
    #
    #     part_label_sql = "select label_id,part_id from db_category_part_label"
    #     part_label_array = self.dao.db.get_data(part_label_sql)
    #     for part_label_data in part_label_array:
    #         label_id = part_label_data['label_id']
    #         part_id = part_label_data['part_id']
    #
    #         third_cat_id = int(part_id_dict[part_id])
    #         cat_label_dict[third_cat_id] = label_id
    #
    #     return cat_label_dict

    def main(self):
        tart_num = 3000
        is_star = True
        # 一级存入
        first_cat_list = self.new_data_pid_dict[0]
        for first_cat_id in first_cat_list:
            first_cat_data = self.new_data_dict[first_cat_id]
            if is_star:
                first_cat_data['cat_id'] = tart_num
                is_star = False
            new_first_cat_id = self.dao.insert_temple(self.sql_category_online_table, first_cat_data)
            # 二级存入
            second_cat_list = self.new_data_pid_dict[first_cat_id]
            for second_cat_id in second_cat_list:
                second_cat_data = self.new_data_dict[second_cat_id]
                second_cat_data['parent_id'] = new_first_cat_id
                new_second_cat_id = self.dao.insert_temple(self.sql_category_online_table, second_cat_data)
                # 三级存入
                third_cat_list = self.new_data_pid_dict[second_cat_id]
                for third_cat_id in third_cat_list:
                    third_cat_data = self.new_data_dict[third_cat_id]
                    third_cat_data['parent_id'] = new_second_cat_id
                    vehicle_code = third_cat_data['vehicle_code']
                    if vehicle_code == 'CH':
                        third_cat_data['vehicle_code'] = 'C'
                        self.dao.insert_temple(self.sql_category_online_table, third_cat_data)
                        third_cat_data['vehicle_code'] = 'H'
                        self.dao.insert_temple(self.sql_category_online_table, third_cat_data)

                    else:
                        self.dao.insert_temple(self.sql_category_online_table, third_cat_data)

                        # 若老的cat存在label对应关系，则此处也存入对应关系
                        # if third_cat_id in self.cat_label_dict.keys():
                        #     label_id = str(self.cat_label_dict[third_cat_id])
                        #     cat_label_data = {
                        #         'label_id': label_id,
                        #         'label_name': self.label_id_name_dict[label_id],
                        #         'cat_id': new_third_cat_id
                        #     }
                        #     self.dao.insert_temple(self.sql_category_cat_label_table, cat_label_data)


test = DataTOOnline()
test.main()
