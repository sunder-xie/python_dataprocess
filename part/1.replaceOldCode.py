# encoding=utf-8
# 替换excel中老的标准零件名称和编号
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

dao = CrawlDao.CrawlDao("modeldatas", "local")
fileDao = FileUtil.FileDao()
stringUtil = StringUtil.StringUtil()

print 1
# 更改part名称
change_part_name_dict = {'空气滤清器芯': '空气滤清器', '车顶前扶手': '车顶前扶手(右)', '后座椅安全带导向板(左': '后座椅安全带导向板(左)',
                         '空调管(空调泵-蒸发器': '空调管(空调泵-蒸发器)','燃油箱门开启开启手柄':'燃油箱门开启手柄','分动箱油':'分动器油'}
def change_part_name(ws, part_name, rownum, clos):
    is_change = False
    if part_name in change_part_name_dict.keys():
        is_change = True
        part_name = change_part_name_dict[part_name]
    elif "（" in part_name or "）" in part_name:
        is_change = True
        part_name = part_name.replace("（", "(").replace("）", ")")

    if is_change:
        ws.write(rownum, clos, part_name.decode('UTF-8'))

    return part_name

# 将C 的标准零件编号 写入 dict 中 part_name:part_code
part_dict = dict()
part_array = dao.db.get_data(
    "SELECT part_name,sum_code FROM db_category_part WHERE is_deleted = 'N' AND vehicle_code != 'H'")
for part_data in part_array:
    part_dict[str(part_data['part_name'])] = str(part_data['sum_code'])

fileList = []
file_list = fileDao.get_file_list('/Users/zxg/Documents/fromFtp/test', fileList)

for excle in file_list:
    if '.DS_Store' in excle or '~$' in excle:
        continue
    print excle
    # 单个excle处理
    data = fileDao.open_excel(excle)
    table = data.sheets()[0]
    nrows = table.nrows  # 行数
    ncols = table.ncols  # 列数

    name_cols_num = 0
    code_cols_num = 0
    # 第一行的列名
    first_row = table.row_values(0)
    for cols_num in range(0, ncols):
        cols_name = first_row[cols_num].strip().upper()
        if u'标准零件名称' in cols_name:
            name_cols_num = cols_num
        elif u'标准零件编码' in cols_name or u'标准零件ID' in cols_name:
            code_cols_num = cols_num

    newname = excle
    portion = os.path.splitext(excle)  # 如果后缀是.txt
    if portion[1] == '.xlsx':
        newname = portion[0] + ".xls"
        os.rename(excle, newname)

    rb = open_workbook(newname)

    wb = copy(rb)

    # 通过get_sheet()获取的sheet有write()方法
    ws = wb.get_sheet(0)

    # 遍历所有行，把标准零件编码进行更改
    for rownum in range(1, nrows):
        row = table.row_values(rownum)
        the_part_name = str(row[name_cols_num])
        the_part_code = str(row[code_cols_num])
        the_part_name = change_part_name(ws, the_part_name, rownum, name_cols_num)
        try:
            if the_part_name not in part_dict.keys():
                print 'the_part_name not in part_dict:%s' % the_part_name
            # if the_part_name in part_dict.keys():
            #     code = part_dict[the_part_name]
            #     if the_part_code != code:
            #         ws.write(rownum, code_cols_num, code)
        except:
            print 'name:%s,code:%s' % (the_part_name, str(row[code_cols_num]))

    # wb.save(newname.decode('UTF-8'))
