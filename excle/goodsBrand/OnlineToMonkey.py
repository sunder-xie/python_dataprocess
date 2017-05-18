# encoding=utf-8
# goods线上的品牌导入monkey库中
__author__ = 'ximeng'

import sys

from util import CrawlDao

reload(sys)
sys.setdefaultencoding("utf-8")


class SqlToMonkey:
    def __init__(self):
        self.dao = CrawlDao.CrawlDao()

    # 保存对应关系
    def main(self):

        # 判断关系表中有无此数据
        sql_string = "select brand_name,site_url,first_letter,brand_desc from db_brand"
        print 'onlineBrand获得数据:%s' % sql_string
        result_array = self.dao.db.get_data(sql_string)
        if result_array:

            for result in result_array:
                monkey_brand_data = dict()

                brand_name = str(result['brand_name']).strip()
                if "/" in brand_name:
                    brand_array = brand_name.split("/")
                    brand_ch = brand_array[0]
                    brand_en = brand_array[1]
                else:
                    brand_ch = brand_name
                    brand_en = brand_name

                site_url = result['site_url']
                if "http://" == site_url or "unknown" == site_url:
                    site_url = ''

                country = 0
                if result['brand_desc'] == '世界知名品牌':
                    country = 1

                monkey_brand_data['first_letter'] = result['first_letter']
                monkey_brand_data['name_ch'] = brand_ch
                monkey_brand_data['name_en'] = brand_en
                monkey_brand_data['online_website'] = site_url
                monkey_brand_data['code'] = brand_name
                monkey_brand_data['country'] = country
                monkey_brand_data['isdelete'] = 0

                brand_exist_data = dict()
                brand_exist_data['name_ch'] = brand_ch
                # brand_exist_data['name_en'] = brand_en
                brand_exist_data['isdelete'] = 0

                self.dao.insert_or_update_without_exit("db_monkey_commodity_brand", monkey_brand_data, brand_exist_data)
        else:
            return


start = SqlToMonkey()
start.main()