# encoding=utf-8
# 配件库配件处理为适合商品中心的临时数据

__author__ = 'zxg'

import sys

from util import CrawlDao

reload(sys)
sys.setdefaultencoding("utf-8")


class partToData:
    def __init__(self):
        # self.athena_dao = CrawlDao.CrawlDao('dataserver')
        self.athena_dao = CrawlDao.CrawlDao('athena_center')
        self.part_dao = CrawlDao.CrawlDao('modeldatas')

        #
        # goods_uuId:goods_data
        self.part_goods_data = dict()

    def init_part_goods(self):

        athena_cat_dict = dict()
        athena_third_key_list = list()
        athena_cat_sql = "select cat_id,cat_code,cat_level,parent_id,vehicle_code from center_category where is_deleted = 'N'"
        athena_cat_array = self.athena_dao.db.get_data(athena_cat_sql)
        for athena_cat_data in athena_cat_array:
            cat_id = str(athena_cat_data['cat_id'])
            cat_level = str(athena_cat_data['cat_level'])
            vehicle_code = str(athena_cat_data['vehicle_code'])

            cat_key = cat_level + str(athena_cat_data['cat_code']) + str(athena_cat_data['parent_id'])
            if cat_level == '3' and vehicle_code == 'H':
                continue
            if cat_level == '3':
                athena_third_key_list.append(cat_key)
            athena_cat_dict[cat_key] = cat_id


        part_base_id_dict = dict()
        part_base_code_dict = dict()
        monkey_part_sql = "select id,part_name,first_cat_id,second_cat_id,third_cat_id,sum_code from db_category_part"
        monkey_part_array = self.part_dao.db.get_data(monkey_part_sql)
        for monkey_part_data in monkey_part_array:
            part_id = str(monkey_part_data['id'])
            part_name = str(monkey_part_data['part_name'])
            part_key = part_name + str(monkey_part_data['first_cat_id']) + str(
                monkey_part_data['second_cat_id']) + str(monkey_part_data['third_cat_id'])
            part_base_id_dict[part_key] = part_id
            part_base_code_dict[part_id] = str(monkey_part_data['sum_code'])

        base_uuId_dict = dict()
        base_uuId_list = list()
        part_base_goods_sql = "select uuId,oe_number,part_name,first_cate_id,second_cate_id,third_cate_id from db_monkey_part_goods_base"
        part_base_array = self.part_dao.db.get_data(part_base_goods_sql)
        for part_base_data in part_base_array:
            base_uuId = str(part_base_data['uuId'])
            oe_number = str(part_base_data['oe_number'])
            part_name = str(part_base_data['part_name'])

            base_uuId_list.append(base_uuId)

            part_key = part_name + str(part_base_data['first_cate_id']) + str(
                part_base_data['second_cate_id']) + str(part_base_data['third_cate_id'])
            part_id = part_base_id_dict[part_key]

            sum_code = part_base_code_dict[part_id]
            first_code = sum_code[0:2]
            second_code = sum_code[2:4]
            third_code = sum_code[4:7]
            first_key = '1' + first_code + '0'
            first_id = athena_cat_dict[first_key]
            second_id = athena_cat_dict['2' + second_code + first_id]

            third_key = '3' + third_code + second_id
            if third_key not in athena_third_key_list:
                print '=========wrong part=========%s' % base_uuId
                third_id = '0'
            else:
                third_id = athena_cat_dict[third_key]

            temp_data = {'oe_number': oe_number, 'part_id': part_id, 'part_name': part_name,
                         'center_first_cate_id': first_id, 'center_second_cate_id': second_id,
                         'center_third_cate_id': third_id}
            base_uuId_dict[base_uuId] = temp_data

        insert_list = list()
        part_goods_sql = "select uuId,goods_base_id,remarks from db_monkey_part_goods"
        part_goods_array = self.part_dao.db.get_data(part_goods_sql)
        for part_goods_data in part_goods_array:
            uuId = str(part_goods_data['uuId'])
            goods_base_id = str(part_goods_data['goods_base_id'])
            remarks = str(part_goods_data['remarks'])

            if goods_base_id in base_uuId_list:
                temp_data = dict(base_uuId_dict[goods_base_id])
                temp_data['uuId'] = uuId
                temp_data['remarks'] = remarks.replace('"',"'")
                insert_list.append(temp_data)
                if len(insert_list) > 1000:
                    self.save_list(insert_list)
                    insert_list = list()

        if len(insert_list) > 0:
            self.save_list(insert_list)


    def save_list(self, insert_list):
        self.part_dao.insert_batch_temple('temp_monkey_part_goods',insert_list)


partToData = partToData()
partToData.init_part_goods()

