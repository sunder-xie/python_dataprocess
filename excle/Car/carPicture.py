# encoding=utf-8
# 爱卡汽车的车型跟我们的车型匹配
__author__ = 'ximeng'

import json
import sys
import re

from util import CrawlDao, HttpUtil
reload(sys)
sys.setdefaultencoding("utf-8")

class CarPicture():

    def __init__(self):
        self.dao = CrawlDao.CrawlDao()
        self.http = HttpUtil.HttpUtil()
        self.brand_dict = dict()
        test_header_url = 'http://app.360cec.com'
        online_header_url = 'http://10.162.51.140'

        self.header_url = test_header_url
        try:
            url = self.header_url+'/car/info?pid=0'
            result = self.http.http_get(url)
            json_result = json.loads(result)
            alist = json_result['data'][0]['list']
            for brand_dic in alist:
                brand_name = str(brand_dic['name']).replace("-", "")
                brand_id = str(brand_dic['id'])
                self.brand_dict[brand_name] = brand_id
            # 存车系的name和id
            self.series_dict = dict()
            for brand_id in self.brand_dict.itervalues():
                series_result = self.http.http_get(self.header_url+'/car/info?pid='+brand_id)
                json_result = json.loads(series_result)
                company_array = json_result['data']
                company_dict = dict()
                for company in company_array:
                    company_name = company['tagName']
                    series_dic = dict()
                    for series in company['list']:
                        series_name = series['carName']
                        series_id = str(series['id'])
                        series_dic[series_name] = series_id
                    company_dict[company_name] = series_dic
                self.series_dict[brand_id] = company_dict
        except Exception as e:
            print "==================get error ================%e" % e.message

    # 处理series里面的对应内容，保存到数据库中
    def process_series(self, series_dic, search_name, series_id, series_name, series_company, series_img_url):
        for dian_series_name in series_dic.keys():
            dian_series_name = str(dian_series_name)
            if dian_series_name.find(search_name) > -1:
                # 匹配成功
                car_crawl_online_data = dict()
                car_crawl_online_data['crawl_car_id'] = series_id
                car_crawl_online_data['online_car_id'] = series_dic[dian_series_name]
                car_crawl_online_data['online_car_name'] = dian_series_name
                car_crawl_online_data['crawl_car_name'] = series_name
                car_crawl_online_data['crawl_car_company'] = series_company
                car_crawl_online_data['img_url'] = series_img_url

                car_exit_crawl_online_data = dict()
                car_exit_crawl_online_data['crawl_car_id'] = series_id
                car_exit_crawl_online_data['online_car_id'] = series_dic[dian_series_name]
                self.dao.insert_without_exit('dw_car_crawl_online', car_crawl_online_data, car_exit_crawl_online_data)

    # 处理 company，匹配我们对应的数据
    def process_company(self, crawl_car_id, crawl_car_name, company_name, is_one=True):
        select_series_string = "select id,name, company,img_url from from dw_crawl_car_brand "
        select_series_string += "where source=4 and parentId = "+crawl_car_id + " and company = " + company_name
        series_result_array = self.dao.db.get_data(select_series_string)
        for series_result_data in series_result_array:
            series_id = str(series_result_data['id'])
            series_name = str(series_result_data['name'])
            series_company = series_result_data['company']
            series_img_url = series_result_data['img_url']
            # 将主要检索的name做处理，若有英文+数字，则取英文加数字，若无，则取中文去品牌名且去空格里面的内容
            # 1.判断是否有英文+数字
            search_name = re.findall(r"\w+", series_name)
            if len(search_name) == 0:
                # 2.去品牌名
                search_name = series_name.replace(crawl_car_name, "")
                # 3.去()
                index = search_name.replace("（", "(").find("(")
                if index > -1:
                    search_name = search_name[:index]
            # ======================开始对应关系=====================
            # 根据品牌名对应到电商品牌id
            search_brand_name = crawl_car_name
            for brand_name in dict(self.brand_dict).keys():
                if crawl_car_name == search_brand_name:
                    break
                if crawl_car_name.find(brand_name) > -1 or brand_name.find(crawl_car_name) > -1:
                    search_brand_name = brand_name
                    break
            brand_id = self.brand_dict[search_brand_name]
            # 根据id找到下属的company
            company_dict = dict(self.series_dict[brand_id])
            # 因为是一个，所以全系匹配
            if is_one:
                for company_key in company_dict.keys():
                    series_dic = dict(company_dict[company_key])
                    self.process_series(series_dic, search_name, series_id, series_name, series_company, series_img_url)
            # 多个车系，需处理后匹配
            else:
                # 爱卡的厂家去品牌处理
                company_name = company_name.replace(crawl_car_name, "")
                # 判断爱卡汽车中有无进口两字，有，则对应官网 xx汽车，无则选择包含关系的公司厂家
                find_value = ''
                if company_name.find("进口") > -1:
                    find_value = "汽车"
                else:
                    find_value = company_name
                for company_key in company_dict.keys():
                    if str(company_key).find(find_value) > -1:
                        series_dic = dict(company_dict[company_key])
                        self.process_series(series_dic, search_name, series_id, series_name, series_company, series_img_url)
                        break

    # 主入口
    def main(self):
        # 读取爱卡汽车的品牌数据
        select_brand_string = "select id , name from from dw_crawl_car_brand where source=4 and type = 'brand'"
        brand_result_array = self.dao.db.get_data(select_brand_string)
        for brand_result_data in brand_result_array:
            crawl_car_id = str(brand_result_data['id'])
            crawl_car_name = str(brand_result_data['name']).replace("·", "")
            # 读取爱卡汽车下面的厂家company
            select_company_string = "select company from from dw_crawl_car_brand where source=4 and parentId = "+ crawl_car_id
            company_result_array = self.dao.db.get_data(select_company_string)
            # 若只有一个company，则全系匹配
            if len(company_result_array) == 1:
                company_name = str(company_result_array['company'])
                self.process_company(crawl_car_id, crawl_car_name, company_name)
            # 若有多个company，区分进出口
            else:
                for company_result_data in company_result_array:
                    company_name = str(company_result_data['company'])
                    self.process_company(crawl_car_id, crawl_car_name, company_name, False)


carPicture = CarPicture()
carPicture.main()