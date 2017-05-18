# encoding=utf-8
# 产出途虎匹配后的结果excel
from decimal import Decimal
import os

__author__ = 'zxg'

import sys

from xlrd import open_workbook
from xlutils.copy import copy

reload(sys)
sys.setdefaultencoding("utf-8")
sys.path.append(os.getcwd() + "../util/")

from util import HttpUtil, CrawlDao, FileUtil, StringUtil

excel_address = r'/Users/zxg/Desktop/途虎车型机油处理/最后结果.xls'
need_sql = True
need_out_excel = False

dao = CrawlDao.CrawlDao("test", "local")
fileDao = FileUtil.FileDao()

# 初始化
tuhu_oil_dict = dict()
the_sql = "select online_car_id,oil,od_the_car_ids,is_not_have from tuhu_oil_result"
the_array = dao.db.get_data(the_sql)
for the_data in the_array:
    tuhu_oil_dict[str(the_data['online_car_id'])] = the_data
if need_out_excel:
    # 单个excle处理
    data = fileDao.open_excel(excel_address)
    table = data.sheets()[0]
    nrows = table.nrows  # 行数
    ncols = table.ncols  # 列数

    rb = open_workbook(excel_address)

    wb = copy(rb)

    # 通过get_sheet()获取的sheet有write()方法
    ws = wb.get_sheet(0)

    # 遍历所有行，把标准零件编码进行更改
    for rownum in range(1, nrows):
        row = table.row_values(rownum)
        online_car_id = str(row[0]).strip().replace(".0","")

        tuhu_oil_data = tuhu_oil_dict[online_car_id]
        ws.write(rownum, 13, str(tuhu_oil_data['oil']).decode('UTF-8'))
        ws.write(rownum, 14, str(tuhu_oil_data['od_the_car_ids']).decode('UTF-8'))
        ws.write(rownum, 15, str(tuhu_oil_data['is_not_have']).decode('UTF-8'))


    wb.save(excel_address.decode('UTF-8'))

# 生存更新的sql
if need_sql:
    need_up_dict = dict()
    for car_id,car_data in tuhu_oil_dict.iteritems():
        oil = str(car_data['oil'])
        if oil == "":
            continue
        if oil in need_up_dict.keys():
            id_list = list(need_up_dict[oil])
        else:
            id_list = list()
        id_list.append(car_id)
        need_up_dict[oil] = id_list


    update_list = list()
    update_list.append("SET unique_checks=0;SET foreign_key_checks=0;set autocommit=0")
    for oil_num,id_list in need_up_dict.iteritems():
        update_list.append("update db_car_category set oil_capacity = '"+oil_num+"' where id in ("+",".join(id_list)+")")

    update_list.append("commit;")

    file_object = open(r'/Users/zxg/Desktop/途虎车型机油处理/update_car.sql', 'w')

    try:
        file_object.writelines(";\n".join(update_list))
    finally:
        file_object.close()