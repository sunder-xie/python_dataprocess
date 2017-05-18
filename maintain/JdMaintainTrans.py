# encoding=utf-8
# 京东保养对接到线上
# 处理前 复制 线上从库 db_model_maintain_plan、db_model_maintain_mileage、db_model_maintain_detail 三个表至测试环境
import datetime
import json
import os

__author__ = 'zxg'

import CrawlDao


class JdMainTrans:
    def __init__(self):
        print "===============start __init__================"
        self.is_test = False
        self.crawl_dao = CrawlDao.CrawlDao('dev_crawler', 'test')
        self.save_maintain_dao = CrawlDao.CrawlDao('modeldatas', 'test')
        if self.is_test:
            self.monkey_dao = CrawlDao.CrawlDao('modeldatas', 'test')
        else:
            self.monkey_dao = CrawlDao.CrawlDao('modeldatas', 'online_cong')

        self.monkey_liyang_set = set()

        # leyel_id:liyang_data
        self.liyang_dict = dict()
        self.liyang_up_dict = dict()

        self.liyang_string_list = list()

        # 主键:list(liyang_data)
        self.jd_car_dict = dict()
        # car_id:list(data)
        self.jd_car_maintain_dict = dict()

        self.init_liyang()
        self.init_jd_car()

        # 存数据
        self.db_car_maintain_plan_data_list = list()
        self.db_car_maintain_plan_up_data_dict = dict()

        self.db_model_maintain_plan_data_list = list()
        self.db_model_maintain_mileage_data_list = list()
        self.db_model_maintain_detail_data_list = list()

        # =======给下属select 缓存用
        self.maintain_plan_by_car_dict = dict()

        # 已处理的力洋id
        self.car_maintain_plan_li_id_list = list()

    def init_jd_car(self):
        # 不管jd_car对应力洋id的增加或更新
        jd_car_array = self.crawl_dao.db.get_data("select car_uuid,liyang_id_list from jd_car where the_type in (1,3) ")
        for jd_car_data in jd_car_array:
            car_uuid = str(jd_car_data['car_uuid'])
            liyang_id_list = str(jd_car_data['liyang_id_list'])
            liyang_array = liyang_id_list.split(",")

            liyang_data_list = list()
            for liyang in liyang_array:
                liyang_data = self.get_liyang_data(liyang)
                if liyang_data == None:
                    print liyang_array
                    print "the car_uuid :%s" % car_uuid
                liyang_data_list.append(liyang_data)

            self.jd_car_dict[car_uuid] = liyang_data_list

    def init_liyang(self):
        liyang_array = self.monkey_dao.db.get_data(
            "select car_brand,car_series,factory_name,vehicle_type,leyel_id,engine_oil_num,oil_num,air_num,aircondition_num,fuel_num,spark_plugs from db_car_info_all ")
        for liyang_data in liyang_array:
            self.liyang_dict[str(liyang_data['leyel_id'])] = liyang_data

    def main_func(self, save_heard_address):
        print "===============start main_func================"

        # self.jd_car_maintain()
        # TODO
        self.maintain_relation()
        self.write_sql(save_heard_address)

        print "===============end main_func================"

    def jd_car_maintain(self):
        jd_car_list = self.jd_car_dict.keys()

        liyang_first_dict = dict()
        car_maintain_array = self.crawl_dao.db.get_data(
            "select car_maintain_uuid,car_uuid,maintain_name,maintain_unit from jd_car_maintain where the_type in (0,1)")
        for car_maintain_data in car_maintain_array:
            car_maintain_uuid = str(car_maintain_data['car_maintain_uuid'])
            car_uuid = str(car_maintain_data['car_uuid'])
            maintain_name = str(car_maintain_data['maintain_name'])
            maintain_unit = str(car_maintain_data['maintain_unit']).replace("升", "").replace("个", "")
            if car_uuid not in jd_car_list:
                continue
            liyang_data_list = self.jd_car_dict[car_uuid]
            for liyang_data in liyang_data_list:
                is_change = False
                liyang_id = str(liyang_data['leyel_id'])
                if liyang_id in liyang_first_dict.keys():
                    update_data = liyang_first_dict[liyang_id]
                else:
                    update_data = dict()

                if '发动机机油' == maintain_name and maintain_unit != str(liyang_data['engine_oil_num']):
                    is_change = True
                    update_data['engine_oil_num'] = maintain_unit
                if '机油滤清器' == maintain_name and maintain_unit != str(liyang_data['oil_num']):
                    is_change = True
                    update_data['oil_num'] = maintain_unit
                if '空气滤清器' == maintain_name and maintain_unit != str(liyang_data['air_num']):
                    is_change = True
                    update_data['air_num'] = maintain_unit
                if '空调滤清器' == maintain_name and maintain_unit != str(liyang_data['aircondition_num']):
                    is_change = True
                    update_data['aircondition_num'] = maintain_unit
                if '燃油滤清器' == maintain_name and maintain_unit != str(liyang_data['fuel_num']):
                    is_change = True
                    update_data['fuel_num'] = maintain_unit
                if '火花塞' == maintain_name and maintain_unit != str(liyang_data['spark_plugs']):
                    is_change = True
                    update_data['spark_plugs'] = maintain_unit

                if is_change:
                    print 'car_maintain_uuid has change maintain:%s' % car_maintain_uuid
                    liyang_first_dict[liyang_id] = update_data

        # 不同的 data 存dict的list
        for liyang_id, update_data in liyang_first_dict.iteritems():
            update_str = json.dumps(update_data)
            if update_str in self.liyang_up_dict.keys():
                liyang_list = list(self.liyang_up_dict[update_str])
            else:
                liyang_list = list()

            liyang_list.append(liyang_id)
            self.liyang_up_dict[update_str] = liyang_list

    # 保养详情主方法
    def maintain_relation(self):
        jd_car_list = self.jd_car_dict.keys()
        maintain_name_dict = {'发动机机油': '1', '机油滤清器': '2', '空气滤清器': '3', '机油滤清器': '2', '空调滤清器': '4', '燃油滤清器': '5',
                              '火花塞': '6'}
        # 改变的maintain_id
        change_car_id_array = self.crawl_dao.db.get_data(
            "select car_uuid from jd_car_maintain_relation where the_type in (0,3) group by car_uuid")

        for change_car_data in change_car_id_array:
            change_car_id = str(change_car_data['car_uuid'])
            # 保养内容:id-自定义数字
            car_maintain_id_dict = dict()
            car_maintain_array = self.crawl_dao.db.get_data(
                "select car_maintain_uuid,maintain_name from jd_car_maintain where car_uuid = '" + change_car_id + "'")
            for car_maintain_data in car_maintain_array:
                car_maintain_uuid = str(car_maintain_data['car_maintain_uuid'])
                maintain_name = str(car_maintain_data['maintain_name'])
                if maintain_name in maintain_name_dict.keys():
                    car_maintain_id_dict[car_maintain_uuid] = maintain_name_dict[maintain_name]
            # 拼接现在的方案
            plan_dict = dict()
            car_maintain_plan_array = self.crawl_dao.db.get_data(
                "select car_maintain_uuid,mileage from jd_car_maintain_relation where car_uuid = '" + change_car_id + "'")
            for car_maintain_plan_data in car_maintain_plan_array:
                car_maintain_uuid = str(car_maintain_plan_data['car_maintain_uuid'])
                mileage = str(car_maintain_plan_data['mileage'])

                if car_maintain_uuid not in car_maintain_id_dict.keys():
                    continue

                the_maintain_name = car_maintain_id_dict[car_maintain_uuid]

                if mileage in plan_dict:
                    detail_list = plan_dict[mileage]
                else:
                    detail_list = list()
                if the_maintain_name not in detail_list:
                    detail_list.append(the_maintain_name)
                    plan_dict[mileage] = detail_list

            # ===========start compare with monkey
            if change_car_id not in jd_car_list:
                continue

            # 根据力洋id找出其在modeldatas的保养方案，
            monkey_maintain_plan_id = 0
            liyang_data_list = self.jd_car_dict[change_car_id]
            if len(liyang_data_list) == 0:
                print '无对应的力洋数据，car——id：%S' % change_car_id
                continue
            # 无记录，取一个数据
            liyang_data = liyang_data_list[0]
            result_plan_dict = dict(self.get_monkey_plan_by_car(str(liyang_data['car_brand']),
                                                                str(liyang_data['factory_name']),
                                                                str(liyang_data['car_series']),
                                                                str(liyang_data['vehicle_type'])))
            for plan_id, result_plan_dict in result_plan_dict.iteritems():
                is_equal = cmp(result_plan_dict, plan_dict)
                if is_equal == 0:
                    monkey_maintain_plan_id = plan_id
                    break
            if monkey_maintain_plan_id == 0:
                # 没有保养方案，新增一个保养方案
                monkey_maintain_plan_id = self.add_new_maintain(plan_dict, str(liyang_data['car_brand']),
                                                                str(liyang_data['factory_name']),
                                                                str(liyang_data['car_series']),
                                                                str(liyang_data['vehicle_type']))

            # 现有的保养方案有符合情况的，存储至car_maintain_plan中
            self.save_car_maintain_plan(monkey_maintain_plan_id, liyang_data_list)

    def write_sql(self, save_address):
        max_num = 3000
        liyang_sql_list = list()
        for update_str, liyang_list in self.liyang_up_dict.iteritems():
            update_data = json.loads(update_str)
            index_num = 0
            while True:
                up_list = liyang_list[index_num * max_num:(index_num + 1) * max_num]
                update_sql = self.get_batch_update_sql('db_car_info_all', update_data, {'leyel_id': up_list})
                liyang_sql_list.append(update_sql)
                index_num += 1
                if len(up_list) < max_num:
                    break

        liyang_file_object = open(save_address + "/monkey_car_info_update.sql", 'w')
        try:
            liyang_file_object.writelines("SET unique_checks=0;SET foreign_key_checks=0;set autocommit=0;\n")
            liyang_file_object.writelines(";\n".join(liyang_sql_list))
            liyang_file_object.writelines(";\ncommit;\n")
        finally:
            liyang_file_object.close()

        # 存数据
        maintain_file_object = open(save_address + "/monkey_maintain.sql", 'w')
        try:
            maintain_file_object.writelines("SET unique_checks=0;SET foreign_key_checks=0;set autocommit=0;\n")

            car_maintain_plan_list = list()
            index_num = 0
            while True:
                insert_list = self.db_car_maintain_plan_data_list[index_num * max_num:(index_num + 1) * max_num]
                insert_length = len(insert_list)
                if insert_length > 0:
                    insert_sql = self.get_insert_batch_sql('db_car_maintain_plan', insert_list)
                    car_maintain_plan_list.append(insert_sql)
                    index_num += 1
                if insert_length < max_num:
                    break
            maintain_file_object.writelines(";\n".join(car_maintain_plan_list))
            maintain_file_object.writelines(";\n")

            # self.get_insert_sql('db_model_maintain_plan', save_data)
            maintain_plan_list = list()
            index_num = 0
            while True:
                insert_list = self.db_model_maintain_plan_data_list[index_num * max_num:(index_num + 1) * max_num]
                insert_length = len(insert_list)
                if insert_length > 0:
                    insert_sql = self.get_insert_batch_sql('db_model_maintain_plan', insert_list)
                    maintain_plan_list.append(insert_sql)
                    index_num += 1
                if insert_length < max_num:
                    break
            maintain_file_object.writelines(";\n".join(maintain_plan_list))
            maintain_file_object.writelines(";\n")

            # self.get_insert_sql('db_model_maintain_mileage', save_data)
            maintain_mileage_list = list()
            index_num = 0
            while True:
                insert_list = self.db_model_maintain_mileage_data_list[index_num * max_num:(index_num + 1) * max_num]
                insert_length = len(insert_list)
                if insert_length > 0:
                    insert_sql = self.get_insert_batch_sql('db_model_maintain_mileage', insert_list)
                    maintain_mileage_list.append(insert_sql)
                    index_num += 1
                if insert_length < max_num:
                    break
            maintain_file_object.writelines(";\n".join(maintain_mileage_list))
            maintain_file_object.writelines(";\n")

            # self.get_insert_sql('db_model_maintain_detail', save_data)
            maintain_detail_list = list()
            index_num = 0
            while True:
                insert_list = self.db_model_maintain_detail_data_list[index_num * max_num:(index_num + 1) * max_num]
                insert_length = len(insert_list)
                if insert_length > 0:
                    insert_sql = self.get_insert_batch_sql('db_model_maintain_detail', insert_list)
                    maintain_detail_list.append(insert_sql)
                    index_num += 1
                if insert_length < max_num:
                    break
            maintain_file_object.writelines(";\n".join(maintain_detail_list))
            maintain_file_object.writelines(";\n")

            maintain_up_list = list()
            for is_deleted, id_list in self.db_car_maintain_plan_up_data_dict.iteritems():
                update_data = {'is_deleted': is_deleted}
                index_num = 0
                while True:
                    up_list = id_list[index_num * max_num:(index_num + 1) * max_num]
                    up_length = len(up_list)

                    if up_length > 0:
                        update_sql = self.get_batch_update_sql('db_car_maintain_plan', update_data, {'id': up_list})
                        maintain_up_list.append(update_sql)
                        index_num += 1
                    if up_length < max_num:
                        break
            maintain_file_object.writelines(";\n".join(maintain_up_list))
            maintain_file_object.writelines(";\n")

            maintain_file_object.writelines("commit;\n")
        finally:
            maintain_file_object.close()

    # =============

    def add_new_maintain(self, plan_dict, car_brand, car_factory, car_series, car_model):
        key = car_brand + car_factory + car_series + car_model
        if key in self.maintain_plan_by_car_dict.keys():
            result_plan_dict = self.maintain_plan_by_car_dict[key]
        else:
            result_plan_dict = dict()

        keys_length = len(result_plan_dict.keys())

        plan_id = self.save_db_model_maintain_plan(car_brand, car_series, car_factory, car_model,
                                                   '方案' + str(keys_length + 1))
        # 补充保养方案的内容
        for mileage, detail_list in plan_dict.iteritems():
            mileage_id = self.save_db_model_maintain_mileage(plan_id, mileage)
            for detail in detail_list:
                self.save_db_model_maintain_detail(mileage_id, detail)

        result_plan_dict[plan_id] = plan_dict
        self.maintain_plan_by_car_dict[key] = result_plan_dict

        return plan_id

    # 获得当前车型的所有方案
    def get_monkey_plan_by_car(self, car_brand, car_factory, car_series, car_model):
        key = car_brand + car_factory + car_series + car_model
        if key in self.maintain_plan_by_car_dict.keys():
            result_plan_dict = dict(self.maintain_plan_by_car_dict[key])
        else:
            result_plan_dict = dict()
            maintain_plan_array = self.monkey_dao.db.get_data(
                "select id from db_model_maintain_plan where car_brand = '" + car_brand + "' and car_series = '" + car_series + "' and company = '" + car_factory + "' and car_model = '" + car_model + "' and is_deleted = 0 ")

            for maintain_plan_data in maintain_plan_array:
                maintain_plan_id = str(maintain_plan_data['id'])
                # 拼接现在的方案
                plan_dict = dict()
                mileage_array = self.monkey_dao.db.get_data(
                    "select id,mileage from db_model_maintain_mileage where maintain_plan_id = '" + maintain_plan_id + "' and is_deleted = 0")
                for mileage_data in mileage_array:
                    mileage_id = str(mileage_data['id'])
                    mileage = str(mileage_data['mileage'])

                    if mileage in plan_dict:
                        detail_list = plan_dict[mileage]
                    else:
                        detail_list = list()

                    detail_array = self.monkey_dao.db.get_data(
                        "select maintain_id from db_model_maintain_detail where model_mileage_id = '" + mileage_id + "' ")
                    for detail_data in detail_array:
                        maintain_id = str(detail_data['maintain_id'])
                        if maintain_id not in detail_list:
                            detail_list.append(maintain_id)
                            plan_dict[mileage] = detail_list

                result_plan_dict[maintain_plan_id] = plan_dict

            self.maintain_plan_by_car_dict[key] = result_plan_dict

        return result_plan_dict

    # ==========private sql======================
    # 保存车型跟保养方案的关系
    def save_car_maintain_plan(self, plan_id, liyang_data_list):
        for liyang_data in liyang_data_list:
            not_have_one = True
            liyang_id = liyang_data['leyel_id']
            if liyang_id in self.car_maintain_plan_li_id_list:
                # 已处理的liyang id
                continue

            self.car_maintain_plan_li_id_list.append(liyang_id)
            car_maintain_array = self.monkey_dao.db.get_data(
                "select id,maintain_plan_id,is_deleted from db_car_maintain_plan where l_id = '" + liyang_id + "' ")
            for car_maintain_data in car_maintain_array:
                id = str(car_maintain_data['id'])
                maintain_plan_id = str(car_maintain_data['maintain_plan_id'])
                is_deleted = str(car_maintain_data['is_deleted'])

                key = 'not_up'

                if maintain_plan_id == plan_id:
                    # 该记录已存在
                    not_have_one = False
                    # is deleted?
                    if is_deleted != '0':
                        # 该记录设置为 正常状态
                        key = '0'

                if maintain_plan_id != plan_id:
                    if is_deleted == '0':
                        # 非这个对应关系的都置为N，update
                        key = '1'

                # 存在更新，将数据存入dict{0：list（id）}
                if key != 'not_up':
                    if key in self.db_car_maintain_plan_up_data_dict.keys():
                        id_list = list(self.db_car_maintain_plan_up_data_dict[key])
                    else:
                        id_list = list()

                    id_list.append(id)
                    self.db_car_maintain_plan_up_data_dict[key] = id_list

            if not_have_one:
                # 新增
                save_data = {'l_id': liyang_id, 'maintain_plan_id': plan_id}
                # save_data_sql = self.get_insert_sql('db_car_maintain_plan', save_data)
                self.db_car_maintain_plan_data_list.append(save_data)

    # 保存新方案
    def save_db_model_maintain_plan(self, car_brand, car_series, company, car_model, maintain_plan):
        save_data = {'car_brand': car_brand, 'car_series': car_series, 'company': company, 'car_model': car_model,
                     'maintain_plan': maintain_plan}

        plan_id = str(self.save_maintain_dao.insert_temple('db_model_maintain_plan', save_data))
        save_data['id'] = plan_id

        self.db_model_maintain_plan_data_list.append(save_data)
        return plan_id

    def save_db_model_maintain_mileage(self, maintain_plan_id, mileage):
        save_data = {'maintain_plan_id': maintain_plan_id, 'mileage': mileage}

        mileage_id = str(self.save_maintain_dao.insert_temple('db_model_maintain_mileage', save_data))
        save_data['id'] = mileage_id

        self.db_model_maintain_mileage_data_list.append(save_data)
        return mileage_id

    def save_db_model_maintain_detail(self, model_mileage_id, maintain_id):
        save_data = {'model_mileage_id': model_mileage_id, 'maintain_id': maintain_id}

        detail_id = str(self.save_maintain_dao.insert_temple('db_model_maintain_detail', save_data))
        save_data['id'] = detail_id

        self.db_model_maintain_detail_data_list.append(save_data)
        return detail_id

    def get_liyang_data(self, leyel_id):

        try:
            return self.liyang_dict[leyel_id]
        except:
            print 'liyang id not in car_info_all: %s' % leyel_id
            return None

    # 更新数据,返回更新语句
    def get_update_sql(self, table, db_dict, where_dict):
        # gmt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # db_dict['gmt_modified'] = gmt
        # 更新的内容
        value_list = list()
        for key, value in db_dict.items():
            value_list.append('%s = "%s"' % (key, str(value)))
        # 判断内容
        where_list = list()
        where_list.append('1 = 1')
        for key, value in where_dict.items():
            where_list.append('%s = "%s"' % (key, str(value)))
        # 更新的条件
        sql = 'update %s set %s  ' % (table, ','.join(value_list))
        sql += 'where  %s ' % (' and '.join(where_list))
        return sql

    # 拼写成sql
    def get_insert_sql(self, table, dic, ):
        gmt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dic['gmt_create'] = gmt
        dic['gmt_modified'] = gmt
        sql = 'insert ignore into ' + table + '(' + ','.join(dic.keys()) + ') values'
        value_list = list()
        for key, value in dic.items():
            value = str(value).replace('"', '')
            value_list.append('"' + self.monkey_dao.html_tag.sub('', str(value)) + '"')
        sql += '(' + ','.join(value_list) + ')'
        return sql

    # 更新数据,返回更新语句
    def get_batch_update_sql(self, table, db_dict, where_dict):
        # gmt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # db_dict['gmt_modified'] = gmt
        # 更新的内容
        value_list = list()
        for key, value in db_dict.items():
            value_list.append('%s = "%s"' % (key, str(value)))
        # 判断内容
        where_list = list()
        where_list.append('1 = 1')
        for key, value in where_dict.items():
            where_list.append('%s in ( "%s" )' % (key, '","'.join(value)))

        # 更新的条件
        sql = 'update %s set %s  ' % (table, ','.join(value_list))
        sql += 'where  %s ' % (' and '.join(where_list))
        return sql

    # 批量插入数据
    def get_insert_batch_sql(self, table, batch_list):
        gmt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for i in batch_list:
            i['gmt_create'] = gmt
            i['gmt_modified'] = gmt
        action = 'insert ignore'
        sql = action + ' into ' + table + '(' + ','.join(batch_list[0].keys()) + ') values'
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


save_heard_address = os.getcwd() + "/sql"

jdMainTrans = JdMainTrans()
jdMainTrans.main_func(save_heard_address)
