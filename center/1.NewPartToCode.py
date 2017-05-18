# encoding=utf-8
# new 配件库导入中心配件库，作为原始数据使用－－－part逻辑出错，应该一个车型一个自身的epc_pic
# 2016/06/02
import os

__author__ = 'zxg'

import sys

from util import CrawlDao

reload(sys)
sys.setdefaultencoding("utf-8")


class newPartToData:
    def __init__(self):
        # self.athena_dao = CrawlDao.CrawlDao("athena_center", "local")
        # self.monkey_dao = CrawlDao.CrawlDao('modeldatas', "local")
        self.athena_dao = CrawlDao.CrawlDao("dataserver", "online_cong")
        self.monkey_dao = CrawlDao.CrawlDao('modeldatas', "online_cong")

        # 实际online car_id 和 pid
        self.true_car_id_dict = dict()
        # id:data
        self.true_car_dict = dict()
        # athena的cate
        self.athena_cate_dict = dict()

        # liyang_id:tqmall_car_id
        self.liyang_online_dict = dict()
        # athena_g_id:third_cate_id
        self.goods_cate_dict = dict()

        # 已经出现的 goods_car对应关系
        self.athena_goods_car_list = list()

        # 不同的model 的相同pic 是不同的，因此存已出现的 pic_id
        self.has_show_pic_id_list = list()
        # === 冗余表服务＝＝＝
        self.online_car_id_set = set()
        self.car_cate_yu_dict = dict()

        self.has_append_list = list()
        # 断了后的最后的pic_id
        self.athena_pic_final_id = 52167
        # ＝＝＝＝＝＝对应的关系
        self.athena_goods_id = 0
        self.athena_pic_id = 0
        self.athena_sub_id = 0

        # 新增商品和uuid的对应关系:uuid:athena_goods_id
        self.goods_dui_dict = dict()
        # uuid:new_data{xx:xx}
        self.goods_dui_data_dict = dict()
        # 新增图片和uuid的对应关系:uuid:athena_pic_id
        self.pic_dui_dict = dict()
        self.pic_dui_data_dict = dict()
        # 新增附加表和uuid的对应关系:uuid:athena_subjoin_id
        self.subjoin_dui_dict = dict()
        self.subjoin_dui_data_dict = dict()

        # ＝＝＝＝＝＝存储的sql
        self.goods_insert_data_list = list()
        self.pic_insert_data_list = list()
        self.subjoin_insert_data_list = list()
        self.car_relation_insert_data_list = list()

        self.car_fix_insert_data_list = list()
        self.car_cate_insert_data_list = list()

    # part goods 转为 center_goods
    def goods_process(self):
        # athena的cate
        athena_cate_dict = dict()
        athena_cate_array = self.athena_dao.db.get_data(
            "select id,cat_code,vehicle_code from center_category where is_deleted ='N' and cat_level = '3'")
        for athena_cate_data in athena_cate_array:
            key = str(athena_cate_data['cat_code']) + str(athena_cate_data['vehicle_code'])
            athena_cate_dict[key] = str(athena_cate_data['id'])
        athena_cate_dict_keys = athena_cate_dict.keys()

        # athena part
        athena_part_dict = dict()
        athena_part_list = list()
        athena_part_array = self.athena_dao.db.get_data("select id,sum_code from center_part where is_deleted ='N'")
        for athena_part_data in athena_part_array:
            sum_code = str(athena_part_data['sum_code'])
            athena_part_dict[sum_code] = str(athena_part_data['id'])
            athena_part_list.append(sum_code)

        # monkey 数据
        monkey_goods_array = self.monkey_dao.db.get_data(
            "select uuid,oe_number,part_name,part_code,first_cate_code,second_cate_code,third_cate_code "
            "from db_monkey_part_goods_base")
        for monkey_goods_data in monkey_goods_array:
            uuid = str(monkey_goods_data['uuid'])
            oe_number = str(monkey_goods_data['oe_number'])
            part_code = str(monkey_goods_data['part_code'])
            part_name = str(monkey_goods_data['part_name'])
            first_cate_code = str(monkey_goods_data['first_cate_code'])
            second_cate_code = str(monkey_goods_data['second_cate_code'])
            third_cate_code = str(monkey_goods_data['third_cate_code'])

            cate_code = first_cate_code + "." + second_cate_code + "." + third_cate_code

            third_cate_id = 0
            if cate_code + "C" in athena_cate_dict_keys:
                third_cate_id = athena_cate_dict[cate_code + "C"]
            elif cate_code + "H" in athena_cate_dict_keys:
                third_cate_id = athena_cate_dict[cate_code + "H"]
            if third_cate_id == 0:
                print 'third_cate_id is 0,uuid:' + uuid

            part_id = 0
            if part_code in athena_part_list:
                part_id = athena_part_dict[part_code]

            self.goods_dui_data_dict[uuid] = {"oe_number": oe_number, "third_cate_id": third_cate_id,
                                              "part_id": part_id,
                                              "part_name": part_name}
            # 自增id
            self.athena_goods_id += 1
            ath_g_id = self.athena_goods_id
            self.goods_dui_dict[uuid] = ath_g_id
            # 保存到list中
            save_dict = self.goods_dui_data_dict[uuid]
            save_dict["id"] = ath_g_id
            self.goods_insert_data_list.append(save_dict)
            # 为 car_cate服务
            self.goods_cate_dict[ath_g_id] = save_dict['third_cate_id']

    # part pic 转为 center_pic
    def pic_process(self):
        # athena_pic_id = 0

        monkey_pic_array = self.monkey_dao.db.get_data(
            "select uuid,picture_num,picture_index from db_monkey_part_picture")
        for monkey_pic_data in monkey_pic_array:
            pic_uuid_id = str(monkey_pic_data['uuid'])
            picture_num = str(monkey_pic_data['picture_num'])
            picture_index = str(monkey_pic_data['picture_index'])

            self.pic_dui_data_dict[pic_uuid_id] = {"epc_pic_num": picture_num, "epc_index": picture_index}
            self.athena_pic_id += 1
            ath_pic_id = self.athena_pic_id
            self.pic_dui_dict[pic_uuid_id] = ath_pic_id
            # 保存到list中
            save_dict = self.pic_dui_data_dict[pic_uuid_id]
            save_dict["id"] = ath_pic_id
            self.pic_insert_data_list.append(save_dict)

    # part subjoin 转为 center_subjoin
    def subjoin_process(self):
        # athena_subjoin_id = 0

        monkey_subjoin_array = self.monkey_dao.db.get_data(
            "select uuid,remarks,application_amount from db_monkey_part_subjoin")
        for monkey_subjoin_data in monkey_subjoin_array:
            subjoin_uuid_id = str(monkey_subjoin_data['uuid'])
            remarks = str(monkey_subjoin_data['remarks'])
            application_amount = str(monkey_subjoin_data['application_amount'])

            self.subjoin_dui_data_dict[subjoin_uuid_id] = {"goods_car_remarks": remarks,
                                                           "application_amount": application_amount}
            self.athena_sub_id += 1
            ath_sub_id = self.athena_sub_id
            self.subjoin_dui_dict[subjoin_uuid_id] = ath_sub_id
            # 保存到list中
            save_dict = self.subjoin_dui_data_dict[subjoin_uuid_id]
            save_dict["id"] = ath_sub_id
            self.subjoin_insert_data_list.append(save_dict)

    # part relation 转为 center_goods_car
    def relation_process(self, file_first_name):

        # has_save_list = ['db_monkey_part_liyang_relation_audi','db_monkey_part_liyang_relation_toyota']
        has_save_list = []
        # 断了后 补pic的id值
        if self.athena_pic_final_id != 0:
            self.athena_pic_id = self.athena_pic_final_id

        table_array = self.monkey_dao.db.get_data("select liyang_table from db_monkey_part_liyang_table_relation")
        for table_data in table_array:
            table_name = str(table_data['liyang_table'])
            brand_name = table_name.replace("db_monkey_part_liyang_relation", "")
            print '处理品牌表：' + table_name
            print '品牌：' + brand_name

            # TODO 已保存一份，就过滤了,仅处理别克/宝马
            if table_name in has_save_list:
                print '此品牌表 已处理，过滤'+table_name
                self.monkey_dao = CrawlDao.CrawlDao('modeldatas', "online_cong")
                pic_uuid_array = self.monkey_dao.db.get_data("select pic_id from " + table_name + " group by pic_id")
                for pic_data in pic_uuid_array:
                    ath_pic_id = self.pic_dui_dict[str(pic_data['pic_id'])]
                    if ath_pic_id not in self.has_show_pic_id_list:
                        self.has_show_pic_id_list.append(ath_pic_id)
                continue

            # model_id_pic_uuid_id
            pic_model_id_dict = dict()
            self.monkey_dao = CrawlDao.CrawlDao('modeldatas', "online_cong")

            old_model_id = ""
            # 已经添加到 car_id
            self.has_append_list = list()
            monkey_relation_array = self.monkey_dao.db.get_data(
                "select goods_id,pic_id,subjoin_id,liyang_id from " + table_name + " order by part_liyang_id")
            for monkey_relation_data in monkey_relation_array:
                goods_uuid_id = str(monkey_relation_data['goods_id'])
                pic_uuid_id = str(monkey_relation_data['pic_id'])
                subjoin_uuid_id = str(monkey_relation_data['subjoin_id'])
                liyang_id = str(monkey_relation_data['liyang_id'])

                online_car_id = self.get_tqmall_car_by_liyang(liyang_id)
                model_id = self.true_car_dict[online_car_id]['model_id']
                # 根据车型进行数据分批保存
                if old_model_id == "":
                    old_model_id = model_id
                if old_model_id != model_id:
                    old_model_id = model_id
                    self.other_rongyu()
                    # 是否保存
                    self.write_to_sql(file_first_name, False, brand_name)

                # goods_id
                if goods_uuid_id in self.goods_dui_dict.keys():
                    ath_g_id = self.goods_dui_dict[goods_uuid_id]
                else:
                    self.athena_goods_id += 1
                    ath_g_id = self.athena_goods_id
                    self.goods_dui_dict[goods_uuid_id] = ath_g_id
                    print 'wrong goods_uuid:%s' % goods_uuid_id

                # 保存过一次的不再append
                goods_car_key = str(online_car_id) + "-" + str(ath_g_id)
                if goods_car_key in self.athena_goods_car_list:
                    continue
                self.athena_goods_car_list.append(goods_car_key)

                # pic
                model_pic_key = str(model_id) + "-" + str(pic_uuid_id)
                if model_pic_key in pic_model_id_dict.keys():
                    ath_pic_id = pic_model_id_dict[model_pic_key]
                else:
                    ath_pic_id = self.pic_dui_dict[pic_uuid_id]
                    # 历史上出现过一次，则进行后续处理，否则就保存即可
                    if ath_pic_id in self.has_show_pic_id_list:
                        self.athena_pic_id += 1
                        ath_pic_id = self.athena_pic_id
                        # 保存到list中
                        save_dict = self.pic_dui_data_dict[pic_uuid_id]
                        save_dict["id"] = ath_pic_id
                        self.pic_insert_data_list.append(save_dict)

                    # 保存此时的数据
                    pic_model_id_dict[model_pic_key] = ath_pic_id
                    self.has_show_pic_id_list.append(ath_pic_id)

                # subjoin
                if subjoin_uuid_id in self.subjoin_dui_dict.keys():
                    ath_sub_id = self.subjoin_dui_dict[subjoin_uuid_id]
                else:
                    self.athena_sub_id += 1
                    ath_sub_id = self.athena_sub_id
                    self.subjoin_dui_dict[subjoin_uuid_id] = ath_sub_id
                    print 'wrong subjoin_uuid_id:%s' % subjoin_uuid_id

                self.car_relation_insert_data_list.append(
                    {"goods_id": ath_g_id, "car_id": online_car_id, "pic_id": ath_pic_id, "subjoin_id": ath_sub_id,
                     "model_id": model_id})

                # 是否保存
                if len(self.car_relation_insert_data_list) > 6000:
                    self.write_to_file(file_first_name + "4.center_goods_car" + brand_name + ".sql",
                                       self.car_relation_insert_data_list,
                                       "center_goods_car_relation", False)
                    self.car_relation_insert_data_list = []

                # 冗余该车型为已有
                self.online_car_id_set.add(online_car_id)
                # 冗余 该车型下的三级商品分类
                third_id = str(self.goods_cate_dict[ath_g_id])
                if online_car_id in self.car_cate_yu_dict.keys():
                    third_set = set(self.car_cate_yu_dict[online_car_id])
                else:
                    third_set = set()
                third_set.add(third_id)
                self.car_cate_yu_dict[online_car_id] = third_set

            print brand_name + ' is doing ok'
            # 一个品牌结束，进行数据保存
            self.other_rongyu()
            # 是否保存
            self.write_to_sql(file_first_name, False, brand_name)
            self.athena_goods_car_list = []
            print 'now the self.athena_pic_id:%s' % str(self.athena_pic_id)

    def write_base_to_sql(self, file_first_name):
        #
        if len(self.goods_insert_data_list) > 0:
            # TODO 二次补充室，无需再添加数据
            # self.write_to_file(file_first_name + "1.center_goods.sql", self.goods_insert_data_list, "center_goods",True)
            self.goods_insert_data_list = []

        # 根据不同的model_id会有新增，因此还没结束
        if len(self.pic_insert_data_list) > 0:
            # self.write_to_file(file_first_name + "2.center_pic.sql", self.pic_insert_data_list,"center_goods_car_picture", False)
            self.pic_insert_data_list = []

        if len(self.subjoin_insert_data_list) > 0:
            # self.write_to_file(file_first_name + "3.center_subjoin.sql", self.subjoin_insert_data_list,"center_goods_car_subjoin", True)
            self.subjoin_insert_data_list = []

    def write_to_sql(self, file_first_name, is_final=False, append_name=""):
        if len(self.pic_insert_data_list) > 0:
            self.write_to_file(file_first_name + "2.center_pic.sql", self.pic_insert_data_list,
                               "center_goods_car_picture", is_final)
            self.pic_insert_data_list = []

        if len(self.car_relation_insert_data_list) > 0:
            self.write_to_file(file_first_name + "4.center_goods_car" + append_name + ".sql",
                               self.car_relation_insert_data_list,
                               "center_goods_car_relation", is_final)
            self.car_relation_insert_data_list = []

        if len(self.car_cate_insert_data_list) > 0:
            self.write_to_file(file_first_name + "5.center_car_cate_relation" + append_name + ".sql",
                               self.car_cate_insert_data_list,
                               "center_car_cate_relation", is_final)
            self.car_cate_insert_data_list = []

        if len(self.car_fix_insert_data_list) > 0:
            self.write_to_file(file_first_name + "6.center_car_for_fix" + append_name + ".sql",
                               self.car_fix_insert_data_list,
                               "center_car_for_fix", is_final)
            self.car_fix_insert_data_list = []

    # 冗余数据－center_car_cate_relation，center_car_for_fix
    def init_other(self):

        true_car_array = self.athena_dao.db.get_data("select id,name,power,level,first_word,sort,pid,"
                                                     "model,series,brand,company,country,car_type,"
                                                     "car_level,import_info,logo,is_hot,year,engine_type,"
                                                     "chassis_number,guide_price "
                                                     "from db_car_category"
                                                     )
        for true_data in true_car_array:
            id = str(true_data['id'])
            pid = str(true_data['pid'])
            level = int(true_data['level'])

            self.true_car_id_dict[id] = pid
            self.true_car_dict[id] = true_data

            true_data['model_id'] = 0
            if level == 6:
                true_data['model_id'] = self.true_car_id_dict[self.true_car_id_dict[pid]]

        # athena的cate
        athena_cate_array = self.athena_dao.db.get_data(
            "select id,parent_id,cat_name,cat_pic,first_letter,vehicle_code from center_category where is_deleted ='N'")
        for athena_cate_data in athena_cate_array:
            self.athena_cate_dict[str(athena_cate_data['id'])] = athena_cate_data

    def other_rongyu(self):
        # center_car_for_fix
        for car_id in self.online_car_id_set:
            if car_id in self.has_append_list:
                continue
            self.has_append_list.append(car_id)
            car_data = self.true_car_dict[car_id]
            self.car_fix_insert_data_list.append(car_data)

            pid_list = list(self.get_pid_list_by_online_car_id(car_id))
            for pid in pid_list:
                if pid in self.has_append_list:
                    continue
                self.has_append_list.append(pid)
                car_parent_data = self.true_car_dict[pid]
                self.car_fix_insert_data_list.append(car_parent_data)
        self.online_car_id_set = set()

        # center_car_cate_relation
        for online_car_id, third_set in self.car_cate_yu_dict.items():
            for third_id in third_set:
                try:
                    third_cat_data = self.athena_cate_dict[third_id]
                    second_cat_data = self.athena_cate_dict[str(third_cat_data['parent_id'])]
                    first_cat_data = self.athena_cate_dict[str(second_cat_data['parent_id'])]
                except Exception, e:
                    print e
                    print "third_id:" + third_id

                save_data = {
                    'car_id': online_car_id,
                    'first_cat_id': str(first_cat_data['id']),
                    'first_cat_name': str(first_cat_data['cat_name']),
                    'first_pic': str(first_cat_data['cat_pic']),
                    'first_cat_letter': str(first_cat_data['first_letter']),
                    'second_cat_id': str(second_cat_data['id']),
                    'second_cat_name': str(second_cat_data['cat_name']),
                    'second_pic': str(second_cat_data['cat_pic']),
                    'second_cat_letter': str(second_cat_data['first_letter']),
                    'third_cat_id': str(third_cat_data['id']),
                    'third_cat_name': str(third_cat_data['cat_name']),
                    'third_pic': str(third_cat_data['cat_pic']),
                    'third_cat_letter': str(third_cat_data['first_letter']),
                    'vehicle_code': 'C'
                }
                self.car_cate_insert_data_list.append(save_data)

        self.car_cate_yu_dict = dict()

    def main(self):
        file_first_name = os.getcwd() + "/center/"
        print "===========start ========="

        self.init_other()
        print "===========start 处理 goods========="
        # 处理 goods
        self.goods_process()
        print "===========start 处理 pic========="
        # 处理 pic
        self.pic_process()
        print "===========start 处理 subjoin========="
        # 处理 subjoin
        self.subjoin_process()
        print "===========start write 初始数据========="
        self.write_base_to_sql(file_first_name)
        print "===========start 处理 relation========="
        # 处理 relation
        self.relation_process(file_first_name)
        print "===========start 处理 冗余数据========="
        self.has_append_list = list()
        self.other_rongyu()
        print "===========start write sql========="
        # 生成 sql
        self.write_to_sql(file_first_name, True)
        print "===========end ========="

    # =======help======
    def get_tqmall_car_by_liyang(self, liyang_id):
        if liyang_id in self.liyang_online_dict.keys():
            return self.liyang_online_dict[liyang_id]

        liyang_sql = "select car_models_id from db_car_all where l_id = '" + liyang_id + "' limit 1"
        try:
            liyang_array = self.athena_dao.db.get_data(liyang_sql)
        except:
            self.athena_dao = CrawlDao.CrawlDao("dataserver", "online_cong")
            liyang_array = self.athena_dao.db.get_data(liyang_sql)

        if len(liyang_array) == 0:
            print 'liyang_id:%s not exist in db_car_all' % liyang_id
            car_models_id = 0
        else:
            car_models_id = str(liyang_array[0]['car_models_id'])

        self.liyang_online_dict[liyang_id] = car_models_id

        return car_models_id

    # 根据car——id 递归获得父id
    def get_pid_list_by_online_car_id(self, car_id, pid_list=list()):
        pid = self.true_car_id_dict[car_id]
        if pid == "0":
            return pid_list
        else:
            pid_list.append(pid)
            return self.get_pid_list_by_online_car_id(pid, pid_list)

    def write_to_file(self, file_address, insert_list, table_name, is_final=False):
        max_num = 3000
        start_string = "SET unique_checks=0;SET foreign_key_checks=0;set autocommit=0;\n"
        final_string = "commit;\n"
        time_string = "select @now_time := now();\n"

        # 判断是否存在文件：
        is_exist_file = os.path.exists(file_address)

        #
        insert_object = open(file_address, 'a')
        if not is_exist_file:
            print '%s is not exist' % file_address
            insert_object.writelines(start_string)
            insert_object.writelines(time_string)

        insert_help_list = list()
        try:
            for the_data in insert_list:
                the_data['gmt_modified'] = '@now_time'
                the_data['gmt_create'] = '@now_time'

                insert_help_list.append(the_data)
                if len(insert_help_list) > max_num:
                    insert_object.writelines(self.monkey_dao.get_batch_sql(table_name, insert_help_list))
                    insert_object.writelines(";\n")
                    insert_help_list = list()

            insert_list = []
            if len(insert_help_list) > 0:
                insert_object.writelines(self.monkey_dao.get_batch_sql(table_name, insert_help_list))
                insert_object.writelines(";\n")
                del insert_help_list

            if is_final:
                insert_object.writelines(final_string)
        except Exception, e:
            print e
        finally:
            insert_object.close()

    # ===============保存 数据 的sql ==============

    def save_center_goods(self, id, oe_number, third_cate_id, part_id, part_name):
        save_dict = {"id": id, "oe_number": oe_number, "third_cate_id": third_cate_id, "part_id": part_id,
                     "part_name": part_name}
        self.goods_insert_data_list.append(save_dict)


newPartTodata = newPartToData()
newPartTodata.main()
