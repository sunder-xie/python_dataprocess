# encoding=utf-8
# goods_car表 新的sql to 老的sql

__author__ = 'zxg'

import sys

reload(sys)
sys.setdefaultencoding("utf-8")




# new_db_goods_car sql 转化为 老的 db_goods_car sql


class change:
    def __init__(self, *name, **kwargs):
        self.new_add_object = open('/Users/zxg/Desktop/goods_car/new_insertGoodsCar.txt')

        self.old_add_file_name = r'/Users/zxg/Desktop/goods_car/old_insert_goods_car.txt'

    def change_add_sql(self):

        all_list_of_all_the_lines = list()
        data_list = set()

        first_sql = "select @now_time := now();"
        insert_sql = "insert into db_goods_car (goods_id,car_model,level,car_brand_id,car_brand,car_series_id,car_series,car_power_id,car_power,car_year_id,car_year,status,time_created,time_updated) value "
        insert_value = "(goods_id,car_model,level,0,'',0,'',0,'',0,'',0,@now_time,@now_time)"
        try:
            all_list_of_all_the_lines = self.new_add_object.readlines()
        finally:
            self.new_add_object.close()

        for all_line in all_list_of_all_the_lines:
            if 'select' in all_line or 'insert' in all_line:
                continue

            if '),' in all_line:
                one_record = all_line.replace("(", "").replace("),", "").strip('\n')
            else:
                # 最后一行数据
                one_record = all_line.split(")")[0].replace("(", "")

            record_array = one_record.split(",")

            goods_id = record_array[0]
            car_final_id = record_array[1]
            car_brand_id = record_array[4]
            car_series_id = record_array[6]
            car_model_id = record_array[8]
            car_power_id = record_array[10]
            car_year_id = record_array[12]

            data_list.add(
                insert_value.replace("goods_id", goods_id).replace("car_model", car_brand_id).replace("level", '1'))
            data_list.add(
                insert_value.replace("goods_id", goods_id).replace("car_model", car_series_id).replace("level", '2'))
            data_list.add(
                insert_value.replace("goods_id", goods_id).replace("car_model", car_model_id).replace("level", '3'))
            data_list.add(
                insert_value.replace("goods_id", goods_id).replace("car_model", car_power_id).replace("level", '4'))
            data_list.add(
                insert_value.replace("goods_id", goods_id).replace("car_model", car_year_id).replace("level", '5'))
            data_list.add(
                insert_value.replace("goods_id", goods_id).replace("car_model", car_final_id).replace("level", '6'))

        # 合并为sql
        max_size = 5000
        index = 0
        sum = 0
        final_list = list()
        final_list.append(first_sql)
        final_list.append(insert_sql)

        final_size = len(data_list)
        for data_value in data_list:
            index += 1
            sum += 1
            if index >= max_size:
                final_list.append(data_value + ";")
                final_list.append(insert_sql)
                index = 0
                continue
            elif sum < final_size:
                final_list.append(data_value + ",")
                continue
            else:
                final_list.append(data_value + ";")

        # 写入
        file_object = open(self.old_add_file_name, 'w')
        try:
            file_object.writelines("\n".join(final_list))
        finally:
            file_object.close()


change = change()
change.change_add_sql()
