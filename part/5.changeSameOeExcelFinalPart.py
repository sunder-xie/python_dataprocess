# encoding=utf-8
# 更改处理后的 最新的 part name和code
import sys

__author__ = 'zxg'

reload(sys)
sys.setdefaultencoding("utf-8")

from xlrd import open_workbook
from xlutils.copy import copy
from util import HttpUtil, CrawlDao, FileUtil, StringUtil

dao = CrawlDao.CrawlDao("modeldatas", "local")
fileDao = FileUtil.FileDao()




part_dict = dict()
part_array = dao.db.get_data("SELECT part_name,sum_code "
                             "FROM db_category_part WHERE is_deleted = 'N' AND vehicle_code BETWEEN 'C' and 'CH'")
for part_data in part_array:
    part_dict[str(part_data['part_name'])] = str(part_data['sum_code'])

h_list = list()
part_h_array = dao.db.get_data("SELECT part_name "
                             "FROM db_category_part WHERE is_deleted = 'N' AND vehicle_code = 'H'")
for one in part_h_array:
    h_list.append(str(one['part_name']))

newname = r'/Users/zxg/Documents/work/淘气档口/work/2016.06 monkey－part/相同oe不同标准零件名称（完成）.xls'
# 单个excle处理
data = fileDao.open_excel(newname)
table = data.sheets()[0]
nrows = table.nrows  # 行数
ncols = table.ncols  # 列数

name_cols_num = 0
code_cols_num = 0

rb = open_workbook(newname)

wb = copy(rb)

# 通过get_sheet()获取的sheet有write()方法
ws = wb.get_sheet(0)

# 遍历所有行，把标准零件编码进行更改
has_show_list = list()
for rownum in range(1, nrows):
    row = table.row_values(rownum)
    id = str(row[0])
    part_name = str(row[9])
    part_code = str(row[10]).replace(".0", "")
    if part_name == '':
        print 'id：%s,为空part name' % id
        continue

    if part_name not in part_dict.keys():
        if part_name not in h_list:
            print 'part name not in part_dict:%s'%part_name
            has_show_list.append(part_name)

        continue
    new_part_code = part_dict[part_name]
    if part_code != '':
        if part_code != new_part_code:
            print 'id：%s,part name 和code不一致,part name:%s' % (id,part_name)
            # has_show_list.append(part_name)
            ws.write(rownum, 10, new_part_code.decode('UTF-8'))
            continue
    else:
        ws.write(rownum, 10, new_part_code.decode('UTF-8'))
#
wb.save(newname)

