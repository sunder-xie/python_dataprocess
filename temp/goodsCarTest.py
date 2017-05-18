# encoding=utf-8
# 临时处理goodsCar中的

__author__ = 'zxg'

import sys

from util import CrawlDao

reload(sys)
sys.setdefaultencoding("utf-8")


class SqlChangeGoodsCar:
    def __init__(self):
        self.dao = CrawlDao.CrawlDao()
        self.car_dict = dict()
        self.car_pid_dict = dict()

    def main(self):
        select_sql = 'select goods_id,car_model from db_goods_car '
        print 'select 获得数据:%s' % select_sql
        result_array = self.dao.db.get_data(select_sql)

        if result_array:
            insert_list = list()
            max_num = 5000
            table_name = 'db_goods_car_copy'
            index = 0
            for result in result_array:
                goods_id = result['goods_id']
                car_id = result['car_model']

                # 根据车型id获得其父等一系列对象
                get_pid_sql = 'select name from db_car_category where id = '+str(car_id)
                special = self.dao.db.get_data(get_pid_sql)
                name = special[0]['name']

                goods_car_data = self.getExt(car_id)
                goods_car_data['goods_id'] = goods_id
                goods_car_data['car_id'] = car_id
                goods_car_data['car_name'] = name
                goods_car_data['level'] = 6

                insert_list.append(goods_car_data)

                if len(insert_list) == max_num:
                    self.dao.insert_batch_temple(table_name, insert_list)
                    insert_list = []
                    index = index + 1
                    print index

            if len(insert_list) != 0:
                print 'final insert Batch'
                self.dao.insert_batch_temple(table_name, insert_list)


    # 获得最小car的父的所有数据
    def getExt(self, car_id):

        goods_car_data = dict()
        # 第五级
        year_data = self.get_parent(car_id)
        year_id = year_data['id']
        goods_car_data['car_year_id'] = year_id
        goods_car_data['car_year'] = year_data['name']
        # 第4级
        power_data = self.get_parent(year_id)
        power_id = power_data['id']
        goods_car_data['car_power_id'] = power_id
        goods_car_data['car_power'] = power_data['name']
        # 第3级
        model_data = self.get_parent(power_id)
        model_id = model_data['id']
        goods_car_data['car_model_id'] = model_id
        goods_car_data['car_model'] = model_data['name']
        # 第2级
        series_data = self.get_parent(model_id)
        series_id = series_data['id']
        goods_car_data['car_series_id'] = series_id
        goods_car_data['car_series'] = series_data['name']
        # 第1级
        brand_data = self.get_parent(series_id)
        brand_id = brand_data['id']
        goods_car_data['car_brand_id'] = brand_id
        goods_car_data['car_brand'] = brand_data['name']

        return goods_car_data

    # 获得父id的一切属性
    def get_parent(self, car_id):

        if car_id in self.car_pid_dict.keys():
            pid = self.car_pid_dict[car_id]
        else:
            get_pid_sql = 'select pid from db_car_category where id = '+str(car_id)
            result = self.dao.db.get_data(get_pid_sql)
            pid = result[0]['pid']
            self.car_pid_dict[car_id] = pid

        if pid in self.car_dict.keys():
            final_result = self.car_dict.get(pid)
        else:
            car_select_sql = 'select id,name from db_car_category where id = '+str(pid)

            final_result = self.dao.db.get_data(car_select_sql)[0]
            self.car_dict[pid] = final_result

        return final_result


SqlChangeGoodsCar = SqlChangeGoodsCar()
SqlChangeGoodsCar.main()