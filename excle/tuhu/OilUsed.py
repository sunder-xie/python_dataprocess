# encoding=utf-8
# 途虎的车型对上线上车型，并匹配上淘汽车型
# 2016/09/29
import os

__author__ = 'zxg'

import sys

from util import CrawlDao,FileUtil

reload(sys)
sys.setdefaultencoding("utf-8")


class OilToOnline:
    def __init__(self):
        self.dao = CrawlDao.CrawlDao("test", "local")

        self.fileDao = FileUtil.FileDao()

        # car_brand+"_"+company:{data}
        self.tuhu_car_dict = dict()
        # tuhu_car_id:oil_used
        self.tuhu_oil_dict = dict()

        self.initTuhuCar()
        self.initTuhuOil()


        self.tuhu_car_dict_keys = self.tuhu_car_dict.keys()
        self.tuhu_oil_dict_keys = self.tuhu_oil_dict.keys()


        ## 缓存
        self.online_car_liyang_cache = dict()

    def initTuhuCar(self):
        tuhu_sql = "select id,car_brand,company,car_series,car_model,car_power,car_year from od_th_car"
        tuhu_car_array = self.dao.db.get_data(tuhu_sql)

        for tuhu_car_data in tuhu_car_array:
            car_brand = str(tuhu_car_data['car_brand'])
            company = str(tuhu_car_data['company'])

            key = car_brand+"_"+company
            if key in self.tuhu_car_dict.keys():
                tuhu_car_list = list(self.tuhu_car_dict[key])
            else:
                tuhu_car_list = list()
            tuhu_car_list.append(tuhu_car_data)
            self.tuhu_car_dict[key] = tuhu_car_list

    def initTuhuOil(self):
        tuhu_oil_sql = "select outer_id,oil_dosage,outer_table from oil_dosage where outer_table = 'th_car' "
        tuhu_oil_array = self.dao.db.get_data(tuhu_oil_sql)

        for tuhu_oil_data in tuhu_oil_array:
            outer_id = str(tuhu_oil_data['outer_id'])
            oil_dosage = str(tuhu_oil_data['oil_dosage']).replace("L","")
            self.tuhu_oil_dict[outer_id] = oil_dosage


    '''
    1. 获得对应 liyang数据
    2. 途虎过滤，生产年份
    3. online_car:List<筛选后的途虎>
    4. online_car:List<机油用量>
    '''
    def getLiyangList(self,online_car_id):
        if online_car_id in self.online_car_liyang_cache.keys():
            return self.online_car_liyang_cache[online_car_id]

        liyang_sql = "select dca.new_l_id as l_id,dcia.create_year as create_year from db_car_all dca,db_car_info_all dcia where dca.car_models_id = "+str(online_car_id)+" and dca.new_l_id = dcia.leyel_id"
        liyang_array = self.dao.db.get_data(liyang_sql)
        self.online_car_liyang_cache[online_car_id] = liyang_array
        return liyang_array

    def getTuhuList(self,tuhu_car_brand,tuhu_car_company,tuhu_car_model,power,liyang_list):
        result_list = list()

        search_car_key = tuhu_car_brand+"_"+tuhu_car_company
        if search_car_key in self.tuhu_car_dict_keys:
            tuhu_car_list = self.tuhu_car_dict[search_car_key]
            for tuhu_car_data in tuhu_car_list:
                #  id,car_brand,company,car_series,car_model,car_power,car_year
                id = str(tuhu_car_data['id'])
                car_model = str(tuhu_car_data['car_model'])
                car_power = str(tuhu_car_data['car_power'])
                car_year = str(tuhu_car_data['car_year'])

                if tuhu_car_model == car_model and power in car_power:
                    # 判断liyang 里面是否有符合的生产年款
                    for liyang_data in liyang_list:
                        if car_year in str(liyang_data['create_year']):
                            # 符合数据
                            result_list.append(id)
                            break

        return result_list

    def getOil(self,tuhu_id_list):
        oil_set = set()
        for tuhu_id in tuhu_id_list:
            if tuhu_id in self.tuhu_oil_dict_keys:
                oil = self.tuhu_oil_dict[tuhu_id]
                oil_set.add(oil)
        return oil_set

    def save_data(self,online_car_id,oil_set,od_the_car_id_list,is_not_have = 'N'):
        save_data = {
            'online_car_id':online_car_id,
            'oil':",".join(oil_set),
            'od_the_car_ids':",".join(od_the_car_id_list),
            'is_not_have':is_not_have
        }
        self.dao.insert_temple("tuhu_oil_result",save_data)

    def readExcelOnlineCar(self,file_address):
         # 单个excle处理
        data = self.fileDao.open_excel(file_address)
        #
        table = data.sheets()[0]

        n_rows = table.nrows  # 行数
        n_cols = table.ncols  # 列数
        print ('行数：%s ,列数：%s' % (n_rows, n_cols))

        for rownum in range(1, n_rows):
            row = table.row_values(rownum)
            online_car_id = str(row[0]).strip().replace(".0","")
            tuhu_car_brand = str(row[2]).strip()
            tuhu_car_company = str(row[4]).strip()
            tuhu_car_model = str(row[8]).strip()
            power = str(row[9]).strip()
            if online_car_id == "72137":
                print 'hhh'
            if "Y" == tuhu_car_model.upper() or tuhu_car_model == "":
                print '%s 此条为Y，不处理' % online_car_id
                self.save_data(online_car_id,set(),list(),'Y')
                continue
            # 0. 获得力扬列表
            liyang_list = self.getLiyangList(online_car_id)
            if len(liyang_list) == 0:
                print '%s 此条的online_car_id , 无对应的力扬数据' % online_car_id
                self.save_data(online_car_id,set(),list(),"N")
                continue
            # 1. List<途虎id>过滤，生产年份
            tuhu_car_list = self.getTuhuList(tuhu_car_brand,tuhu_car_company,tuhu_car_model,power,liyang_list)
            # 4. online_car:Set<机油用量>
            oil_set = self.getOil(tuhu_car_list)

            # 保存结果
            self.save_data(online_car_id,oil_set,tuhu_car_list,"N")

# file_address = r'/Users/zxg/Desktop/途虎车型机油处理/中西处理-待.xlsx'
file_address = r'/Users/zxg/Desktop/途虎车型机油处理/最后结果.xlsx'
oilToOnline = OilToOnline()
oilToOnline.readExcelOnlineCar(file_address)