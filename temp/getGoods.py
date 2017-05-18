# encoding=utf-8
# 从库数据生成插入语句
import os
import datetime

__author__ = 'zxg'

import CrawlDao


def get_batch_sql(table, batch_list):
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


file_object = open(os.getcwd() + '/db_goods.sql', 'w')

try:
    file_object.writelines("SET NAMES utf8;SET FOREIGN_KEY_CHECKS = 0;DROP TABLE IF EXISTS db_goods;\n")

    file_object.writelines("CREATE TABLE db_goods ( "
                           "cat_id smallint(5) unsigned NOT NULL DEFAULT '0' COMMENT '商品分类ID',"
                           "new_goods_sn varchar(16) NOT NULL DEFAULT '0' COMMENT '2014年3月12日新版的商品编号',"
                           "PRIMARY KEY (new_goods_sn)"
                           ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='商品基础信息表';\n")

    dao = CrawlDao.CrawlDao('', 'stall')

    file_object.writelines("BEGIN;\n")
    insert_list = list()
    goods_array = dao.db.get_data("select cat_id,new_goods_sn from db_goods ")
    for goods_data in goods_array:
        insert_list.append(goods_data)

        if len(insert_list) > 5000:
            sql_string = get_batch_sql('db_goods',insert_list)
            file_object.writelines(sql_string)
            file_object.writelines(";\n")
            insert_list = list()

    if len(insert_list) > 0:
        sql_string = get_batch_sql('db_goods',insert_list)
        file_object.writelines(sql_string)
        file_object.writelines(";\n")
        insert_list = list()

    file_object.writelines("COMMIT;SET FOREIGN_KEY_CHECKS = 1;\n")
finally:
    file_object.close()
