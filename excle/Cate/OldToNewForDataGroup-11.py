# encoding=utf-8
# 2015.11.28 数据团队Monkey 商品库、配件库、供应商库，数据订正
__author__ = 'zxg'

import sys

from util import CrawlDao, FileUtil, StringUtil

reload(sys)
sys.setdefaultencoding("utf-8")


class OldToNew:
    def __init__(self):
        self.dao = CrawlDao.CrawlDao("modeldatas")

        self.commodity_table = 'db_monkey_commodity_goods'
        self.part_table = 'db_monkey_part_goods_base'
        self.offer_table = 'db_monkey_offer_goods'

        self.save_sql_set = list()
        self.save_sql_set.append("select @now_time := now();")

        # id:object
        self.part_id_dict = dict()
        # name:list(object)
        self.part_name_dict = dict()

        part_sql = "select id,part_name,sum_code,first_cat_id,second_cat_id,third_cat_id,first_cat_name,second_cat_name,third_cat_name from db_category_part WHERE is_deleted = 'N' and vehicle_code in ('C','CH')"
        part_array = self.dao.db.get_data(part_sql)
        for part_data in part_array:
            part_id = part_data['id']
            part_name = part_data['part_name']

            self.part_id_dict[part_id] = part_data

            if part_name in self.part_name_dict:
                part_set = list(self.part_name_dict[part_name])
            else:
                part_set = list()
            part_set.append(part_data)
            self.part_name_dict[part_name] = part_set

    def commodity_process(self):
        select_sql = "select part_id,part_name,part_sum_code from db_monkey_commodity_goods where isdelete = 0 GROUP by part_id"
        commodity_array = self.dao.db.get_data(select_sql)
        for commodity_data in commodity_array:
            part_id = commodity_data['part_id']

            if part_id not in self.part_id_dict.keys():
                print '1-commodity=====commodity_process:it need to change id:%s' % part_id
                continue
            part_data = self.part_id_dict[part_id]
            part_name = part_data['part_name']
            sum_code = part_data['sum_code']

            update_sql = "update db_monkey_commodity_goods set part_name = '"+part_name+"',part_sum_code='"+sum_code+"',gmt_modified = @now_time where part_id = '"+str(part_id)+"';"
            self.save_sql_set.append(update_sql)

    def part_goods_process(self):

        select_sql = "select part_name,part_code,first_cate_id,second_cate_id,third_cate_id from db_monkey_part_goods_base  GROUP by part_name,part_code"
        part_goods_array = self.dao.db.get_data(select_sql)
        for part_goods_data in part_goods_array:
            part_name = part_goods_data['part_name']
            third_cate_id = part_goods_data['third_cate_id']
            part_code = str(part_goods_data['part_code'])

            search_part_name = part_name

            if search_part_name not in self.part_name_dict.keys():
                print '2-part_goods_process:it need to change part_name:%s,part_code:%s' % (part_name, part_code)
                continue
            part_list = list(self.part_name_dict[search_part_name])

            if len(part_list) > 1 or len(part_list) == 0:
                print '3-part_goods_process:part_name has more list:%s,%s' % (part_name, len(part_list))

            is_exist = False
            for part_data in part_list:
                this_part_data = part_data
                if third_cate_id == part_data['third_cat_id']:
                    is_exist = True

            if not is_exist:
                print '4-part_goods_process:it need to change part_name:%s ,third_cate_id:%s,part_code:%s' % (part_name, third_cate_id,part_code)

            sum_code = str(this_part_data['sum_code'])
            first_code = sum_code[0:1]
            second_code = sum_code[1:3]
            third_code = sum_code[3:6]
            update_sql = "update db_monkey_part_goods_base set "
            update_sql += "part_name='"+str(search_part_name)+"', "
            update_sql += "part_code='"+sum_code+"', "
            update_sql += "first_cate_id='"+str(this_part_data['first_cat_id'])+"', "
            update_sql += "first_cate_code='"+first_code+"', "
            update_sql += "second_cate_id='"+str(this_part_data['second_cat_id'])+"', "
            update_sql += "second_cate_code='"+second_code+"', "
            update_sql += "third_cate_id='"+str(this_part_data['third_cat_id'])+"', "
            update_sql += "third_cate_code='"+third_code+"', "
            update_sql += "gmt_modified = @now_time where part_name = '"+part_name+"' and part_code= '"+part_code+"';"

            self.save_sql_set.append(update_sql)

    def offer_process(self):
        # 根据名称替换
        select_sql = "select part_id,part_name,part_sum_code from db_monkey_offer_goods where isdelete = 0 GROUP by part_sum_code"
        offer_array = self.dao.db.get_data(select_sql)
        for offer_data in offer_array:
            part_id = offer_data['part_id']
            part_name = offer_data['part_name']

            search_part_name = part_name
            # 特殊处理的part——name
            if part_name == u'空气滤清器芯' :
                search_part_name = u'空气滤清器'

            if search_part_name not in self.part_name_dict.keys():
                print '5-offer_process:it need to change part_name:%s ,part_id:%s' % (part_name, part_id)
                continue

            part_list = list(self.part_name_dict[search_part_name])
            if len(part_list) > 1 or len(part_list) == 0:
                print '6-offer_process:part_name has more list:%s,%s' % (part_name, len(part_list))

            for part_data in part_list:
                this_part_data = part_data

            update_sql = "update db_monkey_offer_goods set "
            update_sql += "part_sum_code='"+str(this_part_data['sum_code'])+"', "
            update_sql += "part_id='"+str(this_part_data['id'])+"', "
            update_sql += "third_cate_id='"+str(this_part_data['third_cat_id'])+"', "
            update_sql += "third_cate_name='"+str(this_part_data['third_cat_name'])+"', "
            update_sql += "second_cate_id='"+str(this_part_data['second_cat_id'])+"', "
            update_sql += "second_cate_name='"+str(this_part_data['second_cat_name'])+"', "
            update_sql += "first_cate_id='"+str(this_part_data['first_cat_id'])+"', "
            update_sql += "first_cate_name='"+str(this_part_data['first_cat_name'])+"', "
            update_sql += "gmt_modified = @now_time where part_name = '"+part_name+"';"

            self.save_sql_set.append(update_sql)

    def write_sql(self, file_name):
        # read_file = open(file_name, "r")
        # content = read_file.read()
        # read_file.close()

        fo = open(file_name, "w+")
        print "Name of the file: ", fo.name

        # fo.seek(0, 2)
        fo.writelines('\n'.join(self.save_sql_set))
        fo.close()

    def main(self):
        file_name = r'/Users/zxg/Desktop/temp/cateTable/monkey-3goodsCate.txt'
        self.commodity_process()
        self.part_goods_process()
        self.offer_process()
        self.write_sql(file_name)


test = OldToNew()
test.main()
