# encoding=utf-8
# 添加新的分类和标准零件名称
import sys

__author__ = 'zxg'

reload(sys)
sys.setdefaultencoding("utf-8")

from util import HttpUtil, CrawlDao, FileUtil, StringUtil

dao = CrawlDao.CrawlDao("modeldatas", "local")
fileDao = FileUtil.FileDao()

cat_code_dict = dict()
cat_id_dict = dict()
# parent_id: max_code
cat_max_code = dict()
cat_array = dao.db.get_data("SELECT cat_id,cat_name,cat_code,cat_level,parent_id "
                            "FROM db_category WHERE is_deleted = 'N'")
for cat_data in cat_array:
    cat_code = str(cat_data['cat_code'])
    cat_level = str(cat_data['cat_level'])
    parent_id = str(cat_data['parent_id'])
    key = parent_id + str(cat_data['cat_name'])
    cat_code_dict[key] = cat_code
    cat_id_dict[key] = str(cat_data['cat_id'])

    if parent_id not in cat_max_code.keys():
        cat_max_code[parent_id] = 0

    if int(cat_code) > cat_max_code[parent_id]:
        cat_max_code[parent_id] = int(cat_code)

part_max_code = dict()
part_list = list()
part_sum_code_list = list()
part_array = dao.db.get_data("SELECT part_name,part_code,third_cat_id,sum_code "
                             "FROM db_category_part WHERE is_deleted = 'N'")
for part_data in part_array:
    part_code = str(part_data['part_code'])
    third_cat_id = str(part_data['third_cat_id'])
    sum_code = str(part_data['sum_code'])
    key = str(part_data['part_name']) + third_cat_id
    part_list.append(key)
    part_sum_code_list.append(sum_code)

    if third_cat_id not in part_max_code.keys():
        part_max_code[third_cat_id] = 0
    if int(part_code) > part_max_code[third_cat_id]:
        part_max_code[third_cat_id] = int(part_code)

data = fileDao.open_excel(r'/Users/zxg/Documents/work/淘气档口/work/2016.06 monkey－part/标准分类V3.xls')
#
table = data.sheets()[0]

n_rows = table.nrows  # 行数
n_cols = table.ncols  # 列数
print ('行数：%s ,列数：%s' % (n_rows, n_cols))
in_num = 0
not_in_num = 0

all_new_part_set = set()

for row_num in range(1, n_rows):
    row = table.row_values(row_num)

    first_name = str(row[2])
    second_name = str(row[3])
    third_name = str(row[4])
    part_name = str(row[5]).replace("（", "(").replace("）", ")")

    first_key = "0" + first_name
    first_code = cat_code_dict[first_key]
    first_id = cat_id_dict[first_key]

    second_key = first_id + second_name
    if second_key not in cat_code_dict.keys():
        save_data = {'cat_name': second_name, 'parent_id': first_id, 'cat_level': '2', 'vehicle_code': 'C'}

        the_code = cat_max_code[first_id] + 1
        cat_max_code[first_id] = the_code
        the_code = str(the_code)
        while len(the_code) != 2:
            the_code = "0" + the_code

        save_data['cat_code'] = the_code
        dao.insert_temple("db_category", save_data)
        cat_code_dict[second_key] = the_code
        continue
    second_code = cat_code_dict[second_key]
    second_id = cat_id_dict[second_key]

    third_key = second_id + third_name
    if third_key not in cat_code_dict.keys():
        save_data = {'cat_name': third_name, 'parent_id': second_id, 'cat_level': '3', 'vehicle_code': 'C'}

        if second_id not in cat_max_code.keys():
            cat_max_code[second_id] = 0
        the_code = cat_max_code[second_id] + 1
        cat_max_code[second_id] = the_code
        the_code = str(the_code)
        while len(the_code) != 3:
            the_code = "0" + the_code

        save_data['cat_code'] = the_code
        dao.insert_temple("db_category", save_data)
        cat_code_dict[third_key] = the_code
        continue
    third_code = cat_code_dict[third_key]
    third_id = cat_id_dict[third_key]

    part_key = part_name + third_id
    if part_key not in part_list:
        if third_id not in part_max_code.keys():
            all_new_part_set.add(third_id)
        if third_id in all_new_part_set:
            if '(左)' in part_name or '(上)' in part_name:
                the_code = '01'
            elif '(右)' in part_name or '(下)' in part_name:
                the_code = '02'
            elif '(中)' in part_name:
                the_code = '03'
            else:
                the_code = '00'
        else:
            test_sum_code = first_code + second_code + third_code + "00"
            if '(左)' not in part_name and '(上)' not in part_name and '(右)' not in part_name and '(下)' not in part_name and '(中)' not in part_name and part_name == third_name and test_sum_code not in part_sum_code_list:
                the_code = "00"
                part_sum_code_list.append(test_sum_code)
            else:
                the_code = part_max_code[third_id] + 1
                part_max_code[third_id] = the_code
                the_code = str(the_code)
                while len(the_code) != 2:
                    the_code = "0" + the_code
        # 新增
        save_data = {'part_name': part_name, 'part_code': the_code, 'first_cat_id': first_id,
                     'first_cat_name': first_name, 'second_cat_id': second_id, 'second_cat_name': second_name,
                     'third_cat_id': third_id, 'third_cat_name': third_name,
                     'sum_code': first_code + second_code + third_code + the_code, 'cat_kind': '1', 'vehicle_code': 'C'}
        dao.insert_temple("db_category_part", save_data)
        part_list.append(key)
