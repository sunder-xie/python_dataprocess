# encoding=utf-8
# fix center_goods_car_picture 对于goods_car的车型 不是1:1,不同车型的epc_pic不同的，因此要1:1
# 2016.07.22
import os

__author__ = 'zxg'

from util import CrawlDao


class FixPic:
    def __init__(self):
        self.dao = CrawlDao.CrawlDao("athena_center", "local")
        self.insert_pic_data_list = list()
        self.update_goods_car_data_list = list()
        self.max_pic_id = 21466

    # 取得已有的pic的数据
    def get_pic(self):
        pic_dict = dict()
        pic_sql = "select id,epc_pic_num,epc_index from center_goods_car_picture"
        pic_array = self.dao.db.get_data(pic_sql)
        for pic_data in pic_array:
            pic_dict[str(pic_data['id'])] = {
                'epc_pic_num': str(pic_data['epc_pic_num']),
                'epc_index': str(pic_data['epc_index'])
            }

        return pic_dict

    # 根据goods_car 获得要新增的图片数据和要更新的数据
    def goods_car_main(self, pic_dict):
        has_show_list = list()

        goods_car_sql = "select model_id,pic_id from center_goods_car_relation GROUP BY model_id,pic_id"
        goods_car_array = self.dao.db.get_data(goods_car_sql)
        for goods_car_data in goods_car_array:
            model_id = str(goods_car_data['model_id'])
            pic_id = str(goods_car_data['pic_id'])

            if pic_id not in has_show_list:
                has_show_list.append(pic_id)
                continue
            new_pic_id = str(self.max_pic_id)
            has_show_list.append(new_pic_id)
            self.max_pic_id += 1

            pic_dict[new_pic_id] = pic_dict[pic_id]
            new_pic_data = pic_dict[pic_id]

            new_pic_data["id"] = new_pic_id

            self.insert_pic_data_list.append(new_pic_data)
            self.update_goods_car_data_list.append({"model_id": model_id, "pic_id": new_pic_id, "old_pic_id": pic_id})

    def write_to_sql(self, file_address):
        max_num = 3000
        start_string = "SET unique_checks=0;SET foreign_key_checks=0;set autocommit=0;\n"
        final_string = "commit;\n"
        time_string = "select @now_time := now();\n"

        insert_table_name = "center_goods_car_picture"
        update_table_name = "center_goods_car_relation"

        #
        insert_object = open(file_address, 'a')
        insert_object.writelines(start_string)
        insert_object.writelines(time_string)

        help_list = list()
        try:
            # insert
            for the_data in self.insert_pic_data_list:
                the_data['gmt_modified'] = '@now_time'
                the_data['gmt_create'] = '@now_time'

                help_list.append(the_data)
                if len(help_list) > max_num:
                    insert_object.writelines(self.dao.get_batch_sql(insert_table_name, help_list))
                    insert_object.writelines(";\n")
                    help_list = list()
            if len(help_list) > 0:
                insert_object.writelines(self.dao.get_batch_sql(insert_table_name, help_list))
                insert_object.writelines(";\n")
                help_list = list()

            insert_object.writelines("\n\n # update\n\n ")
            # update 
            for the_data in self.update_goods_car_data_list:
                update_sql = "update " + update_table_name + " set pic_id='" + the_data[
                    'pic_id'] + "',gmt_modified=@now_time where model_id = '" + the_data[
                    'model_id'] + "' and pic_id ='"+the_data['old_pic_id']+"'"
                insert_object.writelines(update_sql)
                insert_object.writelines(";\n")

            insert_object.writelines(final_string)
        except Exception, e:
            print e
        finally:
            insert_object.close()

    def main(self, file_address):
        pic_dict = self.get_pic()
        self.goods_car_main(pic_dict)
        self.write_to_sql(file_address)


first_name = os.getcwd() + "/center/fix_sql.sql"
fix = FixPic()
fix.main(first_name)
