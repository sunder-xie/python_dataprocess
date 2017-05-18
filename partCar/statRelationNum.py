# encoding=utf-8
# 2016-08-16 统计总的配件数和新增配件数
__author__ = 'zxg'

from util import CrawlDao

dao = CrawlDao.CrawlDao("modeldatas", "online_cong")
# dao = CrawlDao.CrawlDao("modeldatas", "local")

# all relation table
all_table_name_list = list()
all_table_sql = "select liyang_table from db_monkey_part_liyang_table_relation"
print all_table_sql
all_table_array = dao.db.get_data(all_table_sql)
for all_table_data in all_table_array:
    all_table_name_list.append(str(all_table_data['liyang_table']))

# FOR
all_num = 0
month_num = 0
for_month = '2016-08-'

for table_name in all_table_name_list:
    sum_sql = "select count(1) as the_sum from " + table_name
    print sum_sql
    sum_array = dao.db.get_data(sum_sql)
    the_sum = int(sum_array[0]['the_sum'])
    all_num += the_sum

    print "%s:%s" % (table_name, str(the_sum))

    month_sql = "select count(1) as the_sum from " + table_name + " where gmt_create like '" + for_month + "%'"
    print month_sql
    month_array = dao.db.get_data(month_sql)
    month_sum = int(month_array[0]['the_sum'])
    month_num += month_sum

    print "【%s】----%s:%s" % (for_month, table_name, str(month_sum))


print '='*10

print '总共的关系数：%s , %s 月份新增的数：%s' % (str(all_num),for_month,str(month_num))

print '='*10
