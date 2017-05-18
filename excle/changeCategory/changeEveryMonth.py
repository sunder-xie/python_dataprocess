# encoding=utf-8
# 2016/08/01
# 每月动态新增和修改的标准零件名称
__author__ = 'zxg'

from util import CrawlDao,FileUtil

class ChangePart:
    def __init__(self):
        self.athena_dao = CrawlDao.CrawlDao("athena", "local")
        self.monkey_dao = CrawlDao.CrawlDao('modeldatas', "local")
        self.fileDao = FileUtil.FileDao()

        self.insert_part_data_list = list()
        self.updata_part_data_list = list()
        self.monkey_updata_goods_list = list()

        # cat_name+paren_id : cat_id
        self.athena_cat_dict = dict()

        self.init_athena()

    def init_athena(self):
        cate_sql = "select id,cat_name,parent_id from center_category WHERE is_deleted = 'N'"
        cate_array = self.athena_dao.db.get_data(cate_sql)
        for cate_data in cate_array:
            id = str(cate_data['id'])
            cat_name = str(cate_data['cat_name'])
            parent_id = str(cate_data['parent_id'])
            key = cat_name+"-"+parent_id
            self.athena_cat_dict[key] = id

    def console_part(self):
        monkey_sql = "select part_name,part_code,first_cat_name,second_cat_name,third_cat_name,sum_code from db_category_part where gmt_create like '2016-08-01 %'"
        new_part_array = self.monkey_dao.db.get_data(monkey_sql)
        for new_part_data in new_part_array:
            first_id = self.athena_cat_dict[str(new_part_data['first_cat_name'])+"-"+"0"]
            second_id = self.athena_cat_dict[str(new_part_data['second_cat_name'])+"-"+first_id]
            third_id = self.athena_cat_dict[str(new_part_data['third_cat_name'])+"-"+second_id]

            sql = "insert into center_part(part_name,part_code,third_cate_id,sum_code,cat_kind,gmt_create,gmt_modified) VALUES "
            sql += "('"+str(new_part_data['part_name'])+"','"
            sql += str(new_part_data['part_code'])+"','"
            sql += third_id +"','"
            sql += str(new_part_data['sum_code'])+"','1',now(),now();"

            print sql


changePart  =ChangePart()
changePart.console_part()