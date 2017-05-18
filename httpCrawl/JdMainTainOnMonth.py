# encoding=utf-8
# 京东保养定时爬取脚本，每月一次
# 从scrapy中迁移出来，均为 http请求
import datetime
import uuid

__author__ = 'zxg'

import json

from util import CrawlDao, HttpUtil


class JdMaintain:

    def __init__(self):
        self.dao = None
        self.init_dao()

        self.http = HttpUtil.HttpUtil()

        self.brand_url = "http://auto.jd.com/queryBrands"
        self.series_url = "http://auto.jd.com/querySeries?brand=BRAND_VALUE"
        self.model_url = "http://auto.jd.com/queryModel?brand=BRAND_VALUE&series=SERIES_VALUE"
        # 保养url
        self.maintain_url = "http://auto.jd.com/maintain/getMaintain?carModelId=MODEL_ID&mileage=1"

        # ===========数据的保存===============
        self.max_save_num = 3000
        self.jd_car_data_list = list()
        self.jd_car_maintain_data_list = list()
        self.jd_car_maintain_relation_data_list = list()
        self.delete_jd_car_maintain_relation_id_list = list()


        # =============数据初始化===================
        # 京东车型
        self.car_dict = dict()
        car_array = self.dao.db.get_data("select car_uuid,jd_car_id from jd_car")
        for car_data in car_array:
            self.car_dict[str(car_data['jd_car_id'])] = str(car_data['car_uuid'])

        # 车型保养：id-name:unit
        # self.car_maintain_unit_dict = dict()
        # self.car_maintain_dict = dict()
        # car_maintain_array = self.dao.db.get_data(
        #     "select car_maintain_uuid,car_uuid,maintain_name,maintain_unit from jd_car_maintain")
        # for car_maintain_data in car_maintain_array:
        #     key = str(car_maintain_data['car_uuid']) + "-" + str(car_maintain_data['maintain_name'])
        #     self.car_maintain_unit_dict[key] = str(car_maintain_data['maintain_unit'])
        #     self.car_maintain_dict[key] = str(car_maintain_data['car_maintain_uuid'])

        # 车型每公里详情保养数据
        # car_maintain_id-mileage:id
        # self.maintain_relation_dict = dict()
        # maintain_array = self.dao.db.get_data("select id,car_maintain_uuid,mileage from jd_car_maintain_relation")
        # for maintain_data in maintain_array:
        #     key = str(maintain_data['car_maintain_uuid']) + "-" + str(maintain_data['mileage'])
        #     self.maintain_relation_dict[key] = str(maintain_data['id'])

    def init_dao(self):
        self.dao = CrawlDao.CrawlDao('dev_crawler', 'test')

    def parse(self):
        this_month = datetime.datetime.now().strftime("%Y-%m-%d")

        print "========= start JdMaintain============date:%s" % this_month
        brand_result = self.http.http_get(self.brand_url)
        brand_list = dict(json.loads(brand_result))['data']
        # 品牌
        for brand in brand_list:
            brand_value = str(dict(brand)['brandName'])
            if brand_value == '':
                continue
            series_url = self.series_url.replace("BRAND_VALUE", brand_value)
            series_result = self.http.http_get(series_url)
            try:
                series_list = dict(json.loads(series_result))['data']
            except:
                print "get series json to dict wrong,url:%s" % series_url
                continue
            # 车系
            for series in series_list:
                factory_value = str(series['factory'])
                series_value = str(series['seriesName'])
                model_url = self.model_url.replace("BRAND_VALUE", brand_value).replace("SERIES_VALUE", series_value)
                model_result = self.http.http_get(model_url)
                try:
                    model_list = dict(json.loads(model_result))['data']
                except:
                    print "get model json to dict wrong,url:%s" % model_url
                    continue

                # 车型
                for model in model_list:
                    model_id = str(model['carModelId'])
                    model_value = str(model['modelName'])

                    # 保存车型

                    car_uuid = self.save_jd_car(brand_value, factory_value, series_value, model_value, model_id)
                    # 进行保养项
                    self.maintain_parse(model_id, car_uuid)


        # 将list中的剩下数据保存至数据库
        self.final_save()

    # 保养数据的处理
    def maintain_parse(self, model_id, car_uuid):
        try:
            maintain_array = self.dao.db.get_data("select id,car_maintain_uuid,mileage from jd_car_maintain_relation where car_uuid='"+car_uuid+"'")
        except:
            self.init_dao()
            maintain_array = self.dao.db.get_data("select id,car_maintain_uuid,mileage from jd_car_maintain_relation where car_uuid='"+car_uuid+"'")
        maintain_relation_dict = dict()
        maintain_relation_list = list()
        for maintain_data in maintain_array:
            key = str(maintain_data['car_maintain_uuid']) + "-" + str(maintain_data['mileage'])
            maintain_relation_list.append(key)
            maintain_relation_dict[key] = str(maintain_data['id'])


        maintain_url = self.maintain_url.replace("MODEL_ID", model_id)
        range_result = self.http.http_get(maintain_url)

        try:
            range_final_result = dict(json.loads(range_result))['data']['maintainInfo']['columnCells']
        except:
            print "get maintain json to dict wrong,url:%s" % maintain_url
            return

        # index:保养名称id
        column_dict = dict()
        for column in range_final_result:
            cells_list = column['cells']
            column_name = column['columnName']
            if column['num'] == 0:
                # 保养项目列表

                cells_index = 0
                for cells_data in cells_list:
                    cells_index += 1
                    cells_array = str(cells_data).replace("(", "（").replace(")", "").replace("）", "").strip().split("（")
                    maintain_name = cells_array[0]
                    maintain_unit = ''
                    if len(cells_array) > 1:
                        maintain_unit = cells_array[1]

                    car_maintain_uuid = self.save_car_maintain(car_uuid, maintain_name, maintain_unit)
                    column_dict[cells_index] = car_maintain_uuid

            else:
                # 每个公里数的数据记录
                mileage = str(column_name)
                cells_index = 0
                for cells_res in cells_list:
                    cells_index += 1
                    car_maintain_uuid = column_dict[cells_index]

                    key = car_maintain_uuid + "-" + mileage
                    if key in maintain_relation_list:
                        if cells_res == u"false":
                            relation_id = maintain_relation_dict[key]
                            self.delete_car_relation(relation_id)
                    else:
                        if cells_res == u"true":
                            self.save_car_relation(car_uuid, car_maintain_uuid, mileage)



    # ==============save===================
    def final_save(self):
        if len(self.jd_car_maintain_relation_data_list) > 0:
            try:
                self.dao.insert_batch_temple('jd_car_maintain_relation', self.jd_car_maintain_relation_data_list)
            except:
                self.init_dao()
                self.dao.insert_batch_temple('jd_car_maintain_relation', self.jd_car_maintain_relation_data_list)
            finally:
                self.jd_car_maintain_relation_data_list = list()

        if len(self.delete_jd_car_maintain_relation_id_list) > 0:
            try:
                self.dao.update_in_batch_temple('jd_car_maintain_relation', {'the_type': 1},
                                                {'id': self.delete_jd_car_maintain_relation_id_list})
            except:
                self.init_dao()
                self.dao.update_in_batch_temple('jd_car_maintain_relation', {'the_type': 1},
                                                {'id': self.delete_jd_car_maintain_relation_id_list})
            finally:
                self.delete_jd_car_maintain_relation_id_list = list()

        if len(self.jd_car_maintain_data_list) > 0:
            try:
                self.dao.insert_batch_temple("jd_car_maintain", self.jd_car_maintain_data_list)
            except:
                self.init_dao()
                self.dao.insert_batch_temple("jd_car_maintain", self.jd_car_maintain_data_list)
            finally:
                self.jd_car_maintain_data_list = list()

        if len(self.jd_car_data_list) > 0:
            try:
                self.dao.insert_batch_temple("jd_car", self.jd_car_data_list)
            except:
                self.init_dao()
                self.dao.insert_batch_temple("jd_car", self.jd_car_data_list)
            finally:
                self.jd_car_data_list = list()

    def save_car_relation(self, car_uuid, car_maintain_uuid, mileage):
        save_data = {
            'car_uuid': car_uuid,
            'car_maintain_uuid': car_maintain_uuid,
            'mileage': mileage
        }
        self.jd_car_maintain_relation_data_list.append(save_data)

        if len(self.jd_car_maintain_relation_data_list) > self.max_save_num:

            try:
                self.dao.insert_batch_temple('jd_car_maintain_relation', self.jd_car_maintain_relation_data_list)
            except:
                self.init_dao()
                self.dao.insert_batch_temple('jd_car_maintain_relation', self.jd_car_maintain_relation_data_list)
            finally:
                self.jd_car_maintain_relation_data_list = list()

    def delete_car_relation(self, relation_id):
        self.delete_jd_car_maintain_relation_id_list.append(relation_id)
        if len(self.delete_jd_car_maintain_relation_id_list) > self.max_save_num:

            try:
                self.dao.update_in_batch_temple('jd_car_maintain_relation', {'the_type': 1},
                                                {'id': self.delete_jd_car_maintain_relation_id_list})
            except:
                self.init_dao()
                self.dao.update_in_batch_temple('jd_car_maintain_relation', {'the_type': 1},
                                                {'id': self.delete_jd_car_maintain_relation_id_list})
            finally:
                self.delete_jd_car_maintain_relation_id_list = list()

    def save_car_maintain(self, car_uuid, maintain_name, maintain_unit):
        try:
            car_maintain_array = self.dao.db.get_data(
                "select car_maintain_uuid,car_uuid,maintain_name,maintain_unit from jd_car_maintain where car_uuid='"+car_uuid+"' and maintain_name = '"+maintain_name+"'")
        except:
            self.init_dao()
            car_maintain_array = self.dao.db.get_data(
                "select car_maintain_uuid,car_uuid,maintain_name,maintain_unit from jd_car_maintain where car_uuid='"+car_uuid+"' and maintain_name = '"+maintain_name+"'")

        # 判断数据库中是否存在该数据
        if len(car_maintain_array) > 0:
            car_maintain_data = car_maintain_array[0]
            car_maintain_uuid = str(car_maintain_data['car_maintain_uuid'])
            mysql_unit = str(car_maintain_data['maintain_unit'])
            # 判断该数据的保养单位有无更改
            if mysql_unit != maintain_unit:
                try:
                    self.dao.update_temple("jd_car_maintain", {'maintain_unit': maintain_unit, "the_type": 1},
                                           {'car_maintain_uuid': car_maintain_uuid})
                except:
                    self.init_dao()
                    self.dao.update_temple("jd_car_maintain", {'maintain_unit': maintain_unit, "the_type": 1},
                                           {'car_maintain_uuid': car_maintain_uuid})

        else:
            car_maintain_uuid = str(uuid.uuid1())
            save_data = {
                'car_maintain_uuid': car_maintain_uuid,
                'car_uuid': car_uuid,
                'maintain_name': maintain_name,
                'maintain_unit': maintain_unit
            }

            self.jd_car_maintain_data_list.append(save_data)
            if len(self.jd_car_maintain_data_list) > self.max_save_num:
                try:
                    self.dao.insert_batch_temple("jd_car_maintain", self.jd_car_maintain_data_list)
                except:
                    self.init_dao()
                    self.dao.insert_batch_temple("jd_car_maintain", self.jd_car_maintain_data_list)
                finally:
                    self.jd_car_maintain_data_list = list()
                    return car_maintain_uuid
                
        return car_maintain_uuid

    def save_jd_car(self, brand, factory, series, model, jd_car_id):
        if jd_car_id in self.car_dict:
            car_uuid = self.car_dict[jd_car_id]
            return car_uuid

        car_uuid = str(uuid.uuid1())
        self.car_dict[jd_car_id] = car_uuid
        save_data = {
            'car_uuid': car_uuid,
            'jd_car_id': jd_car_id,
            'jd_brand_name': brand,
            'jd_factory_name': factory,
            'jd_series_name': series,
            'jd_model_name': model
        }
        self.jd_car_data_list.append(save_data)

        if len(self.jd_car_data_list) > self.max_save_num:
            try:
                self.dao.insert_batch_temple("jd_car", self.jd_car_data_list)
            except:
                self.init_dao()
                self.dao.insert_batch_temple("jd_car", self.jd_car_data_list)
            finally:
                self.jd_car_data_list = list()
                return car_uuid

        return car_uuid


jdMaintain = JdMaintain()
jdMaintain.parse()