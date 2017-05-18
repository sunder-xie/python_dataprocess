# encoding=utf-8
# 查询出所有excel中，相同的oe 不同的 标准零件名称
__author__ = 'zxg'
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

from openpyxl import Workbook
from openpyxl.writer.excel import ExcelWriter
from util import CrawlDao, FileUtil


class DifCode:
    def __init__(self):
        self.fileDao = FileUtil.FileDao()
        self.dao = CrawlDao.CrawlDao("test", "local")

    def main(self, files_address):
        fileList = []
        file_list = self.fileDao.get_file_list(files_address, fileList)

        # 已经出现的oe码的dict
        have_oe_dict = dict()
        # 该oe的第一条记录是否打印过
        is_oe_first_print = list()

        for excle in file_list:
            if '.DS_Store' in excle or '~$' in excle:
                continue
            excle = excle.decode('utf-8')
            excleArray = excle.split('\\')
            excle_name_array = excleArray[len(excleArray) - 1].split('/')
            excle_name = excle_name_array[len(excle_name_array) - 1]
            print excle_name

            # 单个excle处理
            data = self.fileDao.open_excel(excle)
            table = data.sheets()[0]
            nrows = table.nrows  # 行数
            ncols = table.ncols  # 列数

            print "nrows:%s" % nrows
            index_sql_table = {}
            # 第一行的列名
            first_row = table.row_values(0)
            for cols_num in range(0, ncols):
                cols_name = first_row[cols_num].strip().upper()
                if u'序号' == cols_name:
                    index_sql_table[cols_num] = 'indexs'
                elif u'OE' in cols_name:
                    index_sql_table[cols_num] = 'oe'
                elif u'标准零件名称' in cols_name:
                    index_sql_table[cols_num] = 'part_name'
                elif u'标准零件编码' in cols_name or u'标准零件ID' in cols_name:
                    index_sql_table[cols_num] = 'part_code'

                elif u'图号' in cols_name:
                    index_sql_table[cols_num] = 'pic_num'
                elif u'原厂序号' in cols_name or u'图序号' in cols_name:
                    index_sql_table[cols_num] = 'pic_index'

            # 遍历行的数据存入
            for rownum in range(1, nrows):
                row = table.row_values(rownum)
                save_dict = dict()
                oe = None
                for cols_num in range(0, ncols):
                    if cols_num not in index_sql_table.keys():
                        continue
                    key = index_sql_table[cols_num]
                    value = row[cols_num]
                    value = str(value).strip().replace("\"", "\'").replace(".0", "").upper()
                    save_dict[key] = value
                    save_dict["source"] = excle_name
                    if key == 'oe':
                        oe = value.replace(" ", "").replace("／", "/").replace("（", "(").replace("）", ")").replace("—",
                                                                                                                  "-").replace(
                            "“",
                            "\"").replace(
                            "”", "\"").replace("\"", "'").replace("，", ",").replace("-", "")

                if oe is None:
                    continue

                if oe in have_oe_dict.keys():
                    the_dict = have_oe_dict[oe]
                    if the_dict['part_code'] == save_dict['part_code']:
                        continue
                    # 出现过
                    if oe not in is_oe_first_print:
                        is_oe_first_print.append(oe)
                        start_row = self.save_dict_record(the_dict, oe)

                    start_row = self.save_dict_record(save_dict , oe)

                else:
                    have_oe_dict[oe] = save_dict

    def save_dict_record(self, the_dict, oe):
        the_dict['oe_trim'] = oe

        self.dao.insert_temple("dif", the_dict)


file_address = r'/Users/zxg/Documents/fromFtp/now_all'
difCode = DifCode()
difCode.main(file_address)
