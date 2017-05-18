# encoding=utf-8
# 易损件数据初始化到center中,format+brand 作为唯一商品
''' 商品库中的 空调泵 db_commodity_goods id(13939
13994
13997
14041
) :oe = n:1 ,需要 引入center_oe_format_relation
'''
# 2016.10.27
import json
import os

from util import CrawlDao, FileUtil, StringUtil

__author__ = 'zxg'


class WearingParts:
    def __init__(self):
        self.dao = CrawlDao.CrawlDao("test", "local")
        # 1. 处理蓄电池的数据
        # self.cat_dict = {'cat_id': '4440', 'cat_name': '蓄电池', "cat_code": "1302300"}
        # self.center_goods_max_id = 92603
        # 1. 处理蓄电池的数据
        self.cat_id_dict = {
            '5025': {'cat_name': '汽机油', "cat_code": "1601000"},
            '4440': {'cat_name': '蓄电池', "cat_code": "1302300"},
            '4191': {'cat_name': '轮胎', "cat_code": "1209310"},
            '4375': {'cat_name': '火花塞', "cat_code": "1301320"},
            '4343': {'cat_name': '机油滤清器', "cat_code": "1301230"},
            '4131': {'cat_name': '后刹车片', "cat_code": "1208321"},
        }
        # self.cat_dict = {'cat_id': '4440', 'cat_name': '蓄电池', "cat_code": "1302300"}
        self.center_goods_max_id = 92603

        # ====== 电商数据 ========
        # goods_id:{goods_format,brand_id,goods_img,cat_id,measure_unit,goods_img}
        self.db_goods_dict = dict()
        # brand_id:{brand_name}
        self.db_brand_dict = dict()
        # attr_id:attr_name
        self.db_attr_config_dict = dict()

        self.init_db_goods()
        self.init_db_brand()
        self.init_db_attr()
        # =======商品库数据 ======
        # uuid:{brand_name,sale_unit,goods_format,part_name,part_sum_code,oe_number}
        self.db_commodity_goods_dict = dict()
        # uuid: list(attr_name,attr_value)
        self.db_commodity_goods_attr_dict = dict()

        self.init_commodity_goods()
        self.init_commodity_goods_attr()
        self.db_commodity_goods_attr_list = self.db_commodity_goods_attr_dict.keys()

        # ====== center数据====
        # attr_name:attr_id
        self.center_attr_config_dict = dict()
        self.init_center_attr()
        # == 帮助性的缓存数据
        # liyang_id : car_id
        self.liyang_car_dict = dict()
        self.init_liyang()
        self.liyang_car_list = self.liyang_car_dict.keys()

        self.save_key = '{}_{}'
        # 保存的数据 goods_format+brand_id : goods_data
        self.save_goods_dict = dict()
        # goods_format+brand_id: list(car_id)
        self.save_goods_car_dict = dict()
        # goods_format+brand_id: list(attr_id,attr_name,attr_value)
        self.save_goods_attr_dict = dict()

    # =========init 初始化========================
    def init_commodity_goods(self):
        goods_array = []
        for cat_id, cat_data in self.cat_id_dict.iteritems():
            goods_sql = "select uuId,brand_name,sale_unit,goods_format,part_name,part_sum_code from db_monkey_commodity_goods where part_sum_code like '" + \
                        cat_data['cat_code'] + "%' and isdelete = 0"
            goods_array.extend(self.dao.db.get_data(goods_sql))

        for goods_data in goods_array:
            goods_uuId = str(goods_data['uuId'])
            oe_number = ""
            # 获得oe
            oe_array = self.dao.db.get_data(
                "select oe_number from db_monkey_commodity_goods_oe where goods_uuId = '" + goods_uuId + "'")
            if len(oe_array) > 0:
                oe_number = str(oe_array[0]['oe_number']).replace(" ", "").upper()
            self.db_commodity_goods_dict[goods_uuId] = {
                'brand_name': str(goods_data['brand_name']),
                'sale_unit': str(goods_data['sale_unit']),
                'goods_format': str(goods_data['goods_format']),
                'part_name': str(goods_data['part_name']),
                'part_sum_code': str(goods_data['part_sum_code']),
                'oe_number': oe_number
            }

    def init_db_goods(self):
        goods_sql = "select goods_id,goods_format,cat_id,brand_id,goods_img,measure_unit,goods_img " \
                    "from db_goods where cat_id in (" + ",".join(self.cat_id_dict.keys()) + " ) "
        goods_array = self.dao.db.get_data(goods_sql)
        for goods_data in goods_array:
            goods_format = str(goods_data['goods_format']).strip()
            if '重复' in goods_format or "" == goods_format:
                continue
            self.db_goods_dict[str(goods_data['goods_id'])] = goods_data

    def init_db_brand(self):
        brand_sql = "select brand_id,brand_name from db_brand"
        brand_array = self.dao.db.get_data(brand_sql)
        for brand_data in brand_array:
            self.db_brand_dict[str(brand_data['brand_id'])] = str(brand_data['brand_name'])

    def init_liyang(self):
        liyang_sql = "select car_models_id,l_id from db_car_all "
        liyang_array = self.dao.db.get_data(liyang_sql)
        for liyang_data in liyang_array:
            self.liyang_car_dict[str(liyang_data['l_id'])] = str(liyang_data['car_models_id'])

    def init_db_attr(self):
        center_sql = "select id,attr_name from db_attribute_config where is_deleted = 'N'"
        center_attr_array = self.dao.db.get_data(center_sql)
        for attr_data in center_attr_array:
            self.db_attr_config_dict[str(attr_data['id'])] = str(attr_data['attr_name'])

    def init_center_attr(self):
        center_sql = "select id,attr_name from center_attr_config where is_deleted = 'N'"
        center_attr_array = self.dao.db.get_data(center_sql)
        for attr_data in center_attr_array:
            self.center_attr_config_dict[str(attr_data['attr_name'])] = str(attr_data['id'])

    def init_commodity_goods_attr(self):
        goods_uuid_attr_show_list = list()

        goods_attr_sql = "select goods_uuId,attr_name,attr_value from db_monkey_commodity_goods_attr order by gmt_modified desc"
        goods_attr_array = self.dao.db.get_data(goods_attr_sql)
        for goods_attr_data in goods_attr_array:
            goods_uuid = str(goods_attr_data['goods_uuId'])
            attr_name = str(goods_attr_data['attr_name']).split("(")[0]
            attr_value = str(goods_attr_data['attr_value'])

            if attr_name == "attr":
                continue
            if goods_uuid in self.db_commodity_goods_attr_dict.keys():
                attr_list = list(self.db_commodity_goods_attr_dict[goods_uuid])
            else:
                attr_list = list()

            show_key = goods_uuid + "_" + attr_name
            # 出现过
            if show_key not in goods_uuid_attr_show_list:
                goods_uuid_attr_show_list.append(show_key)
                attr_list.append({"attr_name": attr_name, "attr_value": attr_value})

            self.db_commodity_goods_attr_dict[goods_uuid] = attr_list

    # ============= end init 初始化========================


    # ============= start 获得 车型id list========================
    def get_car_id_by_liyang(self, liyang_id):
        if liyang_id in self.liyang_car_list:
            return self.liyang_car_dict[liyang_id]

        print "=====error===not have this liyang_id:%s" % liyang_id
        return "0"

    def get_car_list_by_goods_id(self, goods_id):
        car_id_list = list()
        car_sql = "SELECT car_id from db_goods_car where goods_id = " + goods_id
        car_array = self.dao.db.get_data(car_sql)
        for car_data in car_array:
            car_id_list.append(str(car_data['car_id']))
        return car_id_list

    def get_attr_by_db_goods(self, goods_id):
        attr_list = list()

        attr_id_show_list = list()
        goods_attr_sql = "select attr_id,attr_value from db_goods_attribute where is_deleted = 'N' and goods_id = " + str(
            goods_id) + " order by gmt_modified desc"
        goods_attr_array = self.dao.db.get_data(goods_attr_sql)
        for goods_attr_data in goods_attr_array:
            attr_name = self.db_attr_config_dict[str(goods_attr_data['attr_id'])]
            center_attr_id = self.center_attr_config_dict[attr_name]
            attr_value = str(goods_attr_data['attr_value']).strip()
            if attr_value == "":
                continue

            # 出现过，则不再存入
            if center_attr_id in attr_id_show_list:
                continue
            attr_id_show_list.append(center_attr_id)

            save_data = {"attr_id": center_attr_id, "attr_name": attr_name, "attr_value": attr_value}
            attr_list.append(save_data)

        return attr_list

    def get_attr_by_uuid(self, goods_uuid):
        attr_list = list()
        if goods_uuid in self.db_commodity_goods_attr_list:
            attr_data_list = self.db_commodity_goods_attr_dict[goods_uuid]
            for attr_data in attr_data_list:
                center_attr_id = self.center_attr_config_dict[attr_data['attr_name']]
                attr_data['attr_id'] = center_attr_id
                attr_list.append(attr_data)

        return attr_list

    def get_car_set_by_commidity_uuid(self, goods_uuid):
        car_id_set = set()
        liyang_sql = "select liyang_Id from db_monkey_commodity_goods_car " \
                     "where isdelete = 0 and goods_uuId = '" + goods_uuid + "'"
        liyang_array = self.dao.db.get_data(liyang_sql)
        for liyang_data in liyang_array:
            liyang_Id = str(liyang_data['liyang_Id'])
            car_id = self.get_car_id_by_liyang(liyang_Id)
            if int(car_id) > 0:
                car_id_set.add(car_id)

        return car_id_set

    def get_cat_id_by_code(self, sum_code):
        for cat_id, cat_data in self.cat_id_dict.iteritems():
            cat_code = cat_data['cat_code']
            if str(sum_code).startswith(cat_code):
                return cat_id

        return "0"

    # ============= start 获得 车型id list========================

    # 获得品牌
    def get_brand_id(self, search_brand_name):
        if search_brand_name == '摩擦1号':
            search_brand_name = '摩擦一号'
        for brand_id, brand_name in self.db_brand_dict.iteritems():
            if search_brand_name == brand_name:
                return brand_id
            if search_brand_name + "/" in brand_name:
                return brand_id
            if "/" + search_brand_name in brand_name:
                return brand_id

        print 'not have brand_id,name:%s' % search_brand_name
        return "0"

    # 处理电商的易损件
    def do_goods(self):
        for goods_id, goods_data in self.db_goods_dict.iteritems():

            car_id_list = self.get_car_list_by_goods_id(goods_id)
            if len(car_id_list) == 0:
                continue

            # 替换当中多余空格为-，替换中文空格，大写字母
            goods_format = "-".join(str(goods_data['goods_format']).split()).replace("（", "(").replace("）", ")").upper()

            goods_brand_key = self.save_key.format(goods_format, str(goods_data['brand_id']))
            brand_id = str(goods_data['brand_id'])
            cat_id = str(goods_data['cat_id'])
            save_goods_data = {'brand_id': brand_id, 'brand_name': self.db_brand_dict[brand_id],
                               'goods_unit': str(goods_data['measure_unit']),
                               'goods_format': goods_format, 'goods_pic': str(goods_data['brand_id']),
                               'third_cate_id': cat_id, 'part_name': str(self.cat_id_dict[cat_id]['cat_name']),
                               "goods_pic": str(goods_data['goods_img']), 'oe_number': ""}

            if goods_brand_key in self.save_goods_dict.keys():
                print "====error~!!!!=== 请仔细查看数据库，出现多个 goods_brand_key，确定后继续执行,%s", goods_brand_key
                continue

            self.save_goods_dict[goods_brand_key] = save_goods_data
            self.save_goods_car_dict[goods_brand_key] = car_id_list

            # 属性
            goods_attr_list = self.get_attr_by_db_goods(goods_id)
            self.save_goods_attr_dict[goods_brand_key] = goods_attr_list

    # 商品库
    def do_commodity(self):
        # uuid:{brand_name,sale_unit,goods_format,part_name,oe_number}
        for goods_uuid, goods_data in self.db_commodity_goods_dict.iteritems():
            car_id_set = self.get_car_set_by_commidity_uuid(goods_uuid)
            goods_format = "-".join(str(goods_data['goods_format']).split()).replace("（", "(").replace("）", ")").upper()
            brand_name = str(goods_data['brand_name']).upper()
            brand_id = self.get_brand_id(brand_name)
            goods_unit = str(goods_data['sale_unit'])
            part_name = str(goods_data['part_name'])
            part_sum_code = str(goods_data['part_sum_code'])
            oe_number = str(goods_data['oe_number'])

            goods_attr_list = self.get_attr_by_uuid(goods_unit)

            if brand_id == "0":
                goods_brand_key = self.save_key.format(goods_format, brand_name)
            else:
                goods_brand_key = self.save_key.format(goods_format, brand_id)

            if goods_brand_key not in self.save_goods_dict.keys():
                third_cate_id = self.get_cat_id_by_code(part_sum_code)
                if third_cate_id == "0":
                    print 'part_sum_code_is_wrong.goods_data:%s' % (json.dumps(goods_data))
                    continue
                # 如果没有车型，则不保存
                if len(car_id_set) == 0:
                    continue
                # 不在范围区间
                save_goods_data = {'brand_id': brand_id, 'brand_name': brand_name, 'goods_unit': goods_unit,
                                   'goods_format': goods_format, 'goods_pic': '',
                                   'third_cate_id': third_cate_id, 'part_name': part_name, "goods_pic": "",
                                   'oe_number': oe_number}
                self.save_goods_dict[goods_brand_key] = save_goods_data
                self.save_goods_car_dict[goods_brand_key] = car_id_set

                self.save_goods_attr_dict[goods_brand_key] = goods_attr_list

            else:
                # 在范围区间,属性就比较了
                save_goods_data = self.save_goods_dict[goods_brand_key]
                save_car_set = set(self.save_goods_car_dict[goods_brand_key])
                save_goods_attr_list = list(self.save_goods_attr_dict[goods_brand_key])

                # goods 更改
                is_goods_change = False
                if goods_unit != "" and save_goods_data['goods_unit'] != goods_unit:
                    save_goods_data['goods_unit'] = goods_unit
                    is_goods_change = True
                if part_name != "" and save_goods_data['part_name'] != part_name:
                    save_goods_data['part_name'] = part_name
                    is_goods_change = True
                if oe_number != "":
                    save_goods_data['oe_number'] = oe_number
                    is_goods_change = True
                if is_goods_change:
                    self.save_goods_dict[goods_brand_key] = save_goods_data

                # goods_car_list 更改
                is_car_id_change = False
                for car_id in car_id_set:
                    if car_id not in save_car_set:
                        save_car_set.add(car_id)
                        is_car_id_change = True
                if is_car_id_change:
                    self.save_goods_car_dict[goods_brand_key] = save_car_set

                # goods_attr 补充
                is_attr_change = False
                for co_attr_data in goods_attr_list:
                    attr_id = co_attr_data['attr_id']

                    is_in_save_list = False
                    for attr_data in save_goods_attr_list:
                        # 已经存在attr
                        if attr_data['attr_id'] == attr_id:
                            is_in_save_list = True
                            break
                    if not is_in_save_list:
                        save_goods_attr_list.append(co_attr_data)
                        is_attr_change = True
                if is_attr_change:
                    self.save_goods_attr_dict[goods_brand_key] = save_goods_attr_list

    def create_sql(self, file_address):
        # 处理数据
        insert_goods_list = list()
        insert_goods_car_list = list()
        insert_goods_attr_list = list()
        id = self.center_goods_max_id
        for goods_brand_key, save_data in self.save_goods_dict.iteritems():
            id += 1
            save_data["id"] = id
            insert_goods_list.append(save_data)
            # goods_car
            save_car_set = self.save_goods_car_dict[goods_brand_key]
            for car_id in save_car_set:
                goods_car_data = {"goods_id": id, "car_id": car_id}
                insert_goods_car_list.append(goods_car_data)

            # goods_attr
            goods_attr_list = self.save_goods_attr_dict[goods_brand_key]
            for goods_attr_data in goods_attr_list:
                goods_attr_data['goods_id'] = id
                insert_goods_attr_list.append(goods_attr_data)

        # 生成sql
        max_num = 3000
        start_string = "SET unique_checks=0;SET foreign_key_checks=0;set autocommit=0;\n"
        final_string = "commit;\n"
        time_string = "select @now_time := now();\n"
        insert_object = open(file_address, 'w')

        insert_object.writelines(start_string)
        insert_object.writelines(time_string)

        insert_help_list = list()
        try:
            # goods
            insert_object.writelines("# goods \n")
            for the_data in insert_goods_list:
                the_data['gmt_modified'] = '@now_time'
                the_data['gmt_create'] = '@now_time'

                insert_help_list.append(the_data)
                if len(insert_help_list) > max_num:
                    insert_object.writelines(self.dao.get_batch_sql("center_goods", insert_help_list))
                    insert_object.writelines(";\n")
                    insert_help_list = list()

            if len(insert_help_list) > 0:
                insert_object.writelines(self.dao.get_batch_sql("center_goods", insert_help_list))
                insert_object.writelines(";\n")
                insert_help_list = list()

            # goods_car
            insert_object.writelines("# goods_car \n")
            for the_data in insert_goods_car_list:
                the_data['gmt_modified'] = '@now_time'
                the_data['gmt_create'] = '@now_time'

                insert_help_list.append(the_data)
                if len(insert_help_list) > max_num:
                    insert_object.writelines(self.dao.get_batch_sql("center_goods_car_relation", insert_help_list))
                    insert_object.writelines(";\n")
                    insert_help_list = list()
            if len(insert_help_list) > 0:
                insert_object.writelines(self.dao.get_batch_sql("center_goods_car_relation", insert_help_list))
                insert_object.writelines(";\n")
                insert_help_list = []

            # goods_attr
            insert_object.writelines("# goods_attr \n")
            for the_data in insert_goods_attr_list:
                the_data['gmt_modified'] = '@now_time'
                the_data['gmt_create'] = '@now_time'

                insert_help_list.append(the_data)
                if len(insert_help_list) > max_num:
                    insert_object.writelines(self.dao.get_batch_sql("center_goods_attr_relation", insert_help_list))
                    insert_object.writelines(";\n")
                    insert_help_list = list()
            if len(insert_help_list) > 0:
                insert_object.writelines(self.dao.get_batch_sql("center_goods_attr_relation", insert_help_list))
                insert_object.writelines(";\n")
                insert_help_list = []

            insert_object.writelines(final_string)
        except Exception, e:
            print e
        finally:
            insert_object.close()

    # 核心执行的接口
    def sum_do(self, file_address):
        print "====start===="
        # 电商
        self.do_goods()
        # 商品库
        self.do_commodity()

        print "=====start create sql==="
        # 结果集产出sql
        self.create_sql(file_address)
        print "====end===="


file_address = os.getcwd() + "/wearingParts/insert.sql"
wearingParts = WearingParts()
wearingParts.sum_do(file_address)
