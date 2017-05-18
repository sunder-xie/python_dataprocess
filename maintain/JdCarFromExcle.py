# encoding=utf-8
# 京东没匹配上的车型的excle的处理
import os

__author__ = 'zxg'

from util import FileUtil, CrawlDao

# 初始化力洋数据
def init_liyang():
    liyang_show_dict = dict()
    monkey_dao = CrawlDao.CrawlDao('modeldatas', 'online_cong')
    liyang_array = monkey_dao.db.get_data(
        "select leyel_id,car_brand,factory_name,car_series,model_year,vehicle_type,market_name from db_car_info_all")
    for liyang_data in liyang_array:
        leyel_id = str(liyang_data['leyel_id'])
        car_brand = str(liyang_data['car_brand']).replace("·", "")
        factory_name = str(liyang_data['factory_name']).replace("·", "").replace("·", "")
        car_series = str(liyang_data['car_series'])
        model_year = str(liyang_data['model_year'])
        vehicle_type = str(liyang_data['vehicle_type'])
        market_name = str(liyang_data['market_name'])

        # 实际匹配dict
        show_key = car_brand + "-" + factory_name + "-" + car_series
        show_name = model_year + "款 " + vehicle_type + " " + market_name

        if show_key in liyang_show_dict.keys():
            show_dict = dict(liyang_show_dict[show_key])
        else:
            show_dict = dict()

        if show_name in show_dict.keys():
            leyel_list = list(show_dict[show_name])
        else:
            leyel_list = list()
        leyel_list.append(leyel_id)
        show_dict[show_name] = leyel_list
        liyang_show_dict[show_key] = show_dict

    return liyang_show_dict


liyang_show_dict = init_liyang()

fileDao = FileUtil.FileDao()
# 处理excle
excle_file = os.getcwd() + r'/jdcar-final.xls'
print excle_file

# 单个excle处理
data = fileDao.open_excel(excle_file)
#
table = data.sheets()[0]

n_rows = table.nrows  # 行数
n_cols = table.ncols  # 列数
print ('行数：%s ,列数：%s' % (n_rows, n_cols))

need_up_dict = dict()
for row_num in range(1, n_rows):
    row = table.row_values(row_num)

    jd_car_id = str(row[0]).replace(".0", "").strip()

    car_brand = str(row[5]).replace(".0", "").strip()
    factory_name = str(row[6]).replace(".0", "").strip()
    car_series = str(row[7]).replace(".0", "").strip()

    if car_brand == '':
        continue

    show_name = str(row[8]).strip()
    show_key = car_brand + "-" + factory_name + "-" + car_series

    # print show_key+" ==== "+show_name
    if show_key not in liyang_show_dict.keys():
        print "not have this show:%s" % show_key
        continue
    show_dict = dict(liyang_show_dict[show_key])
    if show_name not in show_dict.keys():
        print "not have this show:%s" % show_key + " " + show_name
        continue
    leyel_list = list(show_dict[show_name])

    if jd_car_id in need_up_dict.keys():
        li_set = set(need_up_dict[jd_car_id])
    else:
        li_set = set()
    li_set.update(leyel_list)

    need_up_dict[jd_car_id] = li_set

crawl_dao = CrawlDao.CrawlDao('dev_crawler', 'test')
for jd_car_id, li_set in need_up_dict.iteritems():
    liyang_string = ",".join(li_set)

    crawl_dao.update_temple("jd_car", {'liyang_id_list': liyang_string, 'the_type': 1},
                            {'jd_car_id': jd_car_id})
