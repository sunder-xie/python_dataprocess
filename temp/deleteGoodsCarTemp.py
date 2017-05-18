# encoding=utf-8
# 临时处理火花塞和滤清器的删除车型操作

__author__ = 'zxg'

import sys
import json

from util import CrawlDao,HttpUtil

reload(sys)
sys.setdefaultencoding("utf-8")


class delete:
    def __init__(self):
        self.dao = CrawlDao.CrawlDao()
        self.http = HttpUtil.HttpUtil()
    #
    def main(self):
        # Search url
        search_url = 'http://search.tqmall.com/elasticsearch/goods/convert?q=*&brandName=BRANDNAME&goodsFormat=FORMAT'

        sql_string = 'select goods_format,brand_name from db_monkey_commodity_goods  where isdelete = 0 and EXISTS'
        sql_string += '( select goods_uuId from db_monkey_commodity_goods_car where status = 1 and uuId = goods_uuId group by goods_uuId)'

        print sql_string
        result_array = self.dao.db.get_data(sql_string)
        if result_array:
            for result in result_array:

                format = result['goods_format']
                brand_name = result['brand_name']
                if format == 'F7HER2':
                    print 'this'
                final_search_url = search_url.replace('BRANDNAME', brand_name).replace('FORMAT', format)

                print 'final search: %s' % final_search_url
                try:
                    result = self.http.http_get(final_search_url)
                    json_result = json.loads(result)
                    response = json_result['response']
                    list = response['list']
                    oneRecord = list[0]

                    goodsId = oneRecord['id']
                    print 'goodsId is ====:%s' % goodsId
                except:
                    print 'wrong'


delete = delete()
delete.main()