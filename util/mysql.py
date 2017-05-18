# -*- coding: UTF-8 -*-

__author__ = 'wcong'

import MySQLdb
import MySQLdb.cursors


def create_conf():
    conf = dict()
    conf['port'] = 3306
    conf['charset'] = 'utf8'
    return conf

# 本地环境的扒取库
def get_local_conf(db_name='crawl'):
    conf = create_conf()
    conf['host'] = '127.0.0.1'
    conf['user'] = 'root'
    conf['passwd'] = 'root'
    conf['db'] = db_name
    return conf


class PDBC:
    def __init__(self, conf):
        self.conn = MySQLdb.connect(host=conf['host'], user=conf['user'], passwd=conf['passwd'], db=conf['db'],
                                    port=conf['port'], charset=conf['charset'], cursorclass=MySQLdb.cursors.DictCursor)
        self.cur = self.conn.cursor()

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def get_data(self, sql):
        self.cur.execute(sql)
        result = self.cur.fetchall()
        return result

    def get_cursor(self, sql):
        self.cur.execute(sql)
        return self.cur

    def exec_data(self, sql):
        result = self.cur.execute(sql)
        self.conn.commit()
        return result

    # 插入函数，返回最后插入的主键id
    def insert_data(self, sql):
        self.cur.execute(sql)
        new_id = int(self.cur.lastrowid)
        self.conn.commit()
        return new_id

    # 更新函数
    def update_data(self, sql):
        self.cur.execute(sql)
        self.conn.commit()