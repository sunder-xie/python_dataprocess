# encoding=utf-8
# 查看商品是否在数据库有关系
import os
import sys

__author__ = 'zxg'

from util import CrawlDao

if len(sys.argv) == 1:
    print "请输入 要查询的 db_monkey_part_goods 的 primary key"
    sys.exit()


primary_key = sys.argv[1]
dao = CrawlDao.CrawlDao("modeldatas", "online_cong")
# dao = CrawlDao.CrawlDao("modeldatas", "local")



goods_sql = "select uuid from db_monkey_part_goods_base where id =  " + primary_key
print "goods_sql:%s" % goods_sql
goods_array = dao.db.get_data(goods_sql)
if len(goods_array) == 0:
    print "此id 在 db_monkey_part_goods_base 不存在"
    sys.exit()
    
goods_uuid = str(goods_array[0]['uuid'])



relation_sql = 'select car_brand_name,liyang_table from db_monkey_part_liyang_table_relation'
relation_array = dao.db.get_data(relation_sql)

brand_index = 0
brand_sum = len(relation_array)
for relation_data in relation_array:
    car_brand_name = str(relation_data['car_brand_name'])
    liyang_table = str(relation_data['liyang_table'])

    brand_index += 1

    print "===start 处理品牌 %s-%s:%s" % (str(brand_sum), str(brand_index), car_brand_name)

    have_goods_sql = "select goods_id from " + liyang_table +" where goods_id = '"+goods_uuid+"'"

    print "the_sql: %s" % have_goods_sql
    have_array = dao.db.get_data(have_goods_sql)

    if len(have_array) > 0:
        print "==Happy~~!!!!!!== 此id 存在 对应关系goods_car 在这个表中===~~~~"
        sys.exit()

    print "==end 此品牌"


print "=======SAD~~~~~~~====此id 无对应关系 在任何品牌表============"

