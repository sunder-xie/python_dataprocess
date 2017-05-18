# encoding=utf8
import mysql
import sys

__author__ = 'wcong && zhongxi'

reload(sys)
sys.setdefaultencoding("utf-8")

import datetime
import re

db_goods_unique_key = ['source_goods_id', 'source_id']


class CrawlDao:
    html_tag = re.compile(r'<[^>]+>', re.S)

    def __init__(self, table_name='test', ip_type='test'):
        # 测试monkey库＆＆爬虫
        if ip_type == 'test':
            conf = mysql.get_test_out_conf(table_name)
        elif ip_type == 'test_in':
            conf = mysql.get_test_in_conf(table_name)
        elif ip_type == 'online_cong':
            # 线上monkey库,从库
            conf = mysql.get_online_cong_conf(table_name)
        elif ip_type == 'local':
            conf = mysql.get_local_conf(table_name)
        elif ip_type == 'stall':
            conf = mysql.get_online_stall_conf(table_name)

        self.db = mysql.PDBC(conf)
        # self.slave_db = mysql.PDBC(mysql.get_slave_conf())

    # 查找数据
    def select_temple(self, table, select_list, where_dict):
        # 判断内容
        where_list = list()
        where_list.append('1 = 1')
        for key, value in where_dict.items():
            where_list.append('%s = "%s"' % (key, str(value)))
        # 拼sql
        sql = 'select %s from %s' % (','.join(select_list), table)
        sql += ' where  %s ' % (' and '.join(where_list))
        print 'selecr sql:%s' % sql

        data = self.db.get_data(sql)
        return data

    # 更新数据,返回更新语句
    def update_temple(self, table, db_dict, where_dict):
        gmt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
        print 'update sql: %s' % sql
        self.db.update_data(sql)
        return sql

    # 插入数据
    def insert_temple(self, table, dic, replace=False):
        # gmt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # dic['gmt_create'] = gmt
        # dic['gmt_modified'] = gmt
        if replace:
            action = 'replace'
        else:
            action = 'insert'
        sql = action + ' into ' + table + '(' + ','.join(dic.keys()) + ') values'
        value_list = list()
        for key, value in dic.items():
            value = str(value).replace('"', '')
            value_list.append('"' + self.html_tag.sub('', str(value)) + '"')
        sql += '(' + ','.join(value_list) + ')'
        print '%s;' % sql
        return self.db.insert_data(sql)
        # return sql

    # 批量插入数据
    def insert_batch_temple(self, table, batch_list, is_replace=False):
        gmt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for i in batch_list:
            i['gmt_create'] = gmt
            i['gmt_modified'] = gmt
        action = 'insert ignore'
        if is_replace:
            action = 'replace'
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
        print sql
        self.db.exec_data(sql)
        return sql

    # 判断数据存不存在
    def boolean_exit(self, table, db_dict, primary_id='id', others_sql=''):
        value_list = list()
        for key, value in db_dict.items():
            if key in ('gmt_create', 'gmt_modified'):
                continue
            value_list.append(' %s = "%s" ' % (key, str(value)))

        select_sql = 'select '+primary_id+' from %s where %s' % (table, 'and'.join(value_list))
        select_sql += others_sql
        print '判断存在不存在的sql：%s' % select_sql

        data = self.db.get_data(select_sql)
        return data

    # 插入数据，若存在则不插入,筛选条件为db_exit
    def insert_without_exit(self, table, db_dict, db_exit, primary_id='id', others_sql=''):
        data = self.boolean_exit(table, db_exit, primary_id, others_sql)
        if data:
            return data[0][primary_id]
        else:
            primary_key_id = self.insert_temple(table, db_dict)
            return primary_key_id

    # 根据条件更新数据，返回id，若不存在数据，则插入返回自增id
    def insert_or_update_without_exit(self, table, db_dict, db_exit, primary_id='id', others_sql=''):
        data = self.boolean_exit(table, db_exit, primary_id, others_sql)
        if data:
            length = len(data)
            if length > 1:
                print 'have >1 id need update'
            key_id = data[0][primary_id]
            where_dict = dict()
            where_dict[primary_id] = key_id
            self.update_temple(table, db_dict, where_dict)
            return key_id
        else:
            primary_key_id = self.insert_temple(table, db_dict)
            return primary_key_id

    # 仅仅更新，若不存在，则跑出错误
    def only_update_without_exit(self, table, db_dict, db_exit, primary_id='id', others_sql=''):
        data = self.boolean_exit(table, db_exit, primary_id, others_sql)
        if data:
            key_id = data[0][primary_id]
            where_dict = dict()
            where_dict[primary_id] = key_id
            self.update_temple(table, db_dict, where_dict)
            return key_id
        else:
            print 'not exit this sql %s' % db_exit
            return 0

    #  插入数据，如果存在唯一索引执行更新操作，这儿通过on duplicate key update实现，所以主键不会执行更新操作
    def insert_or_update_template(self, table, db_dict, unique_key, primary_name='id'):
        select_sql = str()
        for key in unique_key:
            select_sql += key + ' = "' + str(db_dict[key]) + '" and '
        primary_key_id = 0
        if select_sql:
            select_sql = 'select id from %s where %s' % (table, select_sql[:-5])
            data = self.db.get_data(select_sql)
            if data:
                primary_key_id = data[0][primary_name]
        if primary_key_id > 0:
            gmt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db_dict['gmt_modified'] = gmt
            value_list = list()
            for key, value in db_dict.items():
                value_list.append('%s = "%s"' % (key, str(value)))
            self.db.exec_data('update %s set %s %s' % (
                table, ','.join(value_list), ' where %s = %d' % (primary_name, primary_key_id)))
        else:
            primary_key_id = self.insert_temple(table, db_dict)
        return primary_key_id

    # =====不执行仅出 语句＝＝＝＝＝＝＝＝＝
    # 拼写成sql
    def get_insert_sql(self, table, dic):
        gmt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dic['gmt_create'] = gmt
        dic['gmt_modified'] = gmt
        sql = 'insert into ' + table + '(' + ','.join(dic.keys()) + ') values'
        value_list = list()
        for key, value in dic.items():
            value = str(value).replace('"', '')
            value_list.append('"' + self.html_tag.sub('', str(value)) + '"')
        sql += '(' + ','.join(value_list) + ')'
        return sql

    def get_batch_sql(self, table, batch_list):
        sql = 'insert into ' + table + '(' + ','.join(batch_list[0].keys()) + ') values'
        value_list = list()
        for i in batch_list:
            inner_value_list = list()
            for key, value in i.items():
                if isinstance(value, str) or isinstance(value, unicode):
                    if value == "@now_time":
                        append_value = "@now_time"
                    else:
                        append_value = '"' + value + '"'
                    inner_value_list.append(append_value)
                else:
                    if value is None:
                        inner_value_list.append("NULL")
                    else:
                        inner_value_list.append(str(value))
            value_list.append('(' + ','.join(inner_value_list) + ')')
        sql += ','.join(value_list)
        return sql
