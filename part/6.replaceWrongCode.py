# encoding=utf-8
# 替换excle中 错误的标准零件名称和编码，删除部分－－无零件名称数据
import sys

__author__ = 'zxg'

reload(sys)
sys.setdefaultencoding("utf-8")

from xlrd import open_workbook
from xlutils.copy import copy
from util import HttpUtil, CrawlDao, FileUtil, StringUtil


class RepairWrongData:
    def __init__(self):
        self.dao = CrawlDao.CrawlDao("modeldatas", "local")
        self.fileDao = FileUtil.FileDao()

        # {{excel_oe:{part_name:"",part_code:"",remarks:""}}
        self.true_excel_dict = dict()

    # 初始化正确的零件名称数据
    def get_true_part(self):
        excle = r'/Users/zxg/Documents/work/淘气档口/work/2016.06 monkey－part/相同oe不同标准零件名称（完成）.xls'
        # 单个excle处理
        data = self.fileDao.open_excel(excle)
        table = data.sheets()[0]
        nrows = table.nrows  # 行数
        ncols = table.ncols  # 列数

        print 'true part nrows:%s ncols:%s' % (nrows, ncols)

        for rownum in range(1, nrows):
            row = table.row_values(rownum)

            excel_num = str(row[1]).replace(".0", "").strip()
            oe = str(row[3]).replace(".0", "").strip().replace(" ", "")
            source_name = str(row[8]).replace(".0", "").strip().replace(" ", "")
            part_name = str(row[9]).replace(".0", "").strip()
            part_code = str(row[10]).replace(".0", "").strip()
            remarks = str(row[11]).replace(".0", "").strip()

            if oe not in self.true_excel_dict.keys():
                self.true_excel_dict[oe] = {"part_name": part_name, "part_code": part_code, "remarks": remarks}

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
        return index_sql_table

    def replace_all_excle(self, files_address):
        file_list = []
        file_list = self.fileDao.get_file_list(files_address, file_list)

        for excle in file_list:
            if '.DS_Store' in excle or '~$' in excle:
                continue

            excle_name = str(self.get_excle_name(excle)).replace(" ", "").replace("（", "(").replace("）", ")")
            print excle_name

            # 预更改excle 数据
            rb = open_workbook(excle)
            wb = copy(rb)
            # 通过get_sheet()获取的sheet有write()方法
            ws = wb.get_sheet(0)

            # 单个excle处理
            data = self.fileDao.open_excel(excle)
            table = data.sheets()[0]
            nrows = table.nrows  # 行数
            ncols = table.ncols  # 列数


            # 第一行的列名
            first_row = table.row_values(0)
            index_sql_table = self.first_row_process(first_row, ncols)

            # 遍历行的数据存入
            for rownum in range(1, nrows):
                row = table.row_values(rownum)

                excle_oe = str(row[index_sql_table['oe']]).replace(".0", "").replace(" ", "").replace("／", "/").replace(
                    "（", "(").replace("）", ")").replace("—",
                                                        "-").replace(
                    "“",
                    "\"").replace(
                    "”", "\"").replace("\"", "'").replace("，", ",").replace("-", "")
                if excle_oe not in self.true_excel_dict.keys():
                    continue

                indexs = index_sql_table['indexs']
                print "1.rownum:%s,indexs:%s oe :%s" %(rownum,indexs,excle_oe)
                # {"part_name": part_name, "part_code": part_code, "remarks": remarks}
                replace_dict = self.true_excel_dict[excle_oe]

                ws.write(rownum, index_sql_table['part_name'],
                         replace_dict['part_name'].replace(".0", "").decode('UTF-8'))
                ws.write(rownum, index_sql_table['part_code'],
                         replace_dict['part_code'].replace(".0", "").decode('UTF-8'))

                new_remarks = replace_dict['remarks']
                if new_remarks != "":
                    old_remarks = str(row[index_sql_table['remarks']]).replace(".0", "").strip()
                    final_remarks = new_remarks
                    if old_remarks != "":
                        final_remarks = old_remarks + "," + new_remarks
                    ws.write(rownum, index_sql_table['remarks'], final_remarks.decode('UTF-8'))

            # 存入
            wb.save(excle.decode('UTF-8'))

    def delete_all_excle_same(self, files_address):
        file_list = []
        file_list = self.fileDao.get_file_list(files_address, file_list)

        for excle in file_list:
            if '.DS_Store' in excle or '~$' in excle:
                continue

            excle_name = self.get_excle_name(excle)
            print excle_name
            # 预更改excle 数据
            rb = open_workbook(excle)
            wb = copy(rb)
            # 通过get_sheet()获取的sheet有write()方法
            ws = wb.get_sheet(0)

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

            # 遍历行的数据存入
            for rownum in range(1, nrows):
                row = table.row_values(rownum)
                excle_oe = str(row[index_sql_table['oe']]).replace(".0", "").strip().replace(" ", "").replace("／", "/").replace(
                    "（", "(").replace("）", ")").replace("—",
                                                        "-").replace(
                    "“",
                    "\"").replace(
                    "”", "\"").replace("\"", "'").replace("，", ",").replace("-", "")

                excle_pic_num = str(row[index_sql_table['pic_num']]).replace(".0", "").strip()
                excle_pic_index = str(row[index_sql_table['pic_index']]).replace(".0", "").strip()
                excle_remarks = str(row[index_sql_table['remarks']]).replace(".0", "").strip()

                key_value = excle_oe + "-" + excle_pic_num + "-" + excle_pic_index + "-" + excle_remarks
                if key_value in only_list:
                    indexs = index_sql_table['indexs']
                    print "rownum:%s,indexs:%s the same key_value :%s" %(rownum,indexs,key_value)
                    ws.write(rownum, indexs, "")
                else:
                    only_list.append(key_value)
            # 存入
            wb.save(excle.decode('UTF-8'))

    def main(self):
        files_address = r'/Users/zxg/Documents/fromFtp/now_all'
        # files_address = r'/Users/zxg/Documents/fromFtp/test'
        # get ture part
        self.get_true_part()
        # 遍历所有的excle 进行数据替换
        self.replace_all_excle(files_address)
        # 重复的数据进行删除
        self.delete_all_excle_same(files_address)


repairWrongData = RepairWrongData()
repairWrongData.main()
