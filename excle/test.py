# encoding=utf-8
# test
__author__ = "ximeng"

import json
import sys
import re
import os
# sys.path.append(os.getcwd()+"\\excle\\util")
from util import CrawlDao, FileUtil, HttpUtil
reload(sys)
sys.setdefaultencoding("utf-8")
print 3
# all_car_name = "丰田"
# leike = "雷克萨斯RX270/350/450H"
# if leike.find(u"雷克萨斯") > -1:
#         all_car_name += " "
#         for i in range(0, len(leike)):
#             name = leike[i]
#             if name.isdigit():
#                 break
#             else:
#                 all_car_name += name
# real_car_name = all_car_name.split(" ")[1]
# if real_car_name.find(u"雷克萨斯") > -1:
#     real_car_name = real_car_name[12:]
#
# print real_car_name
# dao = CrawlDao.CrawlDao()
# sql_string = "select Id,offer_car_name,company,start_year,end_year,displacement,brand_name from db_monkey_offer_car "
# resultArray = dao.db.get_data(sql_string)
#
# for result in resultArray:
#     ID = result["Id"]
#     car_name = result["offer_car_name"]
#     company = result["company"]
#
#     car_data = dict()
#     car_data["brand_name"] = result["brand_name"]
#     car_data["end_year"] = result["end_year"]
#     car_data["start_year"] = result["start_year"]
#     car_data["displacement"] = result["displacement"]
#     car_data["company"] = result["company"]
#
#     where_data = dict()
#     where_data["Id"] = ID
#
#     if car_name.find(u"/") > -1:
#         car_name_array = car_name.split("/")
#         car_name = car_name_array[0]
#         new_car_name = car_name_array[1]
#         car_data["offer_car_name"] = car_name
#         dao.update_temple("db_monkey_offer_car", car_data, where_data)
#
#         # 插入新的记录
#         car_data["offer_car_name"] = new_car_name
#
#         if new_car_name.find(u"广汽") > -1:
#             car_data["company"] = "广汽丰田"
#         new_car_id = dao.insert_without_exit("db_monkey_offer_car", car_data, car_data)
#
#         # 关系表中查找关系
#         sql_string = "select offer_goods_id from db_monkey_offer_goods_car_relation where car_id ="+str(ID)
#         relation_result_array = dao.db.get_data(sql_string)
#         for relation_result in relation_result_array:
#             relation_data = dict()
#             relation_data["offer_goods_id"] = relation_result["offer_goods_id"]
#             relation_data["car_id"] = new_car_id
#             dao.insert_without_exit("db_monkey_offer_goods_car_relation", relation_data, relation_data)


# for result in resultArray:
#     ID = result["Id"]
#     car_name = result["offer_car_name"]
#     company = result["company"]
#
#     car_data = dict()
#     where_data = dict()
#     where_data["Id"] = ID
#
#     # car_name_array = car_name.split(" ")
#     #
#     # car_name = ""
#     # for i in range(1, len(car_name_array)):
#     #     car_name += car_name_array[i]
#
#     if company == "进口丰田":
#         company = "丰田汽车"
#     elif company == "一汽":
#         company = "一汽丰田"
#     elif company == "广汽":
#         company = "广汽丰田"
#
#
#     car_data["company"] = company
#     if car_name.find(u"雷克萨斯") > -1:
#         car_data["offer_car_name"] = ""
#         for i in range(4,len(car_name)):
#             name = car_name[i]
#             if name.isdigit():
#                 break
#             else:
#                 car_data["offer_car_name"] += name
#     else:
#         car_data["offer_car_name"] = car_name
#
#     dao.update_temple("db_monkey_offer_car", car_data, where_data)


# a = ""
# b = ""
# time = "2010"
# car_year_array = time.split("-")
# if len(car_year_array) == 1:
#     a = time
#     b = time
# if len(car_year_array) == 1:
#     if "-" == time[0]:
#         a = car_year_array[0]
#     if "-" == time[:-1]:
#         b = car_year_array[0]
# result_year = "2006.06"
# index = result_year.find(".")
#
# b = "456"
# if "." in result_year:
#     b = "123"
# a = result_year[:4]
# print "a:%s && b:%s" % (a,b)
# goods_record_data = dict()
# q = goods_record_data.has_key("linkman_phone")
# print q
#


# 更改的价格 update
# fileDao = FileUtil.FileDao()
# dao = CrawlDao.CrawlDao()
# excle = r"D:\PythonExcle\offerGoods\5.28offerGoods_pricechange.xls"
# data = fileDao.open_excel(excle)
# table = data.sheets()[0]
# nrows = table.nrows  # 行数
# ncols = table.ncols  # 列数
# # 遍历数据
# for rownum in range(1, nrows):
#     row = table.row_values(rownum)
#     oe = row[6]
#     price = row[11]
#     advicePrice = row[12]
#     a = row[19]
#
#     select_sql = "select id from db_monkey_offer_goods where oe_num = '"+str(oe)+"'"
#     print select_sql
#     data = dao.db.get_data(select_sql)
#     id = data[0]["id"]
#
#     update_sql = "update db_monkey_offer_record set prime_price_tax ="+str(price)+" ,advice_sale_price ="+str(advicePrice)
#     update_sql += " where offer_goods_id ="+str(id)
#     print update_sql
#     dao.db.update_data(update_sql)
#
#     goods_updata_sql = "update db_monkey_offer_goods set measure_unit ='"+str(a)+"' ,min_measure_unit ='"+str(a)
#     goods_updata_sql += "' where id = '"+str(id)+"'"
#     print goods_updata_sql
#     dao.db.update_data(goods_updata_sql)

# 测试修改的分类
# sum_code = 'C40107201'
# first = sum_code[1:2]
# second = sum_code[2:4]
# third = sum_code[4:7]
# part = sum_code[7:]
#
# type = sum_code[0:1]
#
# delete_end = sum_code[:len(sum_code)-1]
#
# print delete_end

# 测试double四舍五入
# a = '36.1666666667'
# b = '34.4444444444'
#
# fl = float(a)
# c = round(fl, 2)
# print c

# 测试写文件
# txt =r'D:\PythonExcle\cate\updateCate.txt'
# file = open(txt, "r" )
# content = file.read()
# file.close()
#
# fo = open(txt, "w+")
# print "Name of the file: ", fo.name
#
# seq = ["This is sadsadsa12131321 line\n", "This is 10th line"]
# # fo.seek(0, 2)
# for q in seq:
#     content +=q
# fo.writelines(content)
# fo.close()

# 测试读测试库
# sql_string = 'select id from dw_crawl_car_brand where 1=1 order by id desc limit 1'
# dao = CrawlDao.CrawlDao()
# result = dao.db.get_data(sql_string)
# # 初始数据准备final_id = 1233
# final_id = str(result[0]['id'])
# print final_id

# 正则匹配
name = 'Veloster飞思'
name1 = '我是正RS7常的'
name2 = '我是正常的AQ6'
name3 = '我是正常的(sho'
# 将正则表达式编译成Pattern对象
result = re.findall(r"\w+", name)
print len(result)
index = name3.find("(")
index1 = name3.find("正常的")
result_string = name3[:index]
pattern = re.compile(r'\w')

# 使用Pattern匹配文本，获得匹配结果，无法匹配时将返回None
match = pattern.match(name1)
print 'hhh'

