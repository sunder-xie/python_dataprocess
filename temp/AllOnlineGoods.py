# encoding=utf-8
#  所有的淘气在售商品数据
# 商品品牌、商品ID、商品编码、一级分类、二级分类、商品名称、规格型号、包装规格、是否在售、售卖单位


__author__ = 'zxg'

import sys

from util import CrawlDao

reload(sys)
sys.setdefaultencoding("utf-8")

class getOnline:
    def __init__(self):
        self.dao = CrawlDao.CrawlDao()

        # 品牌
        self.brand_dict = self.online_brand()

        # 线上分类
        self.cat_dict = dict()
        self.cat_parent_dict = dict()
        cat_select_sql = 'select cat_id,cat_name,parent_id from db_category'
        cat_result_array = self.dao.db.get_data(cat_select_sql)
        for cat_result in cat_result_array:
            cat_id = cat_result['cat_id']
            self.cat_dict[cat_id] = cat_result['cat_name']
            self.cat_parent_dict[cat_id] = cat_result['parent_id']

    # 线上品牌
    def online_brand(self):
        brand_dict = dict()
        brand_select_sql = 'select brand_id,brand_name from db_brand'
        brand_result_array = self.dao.db.get_data(brand_select_sql)
        for brand_result in brand_result_array:
            brand_dict[brand_result['brand_id']] = brand_result['brand_name']
        return brand_dict

    def main(self):
        # 商品品牌、商品ID、商品编码、一级分类、二级分类、商品名称、规格型号、包装规格、是否在售、售卖单位
        goods_select_sql = 'select goods_id,new_goods_sn,brand_id,cat_id,goods_name,goods_format,package_format from db_goods where is_delete = 0 and seller_id = 1'

        goods_result_array = self.dao.db.get_data(goods_select_sql)
        if goods_result_array:
            for goods_result_data in goods_result_array:

                temp_data = dict()

                goods_id = goods_result_data['goods_id']
                # if int(goods_id) <= 305620:
                #     continue
                new_goods_sn = goods_result_data['new_goods_sn']
                brand_id = goods_result_data['brand_id']
                cat_id = goods_result_data['cat_id']
                goods_name = goods_result_data['goods_name']
                goods_format = goods_result_data['goods_format']
                package_format = goods_result_data['package_format']

                # brand
                if int(brand_id) == 0:
                    brand_name = ''
                else:
                    brand_name = self.brand_dict[brand_id]
                # cat
                second_cat_name = self.cat_dict[cat_id]
                cat_parent_id = self.cat_parent_dict[cat_id]
                if cat_parent_id == 0:
                    first_cat_name = second_cat_name
                    second_cat_name = ''
                else:
                    first_cat_name = self.cat_dict[cat_parent_id]

                # 是否在售和售卖单位
                seller_nick = ''
                on_sale = ''

                warehouse_select_sql = "select seller_id,seller_nick,is_on_sale from db_goods_warehouse where goods_id = '" + str(goods_id) + "' and seller_id = 1"
                warehouse_array = self.dao.db.get_data(warehouse_select_sql)
                if warehouse_array:
                    on_sale = '不在售'
                    seller_nick = ''
                    for warehouse_result in warehouse_array:

                        this_seller_nick = str(warehouse_array[0]['seller_nick'])
                        if this_seller_nick not in seller_nick:
                            seller_nick += ' '+this_seller_nick
                        if int(warehouse_result['is_on_sale']) == 1:
                            on_sale = '在售'

                # 在stock中寻找在售的库存，若为0，则改为不在售
                if on_sale == '在售':
                    stock_sql = "select goods_number from db_goods_stock where goods_id = '" + str(goods_id) + "' and is_deleted = 'N' and seller_id = 1"
                    stock_array = self.dao.db.get_data(stock_sql)
                    if stock_array:
                        number = 0
                        for stock_result in stock_array:
                            number += int(stock_result['goods_number'])

                        if str(number) == '0':
                            on_sale = '不在售'

                temp_data['brand_name'] = brand_name
                temp_data['goods_id'] = goods_id
                temp_data['new_goods_sn'] = new_goods_sn
                temp_data['first_cat_name'] = first_cat_name
                temp_data['second_cat_name'] = second_cat_name
                temp_data['goods_name'] = goods_name
                temp_data['goods_format'] = goods_format
                temp_data['package_format'] = package_format
                temp_data['on_sale'] = on_sale
                temp_data['seller_nick'] = seller_nick.strip()

                self.dao.insert_temple('temp', temp_data)


