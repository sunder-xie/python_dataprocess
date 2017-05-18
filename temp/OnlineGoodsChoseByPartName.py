# encoding=utf-8
# 根据分类名称获得其已更新的数据
# zxg 2015-10-10


__author__ = 'zxg'

import sys

reload(sys)
sys.setdefaultencoding("utf-8")
from util import CrawlDao

part_name = ''

dao = CrawlDao.CrawlDao()

# 获得monkey项目的数据
# select_monkey_sql = "'select brand_name,goods_format from db_monkey_commodity_goods where isdelete = 0 and part_name= '" + part_name + "'"
select_monkey_sql = "select id,brand_name,goods_format from db_monkey_commodity_goods where isdelete = 0 "
monkey_result_array = dao.db.get_data(select_monkey_sql)
if len(monkey_result_array) == 0:
    print 'not have this goods'
    pass

# 获得存在的所有goodsCar的数据:状态：0-新建 1-生成sql 2-失败，电商库无上线goodsId
goods_status_dict = dict()
select_goods_car_select = "select goods_id,status from has_goods_car"
goods_car_result_array = dao.db.get_data(select_goods_car_select)
for goods_car_result in goods_car_result_array:
    goods_status_dict[goods_car_result['goods_id']] = int(goods_car_result['status'])

# brand对应的实际名称
brand_dict = dict()
for monkey_result in monkey_result_array:
    monkey_brand_name = monkey_result['brand_name']
    monkey_goods_format = monkey_result['goods_format']
    monkey_goods_id = monkey_result['id']

    # 判断是否更新进电商库--默认存在在commodity均更新进去
    if monkey_brand_name in brand_dict.keys():
        brand_name = brand_dict[monkey_brand_name]
        select_temp_sql = "select id,brand_name,goods_format from temp where  brand_name = '" + brand_name + "' and goods_format='" + monkey_goods_format + "'"
    else:
        select_temp_sql = "select id,brand_name,goods_format from temp where brand_name like '" + monkey_brand_name + "%' and goods_format='" + monkey_goods_format + "'"
    print 'select_temp_sql:%s' % select_temp_sql

    temp_result_array = dao.db.get_data(select_temp_sql)
    if temp_result_array:
        for temp_result in temp_result_array:
            temp_id = temp_result['id']
            temp_brand_name = temp_result['brand_name']
            temp_goods_format = temp_result['goods_format']

            brand_dict[monkey_brand_name] = temp_brand_name

            temp_status = '已更新'
            temp_is_car = '无车型数据'
            if monkey_goods_id in goods_status_dict.keys():
                status = goods_status_dict[monkey_goods_id]
                if status == 1:
                    temp_is_car = '已导入'
                if status == 2:
                    temp_is_car = '非线上，未导入'

            temp_data = {
                'status': temp_status,
                'is_car': temp_is_car
            }

            dao.update_temple('temp', temp_data, {'id': temp_id})
    else:
        print 'no this select_temp_sql'
print 'end'
