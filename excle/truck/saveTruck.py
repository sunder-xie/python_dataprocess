# encoding=utf-8
# 保存整理的商用车数据
# 2015-12-14

__author__ = 'zxg'

from util import FileUtil, CrawlDao


class saveTruckFromGuo12:
    def __init__(self):
        self.fileDao = FileUtil.FileDao
        self.dao = CrawlDao.CrawlDao("modeldatas")

        self.category_dict = dict()

    def main(self, excel_file):
        excel = self.fileDao.open_excel(excel_file)
        sheet = excel.sheet_by_index(0)

        row_sum = sheet.nrows
        col_sum = sheet.ncols


        # 获得属性
        attr_name_dict = dict()
        first_row = sheet.row_values(0)
        for this_col in range(16, col_sum):
            attr_name = first_row[this_col].strip()
            attr_id = self.attr_save(attr_name)

            attr_data = {
                'attr_name': attr_name,
                'attr_id': attr_id
            }
            attr_name_dict[this_col] = attr_data

            print attr_name

        for this_row in range(1, row_sum):
            row = sheet.row_values(this_row)

            car_sum_code = str(row[0]).strip().replace(".0", "")
            batch_number = row[1].strip()
            car_model_type = row[2].strip()

            car_brand_name = row[3].strip()
            car_brand_code = str(row[4]).strip().replace(".0", "")
            brand_id = self.category_save(car_brand_name, car_brand_code, 0, 1)

            car_factory_name = row[5].strip()
            car_factory_code = str(row[6]).strip().replace(".0", "")
            factory_id = self.category_save(car_factory_name, car_factory_code, brand_id, 2)

            car_series_name = row[7].strip()
            car_series_code = str(row[8]).strip().replace(".0", "")
            series_id = self.category_save(car_series_name, car_series_code, factory_id, 3)

            car_model_name = row[9].strip()
            car_model_code = str(row[10]).strip().replace(".0", "")
            model_id = self.category_save(car_model_name, car_model_code, series_id, 4)

            car_name = row[11].strip()
            car_code = str(row[12]).strip().replace(".0", "")
            # factory_name = row[13].strip()
            # flue_name = row[14].strip()
            # remark = row[15].strip()
            flue_name = ''
            remark = ''

            car_data = {
                'batch_number': batch_number,
                'car_code': car_code,
                'car_name': car_name,
                'car_sum_code': car_sum_code,
                'car_type_name': car_model_type,
                'car_category_id': model_id,
                'flue_name': flue_name,
                'car_remarks': remark
            }
            car_id = self.dao.insert_without_exit("db_truck_car", car_data, {"car_sum_code": car_sum_code})

            # 属性
            # for this_col in range(16, col_sum):
            #     attr_value = row[this_col].strip()
            #     attr_data = dict(attr_name_dict[this_col])
            #
            #     attr_val_data = {
            #         'car_id': car_id,
            #         'attr_key_id': attr_data['attr_id'],
            #         'attr_key_name': attr_data['attr_name'],
            #         'attr_value': attr_value
            #     }
            #
            #     self.dao.insert_without_exit("db_truck_attr_value",attr_val_data,attr_val_data)

    '''===============save==========================='''
    # save attr key
    def attr_save(self, attr_name):
        attr_data = {'key_name': attr_name}
        return self.dao.insert_without_exit("db_truck_attr_key", attr_data, attr_data)

    # save_cate
    def category_save(self, truck_name, truck_code, pid, truck_level):
        key = str(truck_name) + str(truck_code) + str(pid) + str(truck_level)
        if key in self.category_dict.keys():
            cate_id = self.category_dict[key]
        else:

            category_data = {
                'truck_name': truck_name,
                'truck_code': truck_code,
                'pid': pid,
                'truck_level': truck_level,
            }

            cate_id = self.dao.insert_without_exit("db_truck_category", category_data, category_data)
            self.category_dict[key] = cate_id

        return cate_id

excel_file = r'/Users/zxg/Documents/work/PythonExcle/truck/商用车型许国文.xlsx'
# excel_file = r'/Users/zxg/Documents/work/PythonExcle/truck/test.xlsx'
test = saveTruckFromGuo12()
test.main(excel_file)
