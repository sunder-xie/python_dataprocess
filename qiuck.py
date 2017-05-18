# encoding=utf-8
__author__ = 'zxg'


from util import CrawlDao,FileUtil

dao = CrawlDao.CrawlDao("test", "local")
fileDao = FileUtil.FileDao()

print "=====start======"

warehouse_id =  22129
org_id =  50450
seller_id = 10155

goods_start_id = 1100000

goods_data_list = list()
third_data_list = list()

# sql
brand_dict = dict()
brand_sql = "select brand_id,brand_name from db_brand"
brand_array = dao.db.get_data(brand_sql)
for brand_data in brand_array:
    brand_dict[str(brand_data['brand_name'])] = str(brand_data['brand_id'])

excle_file = r'/Users/zxg/Desktop/Hyundai-杭州韩现配件商品-- 数据2016-5500+.xls'
# 单个excle处理
data = fileDao.open_excel(excle_file)
#
table = data.sheets()[0]

n_rows = table.nrows  # 行数
n_cols = table.ncols  # 列数
print ('行数：%s ,列数：%s' % (n_rows, n_cols))

start_row_num = 2
for rownum in range(1, n_rows):
    row = table.row_values(rownum)
    quality_type = 0 # 默认为品牌件
    quality_name = str(row[3]).strip().replace("品牌/","")
    if quality_name == '正厂1':
        continue
    if quality_name == '正厂' or quality_name == 'zc':
        quality_type = 1
        quality_name = ""
    elif quality_name == '配套':
        quality_type = 2
        quality_name = ""
    elif " 配套/" in quality_name:
        quality_type = 2
        quality_name = quality_name.replace("配套/","")

    brand_id = '0'
    if quality_name != "" and quality_name in brand_dict.keys():
        brand_id = brand_dict[quality_name]

    goods_name = str(row[1]).strip()
    car_name = str(row[2]).strip()
    goods_unint = str(row[4]).strip()
    price = str(row[6]).strip().replace(".0","")

    oe_number_array = str(row[0]).strip().replace("-","").split("/")

    i = 0
    for oe_numer in oe_number_array:
        goods_data = {'new_goods_sn':"Test"+str(rownum)+str(i),'goods_name':goods_name,
                      'brand_id':brand_id,'oe_num':oe_numer,'goods_quality_type':quality_type,'measure_unit':goods_unint,
                      'car_model':car_name,'goods_id':goods_start_id}

        third_data = {'goods_id':goods_start_id,'warehouse_id':warehouse_id,'third_part_id':org_id,'price':price,'yun_xiu_price':price*0.8}

        goods_start_id += 1
        i += 1



print "=====end======"

