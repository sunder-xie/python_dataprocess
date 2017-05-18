# encoding=utf-8
# 处理 monkey中的商品数据，置电商数据为 已处理
__author__ = 'zxg'


from util import CrawlDao

dao = CrawlDao.CrawlDao("modeldatas","local")


stall_dict = dict()
stall_key_list = list()
stall_array = dao.db.get_data("select dg.goods_id as 'goodsId',dg.goods_format as 'format',db.brand_name as 'brandName' from db_goods dg,db_brand db where dg.is_delete = 0 and dg.seller_id = 1 and dg.brand_id = db.brand_id")
for stall_data in stall_array:
    goods_id = str(stall_data['goodsId'])
    format = str(stall_data['format']).replace(" ","").strip()
    brandName = str(stall_data['brandName']).upper()

    key = brandName+format

    stall_key_list.append(key)
    stall_dict[key] = goods_id

# 数据已整理的id
have_up_id_list = list()
monkey_have_up_id_list = list()
monkey_array = dao.db.get_data("select dg.id as id,dg.goods_code as goods_code,db.name_ch as name_ch,db.name_en as name_en from db_monkey_commodity_goods dg,db_monkey_commodity_brand db where db.id = dg.brand_id ")
for monkey_data in monkey_array:
    goods_code = str(monkey_data['goods_code']).replace(" ","").strip()
    id = str(monkey_data['id'])
    name_ch = str(monkey_data['name_ch'])
    name_en = str(monkey_data['name_en'])

    if name_en == '':
        brand_name = name_ch
    elif name_ch == '':
        brand_name = name_en
    else:
        brand_name = name_ch+"/"+name_en

    key = brand_name.upper()+goods_code
    if key in stall_key_list:
        goods_id = stall_dict[key]
        have_up_id_list.append(goods_id)

        monkey_have_up_id_list.append(id)


update_file_object = open(r'/Users/zxg/Desktop/temp/goods/1.update_goods_flag.sql', 'w')
try:
    update_file_object.writelines("update db_goods set data_flag = 1,gmt_modified = now() where goods_id in (")
    update_file_object.writelines(",".join(have_up_id_list))
    update_file_object.writelines(");")
finally:
    update_file_object.close()

se_update_file_object = open(r'/Users/zxg/Desktop/temp/goods/2.update_monkey.sql', 'w')
try:
    se_update_file_object.writelines("update db_monkey_commodity_goods set sale_status = 1,gmt_modified = now() where id in (")
    se_update_file_object.writelines(",".join(monkey_have_up_id_list))
    se_update_file_object.writelines(");")
finally:
    se_update_file_object.close()





