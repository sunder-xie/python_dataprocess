# encoding=utf-8
# 每月 从 数据平台 获得数据 新增到 商品中心 sql
# 若数据库 数据进行更改 每次重新从线上导 center_Car center_Car_Cat center_goods center_goods_base center_goods_car
#
import os

__author__ = 'zxg'

import sys

import datetime

reload(sys)
sys.setdefaultencoding("utf-8")

from util import CrawlDao


class MonkeyToCenter:
    def __init__(self):
        # linux
        # self.athena_test_dao = CrawlDao.CrawlDao('dev_dataserver', 'test')
        self.athena_test_dao = CrawlDao.CrawlDao('dataserver', 'online_cong')
        self.monkey_dao = CrawlDao.CrawlDao('modeldatas', 'online_cong')
        self.liyang_dao = CrawlDao.CrawlDao('dataserver', 'online_cong')
        # local
        # self.athena_test_dao = CrawlDao.CrawlDao('athena_center', 'local')
        # self.monkey_dao = CrawlDao.CrawlDao('modeldatas', 'local')
        # self.liyang_dao = CrawlDao.CrawlDao('athena_center', 'local')
        # 初始化存储的id
        # self.start_center_goods_base_id = self.start_center_goods_id = '0'

        self.center_goods_base_final_id = 0
        self.center_goods_final_id = 0

        # 更新的语句{id:string}
        self.update_dict = dict()
        # 插入语句
        self.goods_car_data_list = list()

        self.goods_insert_list = list()
        self.goods_base_data_list = list()
        self.goods_data_list = list()

        self.car_cat_list = list()
        self.car_cat_data_list = list()

        # 新增的car_id
        self.center_new_car_id_list = list()
        self.center_car_data_list = list()


        # ===========基础数据====================
        # monkey_category初始化,id:
        self.monkey_cat_dict = dict()
        monkey_cat_array = self.monkey_dao.db.get_data("select cat_id,cat_code from db_category where is_deleted = 'N'")
        for monkey_cat_data in monkey_cat_array:
            self.monkey_cat_dict[str(monkey_cat_data['cat_id'])] = str(monkey_cat_data['cat_code'])

        # center_category
        self.center_cat_dict = dict()
        self.center_cat_id_dict = dict()
        center_cat_array = self.liyang_dao.db.get_data(
            "select cat_id,cat_code,cat_name,cat_pic,first_letter from center_category where is_deleted = 'N'")
        for center_cat_data in center_cat_array:
            self.center_cat_dict[str(center_cat_data['cat_code'])] = center_cat_data
            self.center_cat_id_dict[str(center_cat_data['cat_id'])] = center_cat_data

        # center_part
        self.center_part_dict = dict()
        center_part_array = self.liyang_dao.db.get_data(
            "select id,part_name,sum_code from center_part where is_deleted = 'N'")
        for center_part_data in center_part_array:
            sum_code = str(center_part_data['sum_code'])
            part_name = str(center_part_data['part_name'])
            id = str(center_part_data['id'])
            save_code = sum_code[:-2] + part_name
            self.center_part_dict[save_code] = id

        # center_goods
        self.center_goods_dict = dict()
        center_goods_array = self.liyang_dao.db.get_data(
            "select id,oe_number,remarks from center_goods where is_deleted = 'N'")
        for center_goods_data in center_goods_array:
            self.center_goods_dict[str(center_goods_data['oe_number'])] = center_goods_data
            self.center_goods_final_id = int(center_goods_data['id'])

        # center_goods_base final id
        center_goods_base_array = self.liyang_dao.db.get_data(
            "select id from center_goods_base ORDER by id desc limit 1")
        self.center_goods_base_final_id = int(center_goods_base_array[0]['id'])

        # ============获取或存储的临时变量===========
        # pic-id:data
        self.pic_dict = dict()
        # goods-id:data
        self.goods_dict = dict()
        self.goods_base_dict = dict()
        # liyangid:onlinecar_data
        self.liyang_dict = dict()
        # goods_id-car_id
        self.has_goods_car = set()

        # ======center_car_cat=======
        # uuId:base_uuId
        self.monkey_goods_uuId_base = dict()
        self.monkey_goods_uuId_base_cat = dict()
        # car_id+third_cat_id
        self.athena_car_cat_list = list()
        athena_car_cat_array = self.athena_test_dao.db.get_data(
            "select car_id,third_cat_id from center_car_cate_relation")
        for athena_car_cat_data in athena_car_cat_array:
            car_cat_key = str(athena_car_cat_data['car_id']) + "-" + str(athena_car_cat_data['third_cat_id'])
            self.athena_car_cat_list.append(car_cat_key)

        # ========center_car ==========
        self.center_car_id_list = list()
        center_car_array = self.athena_test_dao.db.get_data("select id from center_car")
        for center_car_data in center_car_array:
            self.center_car_id_list.append(str(center_car_data['id']))

        # 实际online car_id 和 pid
        self.true_car_id_dict = dict()
        # id:data
        self.true_car_dict = dict()
        true_car_array = self.liyang_dao.db.get_data("select id,name,power,level,first_word,sort,pid,"
                                                     "model,series,brand,company,country,car_type,"
                                                     "car_level,import_info,logo,is_hot,year,engine_type,"
                                                     "chassis_number,guide_price "
                                                     "from db_car_category"
                                                     )
        for true_data in true_car_array:
            id = str(true_data['id'])
            pid = str(true_data['pid'])

            self.true_car_id_dict[id] = pid
            self.true_car_dict[id] = true_data

    def main(self, insert_address, update_address):
        print '===== start center_goods_id:%s,center_goods_base_id:%s =====' % (
            str(self.center_goods_final_id), str(self.center_goods_base_final_id))
        self.first_from_monkey_to_athena()
        self.second_center_car()
        self.final_write_sql(insert_address, update_address)

        print '====end ============'

    # monkey数据处理为athena数据
    def first_from_monkey_to_athena(self):
        recent_up_time_sql = "select gmt_create from center_car order by gmt_create desc limit 1"
        recent_up_time = str(self.athena_test_dao.db.get_data(recent_up_time_sql)[0]['gmt_create'])

        # 查找新增的车型
        more_liyang_sql = "select id,goods_id,pic_id,liyang_id from db_monkey_part_liyang_relation where gmt_create > '" + recent_up_time + "'"
        more_liyang_array = self.monkey_dao.db.get_data(more_liyang_sql)
        for more_liyang_data in more_liyang_array:
            goods_id = str(more_liyang_data['goods_id'])
            pic_id = str(more_liyang_data['pic_id'])
            liyang_id = str(more_liyang_data['liyang_id'])

            print more_liyang_data
            relation_data = self.get_online_car_relation_by_liyang(liyang_id)
            pic_data = self.get_pic_by_id(pic_id)
            picture_num = pic_data['picture_num']
            picture_index = pic_data['picture_index']
            relation_data['epc_pic'] = picture_num
            relation_data['epc_index'] = picture_index

            center_goods_id = self.get_goods_by_id(goods_id)
            relation_data['goods_id'] = center_goods_id

            # 记录center_car_cat
            cat_data = self.monkey_goods_uuId_base_cat[self.monkey_goods_uuId_base[goods_id]]
            car_id = str(relation_data['car_id'])
            self.save_center_car_cat(car_id, str(cat_data['first_cat_id']), str(cat_data['second_cat_id']),
                                     str(cat_data['third_cat_id']))

            # 存center_goods_car
            key = str(center_goods_id) + "-" + str(relation_data['car_id'])
            if key in self.has_goods_car:
                pass
            else:
                # 保存一份到 center_car_dict 中
                self.center_new_car_id_list.append(car_id)

                self.goods_car_data_list.append(relation_data)
                self.has_goods_car.add(key)

    def second_center_car(self):
        for car_id in self.center_new_car_id_list:
            if car_id in self.center_car_id_list:
                # 该车型已存在在 数据库中
                continue
            car_data = self.true_car_dict[car_id]
            # car_data['model_id'] = model_id
            self.center_car_data_list.append(car_data)

            pid_list = list(self.get_pid_list_by_online_car_id(car_id))
            for pid in pid_list:
                if pid in self.center_car_id_list:
                    # 该车型已存在在 数据库中
                    continue
                car_parent_data = self.true_car_dict[pid]
                self.center_car_data_list.append(car_parent_data)

    # 导出sql语句
    def final_write_sql(self, insert_address, update_address):

        insert_file_object = open(insert_address, 'w')

        max_num = 3000
        try:
            insert_file_object.writelines("SET unique_checks=0;SET foreign_key_checks=0;set autocommit=0;\n")
            # center_goods_base
            base_list = list()
            for goods_base_data in self.goods_base_data_list:
                base_list.append(goods_base_data)
                if len(base_list) > max_num:
                    insert_file_object.writelines(self.get_batch_sql('center_goods_base', base_list))
                    insert_file_object.writelines(";\n")
                    base_list = list()

            if len(base_list) > 0:
                insert_file_object.writelines(self.get_batch_sql('center_goods_base', base_list))
                insert_file_object.writelines(";\n")
                base_list = list()

            # center_goods
            goods_list = list()
            for goods_data in self.goods_data_list:
                goods_list.append(goods_data)
                if len(goods_list) > max_num:
                    insert_file_object.writelines(self.get_batch_sql('center_goods', goods_list))
                    insert_file_object.writelines(";\n")
                    goods_list = list()

            if len(goods_list) > 0:
                insert_file_object.writelines(self.get_batch_sql('center_goods', goods_list))
                insert_file_object.writelines(";\n")
                goods_list = list()

            # cat
            car_cat_list = list()
            for car_cat_data in self.car_cat_data_list:
                car_cat_list.append(car_cat_data)
                if len(car_cat_list) > max_num:
                    insert_file_object.writelines(self.get_batch_sql('center_car_cate_relation', car_cat_list))
                    insert_file_object.writelines(";\n")
                    car_cat_list = list()

            if len(car_cat_list) > 0:
                insert_file_object.writelines(self.get_batch_sql('center_car_cate_relation', car_cat_list))
                insert_file_object.writelines(";\n")
                car_cat_list = list()

            # center_car
            car_list = list()
            for car_data in self.center_car_data_list:
                car_list.append(car_data)
                if len(car_list) > max_num:
                    insert_file_object.writelines(self.get_batch_sql('center_car', car_list))
                    insert_file_object.writelines(";\n")
                    car_list = list()

            if len(car_list) > 0:
                insert_file_object.writelines(self.get_batch_sql('center_car', car_list))
                insert_file_object.writelines(";\n")
                car_list = list()

            # center_goods_car
            goods_car_list = list()
            for goods_car_data in self.goods_car_data_list:
                goods_car_list.append(goods_car_data)
                if len(goods_car_list) > max_num:
                    insert_file_object.writelines(self.get_batch_sql('center_goods_car', goods_car_list))
                    insert_file_object.writelines(";\n")
                    goods_car_list = list()

            if len(goods_car_list) > 0:
                insert_file_object.writelines(self.get_batch_sql('center_goods_car', goods_car_list))
                insert_file_object.writelines(";\n")
                goods_car_list = list()
            insert_file_object.writelines("commit;\n")

        finally:
            insert_file_object.close()

        update_file_object = open(update_address, 'w')
        try:
            update_file_object.writelines("SET unique_checks=0;SET foreign_key_checks=0;set autocommit=0;\n")
            update_file_object.writelines("select @now_time := now();\n")

            for key, value in self.update_dict.iteritems():
                update_file_object.writelines(value + ";\n")

            update_file_object.writelines("commit;\n")
        finally:
            update_file_object.close()

    # ==========================二级方法===================

    # 根据car——id 递归获得父id
    def get_pid_list_by_online_car_id(self, car_id, pid_list=list()):
        pid = self.true_car_id_dict[car_id]
        if pid == "0":
            return pid_list
        else:
            pid_list.append(pid)
            return self.get_pid_list_by_online_car_id(pid, pid_list)

    # 根据力洋Id拼接relation对象
    def get_online_car_relation_by_liyang(self, liyang_id=""):
        if liyang_id in self.liyang_dict.keys():
            online_data = dict(self.liyang_dict[liyang_id])
        else:
            liyang_sql = "select brand,brand_id,series,series_id,model,model_id,power,power_id,year,year_id,car_models,car_models_id from db_car_all where l_id = '" + liyang_id + "' limit 1"
            try:
                online_data = self.liyang_dao.db.get_data(liyang_sql)[0]
            except:
                self.liyang_dao = CrawlDao.CrawlDao('dataserver', 'online_cong')
                online_data = self.liyang_dao.db.get_data(liyang_sql)[0]

            self.liyang_dict[liyang_id] = online_data

        relation_data = {'car_id': str(online_data['car_models_id']), 'car_name': str(online_data['car_models']),
                         'car_brand_id': str(online_data['brand_id']), 'car_brand': str(online_data['brand']),
                         'car_series_id': str(online_data['series_id']), 'car_series': str(online_data['series']),
                         'car_model_id': str(online_data['model_id']), 'car_model': str(online_data['model']),
                         'car_power_id': str(online_data['power_id']), 'car_power': str(online_data['power']),
                         'car_year_id': str(online_data['year_id']), 'car_year': str(online_data['year'])}
        return relation_data

    # 获得图片对象
    def get_pic_by_id(self, pic_id=""):
        if pic_id in self.pic_dict.keys():
            pic_data = self.pic_dict[pic_id]
        else:
            try:
                pic_data = self.monkey_dao.db.get_data(
                    "select picture_num,picture_index from db_monkey_part_picture where uuId = '" + pic_id + "'")[0]
            except:
                self.monkey_dao = CrawlDao.CrawlDao('modeldatas', 'online_cong')
                pic_data = self.monkey_dao.db.get_data(
                    "select picture_num,picture_index from db_monkey_part_picture where uuId = '" + pic_id + "'")[0]

            self.pic_dict[pic_id] = pic_data

        return pic_data

    # 获得 center_goods的主键id
    def get_goods_by_id(self, goods_id=""):
        if goods_id in self.goods_dict.keys():
            center_goods_id = self.goods_dict[goods_id]
        else:
            goods_sql = "select goods_base_id,remarks from db_monkey_part_goods where uuId = '" + goods_id + "'"
            try:
                this_data = self.monkey_dao.db.get_data(goods_sql)[0]
            except:
                self.monkey_dao = CrawlDao.CrawlDao('modeldatas', 'online_cong')
                this_data = self.monkey_dao.db.get_data(goods_sql)[0]

            goods_base_id = str(this_data['goods_base_id'])
            remarks = str(this_data['remarks']).replace("，", ",").replace('"', "'").replace("'", "")
            center_goods_data = self.get_base_goods_by_id(goods_base_id)

            # 为center_car_cat服务
            self.monkey_goods_uuId_base[goods_id] = goods_base_id

            center_goods_id = str(center_goods_data['id'])
            oe_number = str(center_goods_data['oe_number'])
            if center_goods_id == '0':
                # 新增
                center_goods_data['remarks'] = remarks
                center_goods_data.pop('id')
                try:
                    center_goods_result = self.athena_test_dao.boolean_exit('center_goods', {'oe_number': oe_number})
                    if center_goods_result:
                        center_goods_id = center_goods_result[0]['id']
                        center_goods_data['id'] = center_goods_id
                    else:
                        self.center_goods_final_id += 1
                        center_goods_data['id'] = self.center_goods_final_id
                        self.goods_data_list.append(center_goods_data)
                except:
                    self.athena_test_dao = CrawlDao.CrawlDao('dataserver', 'online_cong')
                    center_goods_result = self.athena_test_dao.boolean_exit('center_goods', {'oe_number': oe_number})
                    if center_goods_result:
                        center_goods_id = center_goods_result[0]['id']
                        center_goods_data['id'] = center_goods_id
                    else:
                        self.center_goods_final_id += 1
                        center_goods_data['id'] = self.center_goods_final_id
                        self.goods_data_list.append(center_goods_data)

                self.center_goods_dict[oe_number] = center_goods_data
            else:
                # 判断是否需要更新
                center_goods_id = str(center_goods_data['id'])
                mysql_remarks = str(center_goods_data['remarks']).replace("，", ",").replace('"', "'").replace("'", "")

                new_remarks_list = list()
                mysql_remarks_array = mysql_remarks.split(",")
                remarks_array = remarks.split(",")
                for mysql_remarks_value in mysql_remarks_array:
                    if mysql_remarks_value not in new_remarks_list:
                        new_remarks_list.append(mysql_remarks_value)
                for remarks_value in remarks_array:
                    if remarks_value not in new_remarks_list:
                        new_remarks_list.append(remarks_value)

                if len(new_remarks_list) > 0:
                    new_remarks = ','.join(new_remarks_list)
                    if new_remarks != mysql_remarks:
                        center_goods_data['remarks'] = new_remarks
                        update_sql = 'update center_goods set remarks = "' + new_remarks + '",gmt_modified = now() where id = "' + center_goods_id + '"'

                        self.update_dict[center_goods_id] = update_sql
                        self.center_goods_dict[oe_number] = center_goods_data

            self.goods_dict[goods_id] = center_goods_id

        return center_goods_id

    def get_base_goods_by_id(self, goods_base_id=""):
        if goods_base_id in self.goods_base_dict.keys():
            center_goods_data = self.goods_base_dict[goods_base_id]
        else:
            base_sql = "select oe_number,part_name,first_cate_id,second_cate_id,third_cate_id from db_monkey_part_goods_base where uuId = '" + goods_base_id + "'"
            try:
                base_data = self.monkey_dao.db.get_data(base_sql)[0]
            except:
                self.monkey_dao = CrawlDao.CrawlDao('modeldatas', 'online_cong')
                base_data = self.monkey_dao.db.get_data(base_sql)[0]

            oe_number = str(base_data['oe_number'])
            # goods_base
            part_name = str(base_data['part_name'])
            first_cate_id = str(base_data['first_cate_id'])
            second_cate_id = str(base_data['second_cate_id'])
            third_cate_id = str(base_data['third_cate_id'])

            fist_code = self.monkey_cat_dict[first_cate_id]
            second_code = self.monkey_cat_dict[second_cate_id]
            third_code = self.monkey_cat_dict[third_cate_id]

            new_first_data = self.center_cat_dict[fist_code]
            new_second_data = self.center_cat_dict[fist_code + "." + second_code]
            new_third_data = self.center_cat_dict[fist_code + "." + second_code + "." + third_code]

            new_part_id = self.center_part_dict[fist_code + second_code + third_code + part_name]

            goods_base_data = {
                'first_cat_id': str(new_first_data['cat_id']),
                'second_cat_id': str(new_second_data['cat_id']),
                'third_cat_id': str(new_third_data['cat_id']),
                'first_cat_name': str(new_first_data['cat_name']),
                'second_cat_name': str(new_second_data['cat_name']),
                'third_cat_name': str(new_third_data['cat_name']),
                'part_id': new_part_id,
                'part_name': part_name
            }
            # 为center_car_cat服务
            self.monkey_goods_uuId_base_cat[goods_base_id] = goods_base_data

            # 判断此oe是否存过，若存过，直接返回
            if oe_number in self.center_goods_dict.keys():
                center_goods_data = self.center_goods_dict[oe_number]
            else:
                self.center_goods_base_final_id += 1
                # try:
                #
                #     center_goods_base_id = self.athena_test_dao.insert_temple('center_goods_base', goods_base_data)
                # except:
                #     self.athena_test_dao = CrawlDao.CrawlDao('dataserver', 'online_cong')
                #     center_goods_base_id = self.athena_test_dao.insert_temple('center_goods_base', goods_base_data)

                goods_base_data['id'] = self.center_goods_base_final_id
                self.goods_base_data_list.append(goods_base_data)
                # center_goods 上一层处理
                center_goods_data = {
                    'id': '0',
                    'remarks': '',
                    'oe_number': oe_number,
                    'oe_number_trim': oe_number.replace("-", "").replace("—", ""),
                    'goods_base_id': self.center_goods_base_final_id,
                    'third_cat_id': str(new_third_data['cat_id']),
                    'part_name': part_name
                }

            self.goods_base_dict[goods_base_id] = center_goods_data

        return center_goods_data

    # ==========save ============
    def save_center_car_cat(self, car_id, first_cat_id, second_cat_id, third_cat_id):
        car_cat_key = car_id + "-" + third_cat_id
        if car_cat_key not in self.athena_car_cat_list:
            first_cat_data = self.center_cat_id_dict[first_cat_id]
            second_cat_data = self.center_cat_id_dict[second_cat_id]
            third_cat_data = self.center_cat_id_dict[third_cat_id]

            save_data = {
                'car_id': car_id,
                'first_cat_id': first_cat_id,
                'first_cat_name': str(first_cat_data['cat_name']),
                'first_pic': str(first_cat_data['cat_pic']),
                'first_cat_letter': str(first_cat_data['first_letter']),
                'second_cat_id': second_cat_id,
                'second_cat_name': str(second_cat_data['cat_name']),
                'second_pic': str(second_cat_data['cat_pic']),
                'second_cat_letter': str(second_cat_data['first_letter']),
                'third_cat_id': third_cat_id,
                'third_cat_name': str(third_cat_data['cat_name']),
                'third_pic': str(third_cat_data['cat_pic']),
                'third_cat_letter': str(third_cat_data['first_letter']),
                'vehicle_code': 'C'
            }
            # self.athena_test_dao.insert_temple('center_car_cate_relation',save_data)
            self.car_cat_data_list.append(save_data)
            self.athena_car_cat_list.append(car_cat_key)

    # 拼写成sql
    def get_insert_sql(self, table, dic, ):
        gmt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dic['gmt_create'] = gmt
        dic['gmt_modified'] = gmt
        sql = 'insert ignore into ' + table + '(' + ','.join(dic.keys()) + ') values'
        value_list = list()
        for key, value in dic.items():
            value = str(value).replace('"', '')
            value_list.append('"' + self.athena_test_dao.html_tag.sub('', str(value)) + '"')
        sql += '(' + ','.join(value_list) + ')'
        return sql

    def get_batch_sql(self, table, batch_list):
        sql = 'insert ignore into ' + table + '(' + ','.join(batch_list[0].keys()) + ') values'
        value_list = list()
        for i in batch_list:
            inner_value_list = list()
            for key, value in i.items():
                if isinstance(value, str) or isinstance(value, unicode):
                    inner_value_list.append('"' + value + '"')
                else:
                    inner_value_list.append(str(value))
            value_list.append('(' + ','.join(inner_value_list) + ')')
        sql += ','.join(value_list)
        return sql


insert_address = os.getcwd() + "/center/1.insert.sql"
update_address = os.getcwd() + "/center/2.update.sql"

monkeyToCenter = MonkeyToCenter()
monkeyToCenter.main(insert_address, update_address)
