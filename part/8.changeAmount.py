# encoding=utf-8
# 替换excle中 错误的标准零件名称和编码，删除部分－－无零件名称数据
import sys

__author__ = 'zxg'

reload(sys)
sys.setdefaultencoding("utf-8")

from xlrd import open_workbook
from xlutils.copy import copy
from util import HttpUtil, CrawlDao, FileUtil, StringUtil


class ChangeAmount:
    def __init__(self):
        self.dao = CrawlDao.CrawlDao("modeldatas", "local")
        self.fileDao = FileUtil.FileDao()

        # {{excle_name:{excel_num:{part_name:"",part_code:"",amount:""}}
        self.true_excel_dict = dict()

    # 初始化正确的零件名称数据
    def get_true_part(self):
        excle = r'/Users/zxg/Documents/fromFtp/newamount.xls'
        # 单个excle处理
        data = self.fileDao.open_excel(excle)
        table = data.sheets()[0]
        nrows = table.nrows  # 行数
        ncols = table.ncols  # 列数

        print 'true part nrows:%s ncols:%s' % (nrows, ncols)

        for rownum in range(1, nrows):
            row = table.row_values(rownum)

            excel_num = str(row[0]).replace(".0", "").strip()

            source_name = str(row[9]).replace(".0", "").strip().replace(" ", "")
            amount = str(row[10]).replace(".0", "").strip()
            part_name = str(row[11]).replace(".0", "").strip()
            part_code = str(row[12]).replace(".0", "").strip()

            if source_name in self.true_excel_dict.keys():
                excel_dict = dict(self.true_excel_dict[source_name])
            else:
                excel_dict = dict()
            excel_dict[excel_num] = {"part_name":part_name,"part_code":part_code,"amount":amount}

            self.true_excel_dict[source_name] = excel_dict


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

    def replace_all_excle(self, files_address):
        file_list = []
        file_list = self.fileDao.get_file_list(files_address, file_list)

        for excle in file_list:
            if '.DS_Store' in excle or '~$' in excle:
                continue

            excle_name = str(self.get_excle_name(excle)).replace(" ", "").replace("（", "(").replace("）", ")")
            print excle_name

            if excle_name not in self.true_excel_dict.keys():
                continue

            excel_dict = dict(self.true_excel_dict[excle_name])

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

                indexs_num = str(row[index_sql_table['indexs']]).replace(".0", "").strip()

                if indexs_num not in excel_dict.keys() or indexs_num == "":
                    continue
                new_data = excel_dict[indexs_num]
                new_amount = new_data['amount']
                new_part_name = new_data['part_name']
                new_part_code = new_data['part_code']

                print "1.rownum:%s,indexs:%s new_amount :%s" %(rownum,indexs_num,new_amount)

                if new_amount != "":
                    ws.write(rownum, index_sql_table['amount'],
                         new_amount.decode('UTF-8'))
                if new_part_name != "":
                    ws.write(rownum, index_sql_table['part_name'],
                         new_part_name.decode('UTF-8'))
                if new_part_code != "":
                    ws.write(rownum, index_sql_table['part_code'],
                         new_part_code.decode('UTF-8'))


            # 存入
            wb.save(excle.decode('UTF-8'))


    def main(self):
        files_address = r'/Users/zxg/Documents/fromFtp/now_all'
        # files_address = r'/Users/zxg/Documents/fromFtp/test'
        # get ture part
        self.get_true_part()
        # 遍历所有的excle 进行数据替换
        self.replace_all_excle(files_address)


repairWrongData = ChangeAmount()
repairWrongData.main()
