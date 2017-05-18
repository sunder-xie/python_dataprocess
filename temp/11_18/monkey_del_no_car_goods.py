# encoding=utf-8
# 删除配件库无车型对应关系的商品
import os

__author__ = 'zxg'

from util import CrawlDao


class DelNoCarRelationGoods:
    def __init__(self):
        self.dao = CrawlDao.CrawlDao("modeldatas", "online_cong")
        # self.dao = CrawlDao.CrawlDao("modeldatas", "local")

        self.have_goods_uuid_set = set()

        self.need_del_id_list = list()
        pass

    def have_relation_goods(self):
        relation_sql = 'select car_brand_name,liyang_table from db_monkey_part_liyang_table_relation'
        relation_array = self.dao.db.get_data(relation_sql)

        brand_index = 0
        brand_sum = len(relation_array)
        for relation_data in relation_array:
            car_brand_name = str(relation_data['car_brand_name'])
            liyang_table = str(relation_data['liyang_table'])

            brand_index += 1

            print "===start 处理品牌 %s-%s:%s" % (str(brand_sum), str(brand_index), car_brand_name)

            have_goods_sql = "select distinct goods_id from " + liyang_table
            have_array = self.dao.db.get_data(have_goods_sql)

            for have_data in have_array:
                goods_id = str(have_data['goods_id'])
                self.have_goods_uuid_set.add(goods_id)

            print "==end 此品牌"

    def find_no_relation_goods(self):
        goods_sql = "select id,uuid from db_monkey_part_goods_base "
        goods_array = self.dao.db.get_data(goods_sql)
        for goods_data in goods_array:
            id = str(goods_data['id'])
            uuid = str(goods_data['uuid'])

            if uuid in self.have_goods_uuid_set:
                continue

            self.need_del_id_list.append(id)

    def write_sql(self, write_address):
        max_num = 3000
        start_string = "SET unique_checks=0;SET foreign_key_checks=0;set autocommit=0;\n"
        final_string = "commit;\n"
        time_string = "select @now_time := now();\n"
        del_obj = open(write_address, 'w')

        del_obj.writelines(start_string)
        # up_obj.writelines(time_string)

        del_list = list()
        for id in self.need_del_id_list:
            del_list.append(id)

            if len(del_list) > max_num:
                del_sql = "delete from db_monkey_part_goods_base where id in (" + ",".join(del_list) + ") "
                del_obj.writelines(del_sql)
                del_obj.writelines(";\n")
                del_list = list()
        if len(del_list) > 0:
            del_sql = "delete from db_monkey_part_goods_base where id in (" + ",".join(del_list) + ") "
            del_obj.writelines(del_sql)
            del_obj.writelines(";\n")
            del_list = list()

        del_obj.writelines(final_string)

    def do_process(self, write_address):
        print "===start ==="
        print "  "
        self.have_relation_goods()
        print "========end 1.have_relation_goods========"
        print "  "

        self.find_no_relation_goods()
        print "========end 2.find_no_relation_goods========"
        print "  "
        self.write_sql(write_address)
        print "========end 3.write_sql========"

        print "  "
        print "===end ==="


if __name__ == '__main__':
    file_address = os.getcwd() + "/del_monkey_goods.sql"
    delFunc = DelNoCarRelationGoods()
    delFunc.do_process(file_address)
