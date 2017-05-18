# encoding=utf-8
# 替换excle中 错误的标准零件名称和编码，删除部分－－无零件名称数据
import sys

__author__ = 'zxg'

reload(sys)
sys.setdefaultencoding("utf-8")

from xlrd import open_workbook
from xlutils.copy import copy
from util import HttpUtil, CrawlDao, FileUtil, StringUtil


class SameData:
    def __init__(self):
        self.dao = CrawlDao.CrawlDao("test", "local")
        self.fileDao = FileUtil.FileDao()

        # {{excel_oe:{part_name:"",part_code:"",remarks:""}}
        self.true_excel_dict = dict()

    def get_excle_name(self, excle_file):
        excle = excle_file.decode('utf-8')
        excleArray = excle.split('\\')
        excle_name_array = excleArray[len(excleArray) - 1].split('/')
        excle_name = excle_name_array[len(excle_name_array) - 1]
        return excle_name

    def first_row_process(self, first_row, ncols):
        index_sql_table = {}
        for cols_num in range(0, ncols):
            cols_name = first_row[cols_num].replace(".0", "").strip().upper()
            if u'序号' == cols_name:
                index_sql_table['indexs'] = cols_num
            elif u'OE' in cols_name:
                index_sql_table['oe'] = cols_num
            elif u'标准零件名称' in cols_name:
                index_sql_table['part_name'] = cols_num
            elif u'标准零件编码' in cols_name or u'标准零件ID' in cols_name:
                index_sql_table['part_code'] = cols_num

            elif u'图号' in cols_name:
                index_sql_table['pic_num'] = cols_num
            elif u'原厂序号' in cols_name or u'图序号' in cols_name:
                index_sql_table['pic_index'] = cols_num
            elif u'备注' in cols_name:
                index_sql_table['remarks'] = cols_num
            elif u'用量' in cols_name:
                index_sql_table['amount'] = cols_num
        return index_sql_table

    def find_all_excle_same(self, files_address):
        file_list = []
        file_list = self.fileDao.get_file_list(files_address, file_list)

        for excle in file_list:
            if '.DS_Store' in excle or '~$' in excle:
                continue

            excle_name = self.get_excle_name(excle)
            print excle_name


            # 单个excle处理
            data = self.fileDao.open_excel(excle)
            table = data.sheets()[0]
            nrows = table.nrows  # 行数
            ncols = table.ncols  # 列数

            # 第一行的列名
            first_row = table.row_values(0)
            index_sql_table = self.first_row_process(first_row, ncols)

            # 已有的oe＋图号＋图序号＋part＋remarks
            only_list = list()
            only_dict = dict()
            is_save_list = list()

            # 遍历行的数据存入
            for rownum in range(1, nrows):
                row = table.row_values(rownum)

                excle_indexs = str(row[index_sql_table['indexs']]).replace(".0", "").strip()
                excle_oe = str(row[index_sql_table['oe']]).replace(".0", "").strip()
                excle_oe_trim = excle_oe.replace(" ", "").replace("／", "/").replace(
                    "（", "(").replace("）", ")").replace("—",
                                                        "-").replace(
                    "“",
                    "\"").replace(
                    "”", "\"").replace("\"", "'").replace("，", ",").replace("-", "")

                excle_pic_num = str(row[index_sql_table['pic_num']]).replace(".0", "").strip()
                excle_pic_index = str(row[index_sql_table['pic_index']]).replace(".0", "").strip()
                excle_part_name = str(row[index_sql_table['part_name']]).replace(".0", "").strip()
                excle_part_code = str(row[index_sql_table['part_code']]).replace(".0", "").strip()
                excle_amount = str(row[index_sql_table['amount']]).replace(".0", "").strip()
                excle_remarks = str(row[index_sql_table['remarks']]).replace(".0", "").strip()

                save_dict = {'indexs': excle_indexs, "oe": excle_oe, "oe_trim": excle_oe_trim,
                             "pic_num": excle_pic_num, "pic_index": excle_pic_index, "part_name": excle_part_name,
                             "part_code": excle_part_code, "application_amout": excle_amount, "remarks": excle_remarks,
                             "source": excle_name}
                key_value = excle_oe_trim + "-" + excle_pic_num + "-" + excle_pic_index + "-" + excle_remarks
                if key_value in only_list:
                    if key_value not in is_save_list:
                        self.dao.insert_temple("same_data", only_dict[key_value])
                        is_save_list.append(key_value)

                    indexs = index_sql_table['indexs']
                    print "rownum:%s,indexs:%s the same key_value :%s" % (rownum, indexs, key_value)
                    self.dao.insert_temple("same_data", save_dict)
                else:
                    only_list.append(key_value)
                    only_dict[key_value] = save_dict

    def main(self):
        files_address = r'/Users/zxg/Documents/fromFtp/now_all'
        # 重复的数据进行删除
        self.find_all_excle_same(files_address)


sameData = SameData()
sameData.main()
