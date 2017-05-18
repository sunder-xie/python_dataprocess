# encoding=utf-8
# center_goods

__author__ = 'zxg'

import sys

reload(sys)
sys.setdefaultencoding("utf-8")

from util import CrawlDao
import uuid
import re


class Center:
    def __init__(self):
        self.dao = CrawlDao.CrawlDao()
        self.user = 1


        # 电商brand_id对应的pic和name
        self.online_brand_name_dict = dict()
        self.online_brand_pic_dict = dict()
        db_brand_sql = "select brand_id,brand_name.brand_logo_app " \
                       "from db_brand"
        db_brand_array = self.dao.db.get_data(db_brand_sql)
        for db_brand_data in db_brand_array:
            brand_id = db_brand_data['brand_id']
            self.online_brand_name_dict[brand_id] = str(db_brand_data['brand_name'])
            self.online_brand_pic_dict[brand_id] = str(db_brand_data['brand_logo_app']).strip()

        # 电商brand_id对应的center brand_id
        self.brand_online_center_dict = dict()

        # 电商goods_id 对应的其 cat_id
        self.goods_online_cat_dict = dict()
        # 电商goods_id 对应的center goodsuuid
        self.goods_online_uuid_dict = dict()
        # center goodsId goodsuuid
        self.goods_center_uuid_dict = dict()

        # attr
        self.online_attr_name_dict = dict()
        db_attr_key_sql = "select id,attr_name from db_attribute_config"
        db_attr_key_array = self.dao.db.get_data(db_attr_key_sql)
        for db_attr_key_data in db_attr_key_array:
            self.online_attr_name_dict[db_attr_key_data['id']] = db_attr_key_data['attr_name']
        # online attrkey+cat => center attrkey
        self.attr_key_online_center_dict = dict()

    def main(self):
        self.handle_goods()

    # 处理电商数据到center中
    def handle_goods(self):
        db_goods_sql = "select goods_id,cat_id,goods_name,brand_id,goods_img,goods_format,package_format," \
                       "factory_code,min_package,product_company,min_measure_unit,oe_num,goods_quality_type " \
                       "from db_goods " \
                       "where seller_id = 1 and is_delete = 0"
        db_goods_array = self.dao.db.get_data(db_goods_sql)
        for db_goods_data in db_goods_array:
            online_goods_id = db_goods_data['goods_id']

            brand_id = db_goods_data['brand_id']
            center_brand_array = self.change_brand_online_to_center(brand_id)
            if not center_brand_array:
                print "==============该线上goodsid：%s，不存在" % online_goods_id
                continue

            goods_format = db_goods_data['goods_format']
            factory_code = db_goods_data['factory_code']
            oe_num = db_goods_data['oe_num'].strip()
            cat_id = db_goods_data['cat_id']

            self.goods_online_cat_dict[online_goods_id] = cat_id
            center_uuid = uuid.uuid1()

            center_goods_data = {
                'uuid': center_uuid,
                'goods_quality_type': db_goods_data['goods_quality_type'],
                'brand_id': center_brand_array['center_brand_id'],
                'brand_name': center_brand_array['center_brand_name'],
                'goods_format': self.wipe_string_ch(goods_format),
                'goods_format_after': self.wipe_string(goods_format),
                'goods_factory_code': self.wipe_string_ch(factory_code),
                'goods_factory_code_after': self.wipe_string(factory_code),
                'product_company': str(db_goods_data['product_company']).strip(),
                'goods_name': str(db_goods_data['goods_name']).strip(),
                'goods_category_id': cat_id,
                'min_measure_unit': str(db_goods_data['min_measure_unit']).strip(),
                'package_format': str(db_goods_data['package_format']).strip(),
                'goods_img': str(db_goods_data['goods_img']).strip(),
                # 全部标明为 易损件
                'goods_type': 0
            }

            self.save_center_goods(center_goods_data, online_goods_id)

            self.save_center_goods_oe(oe_num, online_goods_id)

    # center goods_attr
    def handle_goods_attr(self):
        for online_goods_id in self.goods_online_cat_dict.keys():
            db_attrbute_sql = "select attr_id,attr_value from db_goods_attribute where is_deleted='N' " \
                              "and goods_id='" + str(online_goods_id) + "'"
            db_attrbute_array = self.dao.db.get_data(db_attrbute_sql)
            for db_attrbute_data in db_attrbute_array:
                attr_id = db_attrbute_data['attr_id']
                attr_value = db_attrbute_data['attr_value']
                # 将attr_id 转化为 center attr_id
                center_attr_id = self.save_goods_attr_key(attr_id, online_goods_id)
                attr_name = self.online_attr_name_dict[attr_id]
                goods_uuId = self.goods_online_uuid_dict[online_goods_id]

                goods_attr_data = {
                    'goods_uuid': goods_uuId,
                    'attr_id': center_attr_id,
                    'attr_name': attr_name,
                    'attr_value': attr_value,
                    'create_user_id': self.user,
                    'update_user_id': self.user
                }
                goods_attr_exist_data = {
                    'goods_uuid': goods_uuId,
                    'attr_id': center_attr_id,
                }
                self.dao.insert_without_exit("center_goods_attr", goods_attr_data, goods_attr_exist_data)

    # ==============================私有处理 方法==========================
    # 将电商brand id，匹配到center brand中，存对应关系，返回center brand_name 和 center brand_id
    def change_brand_online_to_center(self, online_brand_id):
        if online_brand_id in self.online_brand_name_dict:
            online_brand_name = self.online_brand_name_dict[online_brand_id]

            if online_brand_id in self.brand_online_center_dict:
                center_brand_id = self.brand_online_center_dict[online_brand_id]
            else:
                center_brand_sql = "select id from center_goods_brand where name = '" + online_brand_name + "'"
                center_data_array = self.dao.db.get_data(center_brand_sql)
                if center_data_array:
                    center_brand_id = center_data_array[0]['id']
                else:
                    center_brand_id = 0
                    print "==============无对应的center brand，online name = ：%s" % online_brand_name
                self.brand_online_center_dict[online_brand_id] = center_brand_id

            return {'center_brand_id': center_brand_id, 'center_brand_name': online_brand_name}
        else:
            print "==============该线上brandid：%s，不存在" % online_brand_id
            return False

    # 去除空格和特殊字符
    def wipe_string(self, string):
        result_list = re.subn(u'[^\w]', '', string)

        return result_list[0].upper()

    # 去除中文
    def wipe_string_ch(self, string):
        result_list = re.subn(u'[\u4e00-\u9fa5]+', '', string.strip())
        return result_list[0]

    # ==============================save 方法==========================

    def save_center_goods(self, center_goods_data, online_goods_id):
        center_goods_data['create_user_id'] = self.user
        center_goods_data['update_user_id'] = self.user

        exist_data = {
            'goods_quality_type': center_goods_data['goods_quality_type'],
            'brand_id': center_goods_data['brand_id'],
            'goods_format': center_goods_data['goods_format'],
            'goods_factory_code': center_goods_data['goods_factory_code'],
            'product_company': center_goods_data['product_company'],
        }

        is_data = self.dao.boolean_exit('center_goods', exist_data)
        if is_data:
            center_goods_id = is_data[0]['id']
            center_uuid = self.goods_center_uuid_dict[center_goods_id]
        else:
            center_uuid = center_goods_data['uuid']
            center_goods_id = self.dao.insert_temple('center_goods', center_goods_data)
            self.goods_center_uuid_dict[center_goods_id] = center_uuid

        self.goods_online_uuid_dict[online_goods_id] = center_uuid

    def save_center_goods_oe(self, oe_string, online_goods_id):
        oe_array = oe_string.replace("，", ",").split(",")
        for oe_num in oe_array:
            oe_num_original = self.wipe_string_ch(oe_num)
            oe_num_after = self.wipe_string(oe_num)
            if oe_num_after == "":
                continue

            center_uuid = self.goods_online_uuid_dict[online_goods_id]
            oe_data = {
                'goods_uuid': center_uuid,
                'oe_number': oe_num_original,
                'oe_number_after': oe_num_after,
                'create_user_id': self.user,
                'update_user_id': self.user
            }
            oe_exist = {
                'goods_uuid': center_uuid,
                'oe_number': oe_num_original
            }
            self.dao.insert_without_exit("center_goods_oe", oe_data, oe_exist)

    def save_goods_attr_key(self, online_attr_key, online_goods_id):
        attr_name = self.online_attr_name_dict[online_attr_key]
        cat_id = self.goods_online_cat_dict[online_goods_id]
        key = attr_name + "_" + cat_id
        if key in self.attr_key_online_center_dict.keys():
            attr_key_id = self.attr_key_online_center_dict[key]
        else:
            attr_key_data = {
                'attr_name': attr_name,
                'cat_id': cat_id,
                'create_user_id': self.user,
                'update_user_id': self.user
            }
            attr_exist_data = {
                'attr_name': attr_name,
                'cat_id': cat_id
            }

            attr_key_id = self.dao.insert_without_exit("center_goods_attr_key", attr_key_data, attr_exist_data)
            self.attr_key_online_center_dict[key] = attr_key_id

        return attr_key_id
