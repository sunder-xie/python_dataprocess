# encoding=utf-8
# 4S店数据导入
__author__ = 'ximeng'

import re
import sys

from util import CrawlDao, FileUtil
reload(sys)
sys.setdefaultencoding("utf-8")


class OfferGoods():
    def __init__(self, *name, **kwargs):
        # super(OfferGoods, self).__init__(*name, **kwargs)
        self.measure_unit_dic = dict()
        self.dao = CrawlDao.CrawlDao()
        self.index_sql_table = {}
        self.goods_name = 'goods'
        self.car_name = 'car'
        self.record_name = 'record'

    # 车型年款处理
    def car_year_process(self, car_array_data, goods_data, year_value):
        if 'oe_num' not in goods_data.keys():
            return
        if 'oe_num' in goods_data.keys() and goods_data['oe_num'] == '':
            return

        new_year_value = str(year_value).replace(".0", "")
        year = new_year_value.split("/")
        q = False
        year_list = list()
        for i in range(0, len(year)):
            car_year_array = year[i].split("-")
            if len(car_year_array) == 1:
                result_year = car_year_array[0].strip()
                if len(result_year) > 4:
                    q = True
                    result_year = result_year[:4]
                start = result_year
                end = result_year
            else:
                start = car_year_array[0].strip()
                end = car_year_array[1].strip()
                if len(start) > 4 or len(end) > 4:
                    q = True
                    start = start[:4]
                    end = end[:4]
            this_car_data = dict()
            this_car_data['start_year'] = start
            this_car_data['end_year'] = end
            # 多个年份保存下来
            year_list.append(this_car_data)
        car_array_data['year_list'] = year_list
        if q:
            # 判断有没有备注
            if goods_data.has_key('remark'):
                goods_data['remark'] += ' 车型适用年款：'+str(year_value)
            else:
                goods_data['remark'] = '车型适用年款：'+str(year_value)

    # 品牌处理
    def goods_brand_process(self, value, goods_data):
        key = value.decode('utf-8')
        # 初步筛选
        if self.goods_quality_type_table.has_key(key):
            goods_quality_type = self.goods_quality_type_table.get(key)
            goods_data['brand_name'] = ''
        else:
            # 筛选分号
            array = value.split("/")
            if len(array) > 1:
                key = array[0].decode('utf-8')
                if self.goods_quality_type_table.has_key(key):
                    goods_quality_type = self.goods_quality_type_table.get(key)
                    goods_data['brand_name'] = array[1]
                else:
                    print "=======================the wrong value:%s" % value
            else:
                goods_quality_type = 0
                goods_data['brand_name'] = value
        goods_data['goods_quality_type'] = goods_quality_type

    # 存储处理数据入数据库
    def save_data(self, goods_data, car_array_data, record_data):
        dao = self.dao

        goods_exit_data = dict()
        if 'oe_num' not in goods_data.keys():
            return
        if 'oe_num' in goods_data.keys() and goods_data['oe_num'] == '':
            return

        # ===================================================================存商品数据====================
        oe = str(goods_data['oe_num'].replace('.0', ''))
        if oe.startswith("(") and oe.endswith(")"):
            print "() oe is :%s" % oe
            oe = oe[1:len(oe)-2]
            print "after() oe is :%s" % oe

        # 判断是否有特殊字符，除- 和()外
        if oe.find('.') > -1 or oe.find('=') > -1 or oe.find('=') > -1 or oe.find('+') > -1 or oe.find('->') > -1 or oe.find('/') > -1:
            goods_data['oe_iswrong'] = 1

        # 中文正则
        zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')
        match = zh_pattern.search(oe)
        if match:
            print u'oe中有中文：%s' % oe
            goods_data['oe_iswrong'] = 1

        # 对OE的后缀做处理,暂时对末尾为 - 的数据做处理
        while True:
            if oe.endswith('-'):
                oe = oe[:len(oe)-1]
            else:
                break

        # 处理单位转换值

        if 'goods_quality_type' not in goods_data.keys():
            goods_data['goods_quality_type'] = 8
        if 'brand_name' not in goods_data.keys():
            goods_data['brand_name'] = ''

        goods_data['oe_num'] = oe
        goods_exit_data['oe_num'] = oe
        goods_exit_data['brand_name'] = goods_data['brand_name']
        goods_exit_data['goods_quality_type'] = goods_data['goods_quality_type']
        # ==================================存商品数据之前Pool池查一遍====================
        select_list = list()
        select_list.append('brand_id')
        select_list.append('brand_name')
        select_list.append('part_id')
        select_list.append('third_cate_id')
        select_list.append('third_cate_name')
        select_list.append('second_cate_id')
        select_list.append('second_cate_name')
        select_list.append('first_cate_id')
        select_list.append('first_cate_name')
        select_list.append('part_name')
        select_list.append('part_sum_code')

        where_dict = dict()
        where_dict['oe_num'] = goods_data['oe_num']

        select_data = dao.select_temple('db_pool_goods', select_list, where_dict)
        if select_data:
            for key in select_list:
                goods_data[key] = select_data[0][key]
            goods_data['cate_status'] = 3
            goods_data['brand_status'] = 3

        goods_id = dao.insert_without_exit("db_ext_goods", goods_data, goods_exit_data)

        # =========================================存记录--价格信息====================================================
        record_data['goods_id'] = goods_id
        dao.insert_without_exit("db_ext_record", record_data, record_data)
        # 处理车型数据(车系有/ 年份有/)
        # u'淘汽车系': 'offer_car_name',
        # u'淘汽品牌': 'brand_name',
        # u'淘汽厂商': 'company'
        # 无品牌
        if 'brand_name' not in car_array_data.keys():
            car_data = dict()
            car_data['brand_name'] = ''
            # 存车型数据
            car_id = dao.insert_without_exit("db_ext_car", car_data, car_data)
            # 存车型和商品的对应关系
            goods_car_data = dict()
            goods_car_data['offer_goods_id'] = goods_id
            goods_car_data['car_id'] = car_id
            dao.insert_without_exit("db_ext_goods_car_relation", goods_car_data, goods_car_data)
        else:
            brand_array = car_array_data['brand_name'].split("/")
            for brand_name in brand_array:
                # 无公司
                if 'company' not in car_array_data.keys():
                    car_data = dict()
                    car_data['brand_name'] = brand_name
                    # 存车型数据
                    car_id = dao.insert_without_exit("db_ext_car", car_data, car_data)
                    # 存车型和商品的对应关系
                    goods_car_data = dict()
                    goods_car_data['offer_goods_id'] = goods_id
                    goods_car_data['car_id'] = car_id
                    dao.insert_without_exit("db_ext_goods_car_relation", goods_car_data, goods_car_data)
                else:
                    company_array = car_array_data['company'].split("/")
                    for company in company_array:
                        if 'offer_car_name' in car_array_data.keys():
                            series_name_array = car_array_data['offer_car_name'].split("/")
                            for series_name in series_name_array:
                                if 'year_list' in car_array_data.keys():
                                    for year_dat in car_array_data['year_list']:
                                        car_data = dict()
                                        car_data['brand_name'] = brand_name
                                        car_data['company'] = company
                                        car_data['offer_car_name'] = series_name
                                        if 'displacement' in car_array_data.keys():
                                            car_data['displacement'] = car_array_data['displacement']
                                        car_data['start_year'] = year_dat['start_year']
                                        car_data['end_year'] = year_dat['end_year']
                                        # 存车型数据
                                        car_id = dao.insert_without_exit("db_ext_car", car_data, car_data)
                                        # 存车型和商品的对应关系
                                        goods_car_data = dict()
                                        goods_car_data['offer_goods_id'] = goods_id
                                        goods_car_data['car_id'] = car_id
                                        dao.insert_without_exit("db_ext_goods_car_relation", goods_car_data, goods_car_data)
                                else:
                                    car_data = dict()
                                    car_data['brand_name'] = brand_name
                                    car_data['company'] = company
                                    car_data['offer_car_name'] = series_name
                                    if 'displacement' in car_array_data.keys():
                                        car_data['displacement'] = car_array_data['displacement']

                                    # 存车型数据
                                    car_id = dao.insert_without_exit("db_ext_car", car_data, car_data)
                                    # 存车型和商品的对应关系
                                    goods_car_data = dict()
                                    goods_car_data['offer_goods_id'] = goods_id
                                    goods_car_data['car_id'] = car_id
                                    dao.insert_without_exit("db_ext_goods_car_relation", goods_car_data, goods_car_data)
                        else:
                            # 存车型数据
                            if 'year_list' in car_array_data.keys():
                                for year_dat in car_array_data['year_list']:
                                    car_data = dict()
                                    car_data['brand_name'] = brand_name
                                    car_data['company'] = company
                                    if 'displacement' in car_array_data.keys():
                                        car_data['displacement'] = car_array_data['displacement']
                                    car_data['start_year'] = year_dat['start_year']
                                    car_data['end_year'] = year_dat['end_year']
                                    car_id = dao.insert_without_exit("db_ext_car", car_data, car_data)
                                    # 存车型和商品的对应关系
                                    goods_car_data = dict()
                                    goods_car_data['offer_goods_id'] = goods_id
                                    goods_car_data['car_id'] = car_id
                                    dao.insert_without_exit("db_ext_goods_car_relation", goods_car_data, goods_car_data)
                            else:
                                car_data = dict()
                                car_data['brand_name'] = brand_name
                                car_data['company'] = company
                                if 'displacement' in car_array_data.keys():
                                    car_data['displacement'] = car_array_data['displacement']

                                # 存车型数据
                                car_id = dao.insert_without_exit("db_ext_car", car_data, car_data)
                                # 存车型和商品的对应关系
                                goods_car_data = dict()
                                goods_car_data['offer_goods_id'] = goods_id
                                goods_car_data['car_id'] = car_id
                                dao.insert_without_exit("db_ext_goods_car_relation", goods_car_data, goods_car_data)
                        print 'END~~~~~这一行'

    # 按列处理
    def col_process(self, row, ncols, goods_data, car_array_data, record_data):
        for cols_num in range(1, ncols):
            value = str(row[cols_num]).replace("（", "(").replace("）", ")")
            # 若无数据
            if value == '' or value == '-' or value == '#N/A':
                continue

            # 若为不需要的字段
            if self.index_sql_table.has_key(cols_num):
                index_sql_string = self.index_sql_table[cols_num]
            else:
                continue
            sql_cols_array = index_sql_string.split(" ")
            sql_cols_name = sql_cols_array[0]
            sql_cols_type = sql_cols_array[1]
            # 行中的goods数据
            if sql_cols_type == self.goods_name:
                value = str(value).strip()
                if value == '0':
                    continue
                # 商品属性处理
                if sql_cols_name == 'brand':
                    self.goods_brand_process(value, goods_data)
                else:
                    goods_data[sql_cols_name] = value.replace(" ", "").upper()
            # 行中的car数据
            elif sql_cols_type == self.car_name:
                # 对年款处理
                if sql_cols_name == 'year':
                    self.car_year_process(car_array_data,goods_data, value)
                elif sql_cols_name == 'displacement':
                    displacement = str(value).strip().replace("／", "/")
                    car_array_data['displacement'] = displacement
                else:
                    car_array_data[sql_cols_name] = str(value).strip().replace("／", "/").replace('.0', '')
            # 行中的record数据
            elif sql_cols_type == self.record_name:
                record_data[sql_cols_name] = value

    # 对第一行 进行处理
    def first_row_process(self, table, ncols):
        # 第一行的列名
        first_row = table.row_values(0)
        for cols_num in range(1, ncols):
            cols_name = first_row[cols_num].strip()
            sql_cols_name = self.sql_goods_table.get(cols_name)
            if sql_cols_name is not None:
                self.index_sql_table[cols_num] = sql_cols_name+" "+self.goods_name
            else:
                sql_cols_name = self.sql_car_table.get(cols_name)
                if sql_cols_name is not None:
                    self.index_sql_table[cols_num] = sql_cols_name+" "+self.car_name
                else:
                    sql_cols_name = self.sql_record_table.get(cols_name)
                    if sql_cols_name is not None:
                        self.index_sql_table[cols_num] = sql_cols_name+" "+self.record_name

    # 对第二行开始的数据进行处理
    def next_row_process(self, table, excle_name, nrows, ncols):
        # 遍历数据
        for rownum in range(1, nrows):
            row = table.row_values(rownum)
            # 存数据库的goods字段
            goods_data = dict()
            # 可能有多个车系，需后续处理
            car_array_data = dict()
            # 单条价格记录，直接存数据库record字段
            record_data = dict()
            record_data['record_name'] = excle_name
            self.col_process(row, ncols, goods_data, car_array_data, record_data)

            # 存储数据
            self.save_data(goods_data, car_array_data, record_data)

    # 主处理函数
    def main(self, excle, excle_name):
        print '===============start all==================='
        # 数据初始化
        fileDao = FileUtil.FileDao()

        # 单个excle处理
        data = fileDao.open_excel(excle)
        table = data.sheets()[0]
        nrows = table.nrows  # 行数
        ncols = table.ncols  # 列数

        print ('行数：%s ,列数：%s' %(nrows ,  ncols))

        # measure_unit_table = data.sheets()[1]
        #
        # for rownum in range(1, measure_unit_table.nrows):
        #     row = measure_unit_table.row_values(rownum)
        #     key = row[0].strip()
        #     value = row[1].strip()
        #     self.measure_unit_dic[key] = value

        # 第一行
        self.first_row_process(table, ncols)
        # 第二行开始的后面所有
        self.next_row_process(table, excle_name, nrows, ncols)
        print '===============end all==================='

    # 列名跟数据库字段对应
    sql_goods_table = {
        u'零件名称': 'goods_name',
        u'产品属性（商品品牌）': 'brand',
        u'零件编码OE码': 'oe_num',
        u'零件编码(OE码)': 'oe_num',
        u'备注说明': 'remark',
        u'淘汽零件名称': 'part_name',
        u'淘汽零件编码': 'part_sum_code',
        u'单位': 'measure_unit'
    }
    sql_car_table = {
        u'发动机排量': 'displacement',
        u'年款': 'year',
        u'淘汽车系': 'offer_car_name',
        u'淘汽品牌': 'brand_name',
        u'淘汽厂商': 'company'
    }
    sql_record_table = {
        u'供应淘气价格': 'prime_price_tax',
        u'建议零售价': 'advice_sale_price',
        u'4S进价': 'prime_price_S',
        u'4S售价': 'prime_sale_S',
        u'配件商名称': 'provider_name'
    }

    goods_quality_type_table = {
        u'正厂原厂': 1,
        u'正厂配套': 2,
        u'正厂下线': 3,
        u'全新拆车': 4,
        u'旧件拆车': 5,
        u'副厂': 6,

        # 其他名称
        u'原厂': 1,
        u'原厂正厂': 1,
        u'下线': 3,
        u'正厂': 1,
        u'配套': 2,
        u'品牌': 0,
        u'高仿': 9
    }


# fileDao = FileUtil.FileDao()
#
# fileList = []
# file_list = fileDao.get_file_list('D:\PythonExcle\S_goods_car_excle', fileList)
# for excle in file_list:
#     print excle
#
#     excle = excle.decode('utf-8')
#     excleArray = excle.split('\\')
#     excle_name = excleArray[len(excleArray)-1].split('.')[0]
#
#     offerGoods = OfferGoods()
#     offerGoods.main(excle,excle_name)

excle = r'D:\PythonExcle\S_goods_car_excle\福特4S已修改.xlsx'
excle_name = u'福特4S已修改'

offerGoods = OfferGoods()
offerGoods.main(excle.decode('utf-8'), excle_name)
