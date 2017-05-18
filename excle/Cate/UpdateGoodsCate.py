# encoding=utf-8
# 更新goods表中的分类
__author__ = 'ximeng'

import sys

from util import CrawlDao
reload(sys)
sys.setdefaultencoding("utf-8")

dao = CrawlDao.CrawlDao()

# 获得新老的对应关系
relation_sql_string = 'select my_cat_id,old_cat_id from db_category_relation'
resultArray = dao.db.get_data(relation_sql_string)

relation_table = {}
for relation_result in resultArray:
    relation_table[int(relation_result['old_cat_id'])] = int(relation_result['my_cat_id'])

# 获得goods表总数
sum_sql_string = '  select count(goods_id) as sum from db_goods'
result = dao.db.get_data(sum_sql_string)

sum = result[0]['sum']
pageSize = 1000
pageNum = sum/pageSize + 1
print pageNum


final_id = 0
# 按pageSize遍历数据库数据
for i in range(1, pageNum+1):
    select_sql_string = 'select goods_id,cat_id from db_goods where goods_id > '+str(final_id)+'  limit 0,'+str(pageSize)
    print 'select_sql:%s' % select_sql_string
    resultArray = dao.db.get_data(select_sql_string)
    # 对每条数据进行处理
    for result in resultArray:
        goods_id = result['goods_id']
        cat_id = result['cat_id']
        print 'cat_id: %s' % cat_id
        if relation_table.has_key(cat_id):
            new_cat_id = relation_table.get(cat_id)
            # 执行更新
            update_sql_string = 'update db_goods set cat_id ='+str(new_cat_id)+' where goods_id = '+str(goods_id)
            print 'goods_id-%s is  to new cate' % goods_id
            print 'update_sql_string:%s' % update_sql_string

            # dao.db.update_data(update_sql_string)
        else:
            print 'goods_id-%s is not to new cate' % goods_id
            continue
    try:
        final_id = resultArray[pageSize-1]['goods_id']
    except Exception as e:
        print e.message
        print 'the end~~~~'

print 'the end~~~~'
