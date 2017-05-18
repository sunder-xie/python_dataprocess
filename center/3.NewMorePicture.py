# encoding=utf-8
# 处理时，同个车型出现多个相同图号，不同图的情况
import json
import os
from util import CrawlDao, FileUtil, StringUtil

__author__ = 'zxg'


class MorePicture:
    def __init__(self):
        self.dao = CrawlDao.CrawlDao("athena_center", "local")
        self.fileDao = FileUtil.FileDao()
        self.stringUtil = StringUtil.StringUtil()

        self.insert_pic_data_list = list()
        self.update_goods_car_data_list = list()
        # mac pic
        self.max_pic_id = 0
        # {{pic_num,pic_index}:[oe,oe...]}
        self.pic_dict = dict()

    # 根据liyangid获得modelid
    def Get_Modelid_By_liyang(self, liyang_id):
        model_sql = "select model_id from db_car_all where l_id = '" + str(liyang_id) + "' limit 1"
        model_array = self.dao.db.get_data(model_sql)
        if len(model_array) > 0:
            return str(model_array[0]['model_id'])
        else:
            return ""

    # 获得 excel中的初始数据
    def Read_From_Excel(self, excel_address):
        # 已出现的图号{pic_data,more_index}
        has_show_pic_dict = dict()

        # 单个excle处理
        data = self.fileDao.open_excel(excel_address)
        sheets_array = data.sheets()
        # 获得一个liyangid 找到modelid
        liyang_id = str((sheets_array[1].row_values(1))[1]).replace(".0", '').strip()
        model_id = self.Get_Modelid_By_liyang(liyang_id)
        if model_id == "":
            print "Get_Modelid_By_liyang wrong,liyang:%s " % liyang_id
            return ""

        # 第一个goods sheet
        table = sheets_array[0]

        n_rows = table.nrows  # 行数
        n_cols = table.ncols  # 列数
        print ('行数：%s ,列数：%s' % (n_rows, n_cols))
        for rownum in range(1, n_rows):
            row = table.row_values(rownum)
            more_index = str(row[3]).strip()
            if more_index == "":
                continue
            pic_data = {
                "pic_num": str(row[1]).strip().replace(".0", ''),
                "pic_index": str(row[2]).strip().replace(".0", '')
            }
            pic_key = json.dumps(pic_data)
            if pic_key not in has_show_pic_dict.keys():
                has_show_pic_dict[pic_key] = more_index
                continue
            only_index = has_show_pic_dict[pic_key]
            if more_index == only_index:
                # 相同的index，无需新增
                continue
            # 序号出现过，保存oe，原厂图号和图的唯一性
            oe_num = self.stringUtil.get_true_oe(str(row[4]))
            if pic_key in self.pic_dict.keys():
                oe_list = self.pic_dict[pic_key]
            else:
                oe_list = list()
            if oe_num not in oe_list:
                oe_list.append(oe_num)
                self.pic_dict[pic_key] = oe_list

        return model_id

    def get_max_pic(self):
        self.max_pic_id = int(
            self.dao.db.get_data("select max(id) as 'max_id' from center_goods_car_picture")[0]['max_id'])

    def get_goods_ids(self, oe_list):
        if len(oe_list) == 0:
            return []
        result_list = list()
        goods_sql = "select id from center_goods where oe_number in ('" + "','".join(oe_list) + "')"
        print goods_sql
        goods_array = self.dao.db.get_data(goods_sql)
        for goods_data in goods_array:
            result_list.append(int(goods_data['id']))
        return result_list

    def do_the(self, model_id):
        for pic_key, oe_list in self.pic_dict.items():
            self.max_pic_id += 1
            the_id = self.max_pic_id
            pic_data = json.loads(pic_key)
            pic_data["id"] = the_id

            goods_id_list = self.get_goods_ids(oe_list)
            if len(goods_id_list) > 0:
                self.insert_pic_data_list.append(pic_data)
                self.update_goods_car_data_list.append(
                    {"pic_id": the_id, "model_id": model_id, "goods_id_list": goods_id_list})

    def write_to_sql(self, file_address):
        start_string = "SET unique_checks=0;SET foreign_key_checks=0;set autocommit=0;\n"
        final_string = "commit;\n"
        time_string = "select @now_time := now();\n"

        insert_table_name = "center_goods_car_picture"
        update_table_name = "center_goods_car_relation"

        #
        file_object = open(file_address, 'a')
        file_object.writelines(start_string)
        file_object.writelines(time_string)

        # insert
        help_list = list()
        try:
            # insert
            for the_data in self.insert_pic_data_list:
                the_data['gmt_modified'] = '@now_time'
                the_data['gmt_create'] = '@now_time'

                help_list.append(the_data)
            if len(help_list) > 0:
                file_object.writelines(self.dao.get_batch_sql(insert_table_name, help_list))
                file_object.writelines(";\n")
                help_list = list()

            # update
            file_object.writelines("\n\n # update\n\n ")
            # update
            for the_data in self.update_goods_car_data_list:
                update_sql = "update " + update_table_name + " set pic_id='" + the_data[
                    'pic_id'] + "',gmt_modified=@now_time where model_id = '" + the_data[
                    'model_id'] + "' and goods_id in (" + ",".join(the_data['goods_id_list']) + ")"
                file_object.writelines(update_sql)
                file_object.writelines(";\n")

            file_object.writelines(final_string)
        except Exception, e:
            print e
        finally:
            file_object.close()

    def start(self, excel_address, write_address):
        model_id = self.Read_From_Excel(excel_address)
        if model_id == "":
            return False
        if len(self.pic_dict.keys()) == 0:
            print 'not need to write sql,because no same {pic_num,pic_index}'
            return False
        self.get_max_pic()
        self.do_the(model_id)
        self.write_to_sql(write_address)


excel_address = r'/Users/zxg/Desktop/qijun.xlsx'
write_address = os.getcwd() + "/center/more_by_sql.sql"
morePic = MorePicture()
morePic.start(excel_address, write_address)
