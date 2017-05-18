# encoding=utf-8
# 配件库导入中心配件库，作为原始数据使用

__author__ = 'zxg'

import sys

from util import CrawlDao

reload(sys)
sys.setdefaultencoding("utf-8")


class partToData:
    def __init__(self):
        self.athena_dao = CrawlDao.CrawlDao('dev_dataserver')
        # self.athena_dao = CrawlDao.CrawlDao('athena_center')
        self.part_dao = CrawlDao.CrawlDao('modeldatas')

        # goods_uuId:goods_data
        self.part_goods_data = dict()
        self.init_part_goods()

        # pic_uuId:pic_data
        self.part_pic_data = dict()
        self.init_pic()

        # oe:data
        self.center_goods_dict = dict()
        # part_goods_uuid:athena_goos_id
        self.center_part_goods_dict = dict()
        # liyangid:onlinecar_data
        self.liyang_dict = dict()

        # goods_id-car_id
        self.has_goods_car = set()
        # goods_car insert list
        self.relaton_insert_list = list()

    def init_part_goods(self):
        goods_sql = "select uuId,part_name,part_id,remarks,oe_number,center_first_cate_id,center_second_cate_id,center_third_cate_id from temp_monkey_part_goods"
        goods_array = self.part_dao.db.get_data(goods_sql)
        for goods_data in goods_array:
            self.part_goods_data[str(goods_data['uuId'])] = goods_data

    def init_pic(self):
        pic_sql = "select uuId,picture_num,picture_index from db_monkey_part_picture"
        pic_array = self.part_dao.db.get_data(pic_sql)
        for pic_data in pic_array:
            self.part_pic_data[str(pic_data['uuId'])] = pic_data

    def main(self):
        all_uuid_list = self.part_goods_data.keys()
        final_relation_id = '0'
        while True:
            is_final = True
            relation_sql = "select id,goods_id,pic_id,liyang_id from db_monkey_part_liyang_relation where id > " + final_relation_id + ' limit 10000'
            relation_array = self.part_dao.db.get_data(relation_sql)
            for relation_data in relation_array:
                id = str(relation_data['id'])
                goods_id = str(relation_data['goods_id'])
                pic_id = str(relation_data['pic_id'])
                liyang_id = str(relation_data['liyang_id'])

                if goods_id not in all_uuid_list:
                    continue
                center_goods_id = self.process_goods(goods_id)
                self.process_goods_car_relation(center_goods_id, liyang_id, pic_id)
                is_final = False
                final_relation_id = id

            if is_final:
                # 遍历完全
                break

        if len(self.relaton_insert_list) > 0:
            self.save_relation(self.relaton_insert_list)

    def process_goods_car_relation(self, center_goods_id, liyang_id, pic_id):
        relation_data = dict()
        relation_data['goods_id'] = center_goods_id

        pic_data = dict(self.part_pic_data[pic_id])
        picture_num = pic_data['picture_num']
        picture_index = pic_data['picture_index']
        relation_data['epc_pic'] = picture_num
        relation_data['epc_index'] = picture_index

        if liyang_id in self.liyang_dict.keys():
            online_data = dict(self.liyang_dict[liyang_id])
        else:
            liyang_sql = "select brand,brand_id,series,series_id,model,model_id,power,power_id,year,year_id,car_models,car_models_id from db_car_all where l_id = '" + liyang_id + "' limit 1"
            online_data = self.part_dao.db.get_data(liyang_sql)[0]
            self.liyang_dict[liyang_id] = online_data

        relation_data['car_id'] = str(online_data['car_models_id'])
        relation_data['car_name'] = str(online_data['car_models'])
        relation_data['car_brand_id'] = str(online_data['brand_id'])
        relation_data['car_brand'] = str(online_data['brand'])
        relation_data['car_series_id'] = str(online_data['series_id'])
        relation_data['car_series'] = str(online_data['series'])
        relation_data['car_model_id'] = str(online_data['model_id'])
        relation_data['car_model'] = str(online_data['model'])
        relation_data['car_power_id'] = str(online_data['power_id'])
        relation_data['car_power'] = str(online_data['power'])
        relation_data['car_year_id'] = str(online_data['year_id'])
        relation_data['car_year'] = str(online_data['year'])

        key = str(center_goods_id) + "-" + str(online_data['car_models_id'])
        if key in self.has_goods_car:
            return
        else:
            self.relaton_insert_list.append(relation_data)
            self.has_goods_car.add(key)
            if len(self.relaton_insert_list) > 5000:
                self.save_relation(self.relaton_insert_list)
                self.relaton_insert_list = list()

    # 处理配件存入商品中心
    def process_goods(self, goods_id):

        if goods_id in self.center_part_goods_dict.keys():
            center_goods_id = self.center_part_goods_dict[goods_id]
        else:
            goods_data = dict(self.part_goods_data[goods_id])
            oe_number = goods_data['oe_number']
            remarks = goods_data['remarks']
            part_id = goods_data['part_id']
            part_name = goods_data['part_name']
            first_cate_id = goods_data['center_first_cate_id']
            second_cate_id = goods_data['center_second_cate_id']
            third_cate_id = goods_data['center_third_cate_id']

            is_new = True
            if oe_number in self.center_goods_dict.keys():
                is_new = False
                base_id = 0
            else:
                base_id = self.save_goods_base(part_id, part_name, first_cate_id, second_cate_id, third_cate_id)

            center_goods_id = self.save_or_update_goods(base_id, oe_number, remarks, is_new)
            self.center_part_goods_dict[goods_id] = center_goods_id

        return center_goods_id

    # ==========save ============
    def save_relation(self, insert_list):
        self.athena_dao.insert_batch_temple("center_goods_car_relation", insert_list)

    def save_goods_base(self, part_id=0, part_name='', first_cate_id='', second_cate_id='', third_cate_id=''):
        save_data = {
            'part_id': part_id,
            'part_name': part_name,
            'first_cate_id': first_cate_id,
            'second_cate_id': second_cate_id,
            'third_cate_id': third_cate_id,
        }

        base_id = self.athena_dao.insert_temple("center_goods_base", save_data)
        return base_id

    def save_or_update_goods(self, base_id, oe_number, remarks, is_new=True):
        if not is_new:
            update_data = dict(self.center_goods_dict[oe_number])
            goods_id = update_data['id']
            old_remarks = update_data['remarks']
            if old_remarks != "" and remarks not in old_remarks:
                update_remarks = old_remarks + "," + remarks
                self.athena_dao.update_temple('center_goods', {'remarks': update_remarks}, {'oe_number': oe_number})
        else:

            save_data = {
                'goods_base_id': base_id,
                'oe_number': oe_number,
                'remarks': remarks
            }
            goods_id = self.athena_dao.insert_temple('center_goods', save_data)
            self.center_goods_dict[oe_number] = {'id': goods_id, 'remarks': remarks}

        return goods_id


partToData = partToData()
partToData.main()
