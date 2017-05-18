# encoding=utf-8
__author__ = 'zxg'

from util import CrawlDao

print "=====start======"

dao = CrawlDao.CrawlDao('modeldatas', "online_cong")

# 基于厂商统计 商品数量
is_factory_stat = False
# 基于 车型统计 商品数量
is_model_stat = True

relation_sql = 'select car_brand_name,liyang_table from db_monkey_part_liyang_table_relation'
relation_array = dao.db.get_data(relation_sql)

for relation_data in relation_array:
    print "    "
    car_brand_name = str(relation_data['car_brand_name'])
    liyang_table = str(relation_data['liyang_table'])

    # id:liyang_data
    liyang_data_dict = dict()
    # liyang_factory,liyang_factory
    liyang_factory_dict = dict()
    liyang_base_sql = "select id,liyang_brand,liyang_factory,liyang_series,liyang_model from db_monkey_part_liyang_base where liyang_brand = '" + car_brand_name + "'"
    liyang_base_array = dao.db.get_data(liyang_base_sql)
    for liyang_base_data in liyang_base_array:
        liyang_factory = str(liyang_base_data['liyang_factory'])
        id = str(liyang_base_data['id'])

        if is_factory_stat:
            if liyang_factory in liyang_factory_dict.keys():
                id_list = list(liyang_factory_dict[liyang_factory])
            else:
                id_list = list()
            if id not in id_list:
                id_list.append(id)
                liyang_factory_dict[liyang_factory] = id_list

        if is_model_stat:
            liyang_data_dict[id] = liyang_base_data

    # 基于 factory
    if is_factory_stat:
        for liyang_factory, id_list in liyang_factory_dict.iteritems():
            if len(id_list) == 0:
                sum = 0
            else:
                goods_id_list = list()
                count_sql = "select distinct goods_id from " + liyang_table + " where part_liyang_id in (" + ",".join(
                    id_list) + ") group by goods_id"
                # print 'count_sql:%s' % count_sql
                count_array = dao.db.get_data(count_sql)
                sum = len(count_array)

            print '%s-%s sum is:%s' % (car_brand_name, liyang_factory, str(sum))

        print 'brand:%s,liyang_factory:%s,model_size:%s' % (car_brand_name, liyang_factory, str(len(id_list)))
        print "================="

    # 基于model
    if is_model_stat:
        for id, liyang_base_data in liyang_data_dict.iteritems():
            count_sql = "select distinct goods_id from " + liyang_table + " where part_liyang_id = '" + id + "'"
            count_array = dao.db.get_data(count_sql)
            count_sum = len(count_array)

            print '%s-%s-%s-%s, sum is:%s' % (
                str(liyang_base_data['liyang_brand']), str(liyang_base_data['liyang_factory']),
                str(liyang_base_data['liyang_series']), str(liyang_base_data['liyang_model']), str(count_sum))

print "=====end====="

