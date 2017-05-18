# encoding=utf-8
__author__ = 'ximeng'
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from util import CrawlDao, FileUtil
import os
# 列名跟数据库字段对应
sql_goods_table = {
        'GRNO': 'figure',
        'UPGN': 'types',
        'PNCD': 'figure_index',
        'PTNO': 'oe_number',
        'OPCT': 'counts',
        'LGCH': 'name'
}

# test_name = 'D:\PythonExcle\epc-xiandai\伊兰特00 GEN080PA00.xlsx'
# excleArray = test_name.decode('utf-8').split('\\')
# excle_car_name = excleArray[len(excleArray)-1].split('.')[0]
# string = 'ABCDRF'
# string = string[len(string)-4:]
# start 遍历所有文件夹
fileDao = FileUtil.FileDao()

fileList = []
file_list = fileDao.get_file_list('D:\PythonExcle\epc-xiandai', fileList)
source = '现代EPC'
parentId = 18
for excle in file_list:
    print excle

    excle = excle.decode('utf-8')
    excleArray = excle.split('\\')
    excle_car_name = excleArray[len(excleArray)-1].split('.')[0]

    goods_car_data = dict()
    goods_car_data['name'] = excle_car_name
    goods_car_data['parentId'] = parentId
    goods_car_data['type'] = 'series'
    goods_car_data['source'] = source

    # 单个excle处理
    data = fileDao.open_excel(excle)
    table = data.sheets()[0]
    nrows = table.nrows  # 行数
    ncols = table.ncols  # 列数
    # 存车系
    dao = CrawlDao.CrawlDao()
    car_id = dao.insert_without_exit('dw_epc_car_brand', goods_car_data,goods_car_data)

    index_sql_table = {}
    # 第一行的列名
    first_row = table.row_values(0)
    for cols_num in range(1, ncols):
        cols_name = first_row[cols_num].strip()
        if u'字段1' == cols_name:
            sql_cols_name = 'name'
        else:
            sql_cols_name = sql_goods_table.get(cols_name[len(cols_name)-4:])
        index_sql_table[cols_num] = sql_cols_name

    # 遍历行的数据存入
    for rownum in range(1, nrows):
        row = table.row_values(rownum)
        goods_data = dict()
        goods_car_data = dict()
        for cols_num in range(1, ncols):
            value = row[cols_num]
            value = str(value).strip().replace("\"", "\'")
            if value == '':
                continue
            name = index_sql_table[cols_num]
            goods_data[name] = value
        goods_data['source'] = source
        goods_id = dao.insert_without_exit('dw_epc_goods', goods_data, goods_data)

        goods_car_data['goods_id'] = goods_id
        goods_car_data['car_id'] = car_id
        goods_car_data['car_parent_id'] = parentId
        dao.insert_without_exit('dw_epc_goods_car', goods_car_data, goods_car_data)
    print '=====end one excle===='
print '=====end all===='



