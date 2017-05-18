# encoding=utf-8
# 生成爬取的数据的excle

__author__ = 'zxg'

import sys
import os
import xlwt

reload(sys)
sys.setdefaultencoding("utf-8")

from util import CrawlDao


class CrawlExcle:
    def __init__(self, *name, **kwargs):
        # super(OfferGoods, self).__init__(*name, **kwargs)
        self.dao = CrawlDao.CrawlDao()
        self.file_name = r'/Users/zxg/Desktop/text.xls'
        # 新建一个excel文件
        self.file = xlwt.Workbook(encoding='utf-8')
        # base sheet
        self.car_sheet = None

        # 所有truck id 对应的行
        self.truck_id_dict = dict()
        # 所有other sheet
        self.other_sheet_list = list()
        # 参数对应的sheet
        self.attr_sheet = dict()
        # 参数对应的列
        self.attr_column = dict()


        # ===========车辆类型============
        # type id - name
        self.type_name = dict()
        # type id -pid
        self.type_pid = dict()

        select_type_sql = "select id,type_name,pid from sc_truck_car_type"
        type_array = self.dao.db.get_data(select_type_sql)
        for type_data in type_array:
            id = type_data['id']
            type_name = type_data['type_name']
            pid = type_data['pid']
            self.type_name[id] = type_name
            self.type_pid[id] = pid

        # ===========品牌=========
        # car id - name
        self.car_name = dict()
        # car id -pid
        self.car_pid = dict()
        car_category_sql = "select id,car_name,pid from sc_truck_car_category"
        car_array = self.dao.db.get_data(car_category_sql)
        for car_data in car_array:
            id = car_data['id']
            car_name = car_data['car_name']
            pid = car_data['pid']
            self.car_name[id] = car_name
            self.car_pid[id] = pid

    def start(self):
        if os.path.exists(self.file_name):
            # 存在文件，则先删除
            os.remove(self.file_name)

    def create_heard(self):
        # =========第一个基本sheet=============
        self.car_sheet = self.file.add_sheet(u"基础")
        # 第一行
        self.car_sheet.write(0, 0, u'唯一标识')
        self.car_sheet.write(0, 1, u'名称')
        self.car_sheet.write(0, 2, u'价格')
        self.car_sheet.write(0, 3, u'类型组别')
        self.car_sheet.write(0, 4, u'车型类型')
        self.car_sheet.write(0, 5, u'品牌')
        self.car_sheet.write(0, 6, u'车系')
        self.car_sheet.write(0, 7, u'来源')

        # 动态生成参数的sheet
        attr_key_sql = 'select group_name from sc_attr_key GROUP BY  group_name ORDER BY id'
        print 'attr_key_sql : %s' % attr_key_sql

        attr_key_array = self.dao.db.get_data(attr_key_sql)
        for attr_key_data in attr_key_array:
            group_name = attr_key_data['group_name']
            base_attr_sheet = self.file.add_sheet(u"参数-" + group_name)
            self.other_sheet_list.append(base_attr_sheet)
            # sheet 的第一行
            base_attr_sheet.write(0, 0, u'唯一标识')
            attr_key_true_sql = "select id,key_name from sc_attr_key where group_name = '" + str(group_name) + "'"
            attr_key_true_array = self.dao.db.get_data(attr_key_true_sql)
            index = 1
            for attr_key_true_data in attr_key_true_array:
                attr_key_true_name = attr_key_true_data['key_name']
                attr_key_true_id = attr_key_true_data['id']
                base_attr_sheet.write(0, index, attr_key_true_name)

                self.attr_sheet[attr_key_true_id] = base_attr_sheet
                self.attr_column[attr_key_true_id] = index
                index += 1

    # 第一个sheet
    def add_data_to_first_sheet(self):
        base_sql = "select id,car_name,price,car_type_id,car_category_id,source from sc_truck_car"
        print 'base_sql : %s' % base_sql

        base_array = self.dao.db.get_data(base_sql)
        row_index = 1
        for base_data in base_array:
            truck_id = base_data['id']
            self.truck_id_dict[truck_id] = row_index
            self.car_sheet.write(row_index, 0, truck_id)
            self.car_sheet.write(row_index, 1, base_data['car_name'])
            self.car_sheet.write(row_index, 2, base_data['price'])

            # 类别
            type_id = base_data['car_type_id']
            if int(type_id) != 0:
                type_name = self.type_name[type_id]
                pid = self.type_pid[type_id]
                self.car_sheet.write(row_index, 4, type_name)
                if int(pid) != 0:
                    self.car_sheet.write(row_index, 3, self.type_name[pid])
            # 车型
            car_id = base_data['car_category_id']
            if int(car_id) > 0:
                car_name = self.car_name[car_id]
                pid = self.car_pid[car_id]
                if int(pid) == 0:
                    self.car_sheet.write(row_index, 5, car_name)
                else:
                    self.car_sheet.write(row_index, 5, self.car_name[pid])
                    self.car_sheet.write(row_index, 6, car_name)

            self.car_sheet.write(row_index, 7, base_data['source'])
            row_index += 1

    # 生成其他sheet
    def add_data_to_other_sheet(self):
        for truck_id in self.truck_id_dict.keys():
            row_number = self.truck_id_dict[truck_id]
            for sheet in self.other_sheet_list:
                sheet.write(row_number, 0, truck_id)

            attr_sql = "select attr_key_id,attr_value from sc_truck_car_attr where car_id = " + str(truck_id)
            print 'attr_sql : %s' % attr_sql
            attr_array = self.dao.db.get_data(attr_sql)
            for attr_data in attr_array:
                attr_key = attr_data['attr_key_id']
                attr_value = attr_data['attr_value']

                sheet = self.attr_sheet[attr_key]
                column = self.attr_column[attr_key]
                sheet.write(row_number, column, attr_value)

    def final(self):

        # 保存文件
        self.file.save(self.file_name)

    def main(self):
        print 'start'
        self.start()
        self.create_heard()
        self.add_data_to_first_sheet()
        self.add_data_to_other_sheet()
        self.final()
        print 'end'


start = CrawlExcle()
start.main()
