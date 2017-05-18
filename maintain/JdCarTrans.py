# encoding=utf-8
# 京东车型转力洋id
import re

__author__ = 'zxg'

import CrawlDao


class JdCarLiyang:
    def __init__(self):
        self.is_test = False
        # crawl
        self.crawl_dao = CrawlDao.CrawlDao('dev_crawler', 'test')
        if self.is_test:
            self.monkey_dao = CrawlDao.CrawlDao('modeldatas', 'test')
        else:
            self.monkey_dao = CrawlDao.CrawlDao('modeldatas', 'online_cong')

        # 转换数据字典
        self.brand_dict = {'哈弗': '长城'}
        self.factory_dict = {'克莱斯勒汽车': '克莱斯勒', '北京吉普': '北京吉普(现北京奔驰)', '广汽长丰': '广汽三菱', '上汽通用': '上海通用',
                             '一汽大众奥迪': '一汽大众(奥迪)', '巴博斯': '巴博斯汽车', '长丰扬子': '长丰扬子汽车', '神龙汽车': '东风标致', '比亚迪': '比亚迪汽车',
                             '郑州海马': '一汽海马', '法拉利': '法拉利汽车', '长安福特马自达': '长安福特', '迈凯伦': '迈凯伦汽车'}
        self.series_dict = {'2008': '008', '5008': '008', 'A4L': 'A4', 'A6L': 'A6', 'A8L': 'A8', 'Yeti': '野帝',
                            '悦动': '伊兰特',
                            '朗动': '伊兰特'}
        self.model_dict = {'Yeti': '野帝', '悦动': '伊兰特 悦动', '朗动': '伊兰特 朗动', ' 50周年 ': ' 50周年纪念 ',
                           '2008款 帕杰罗V77 3.8 自动': '2008款 帕杰罗V77 3.8 手自一体', '花冠EX': '花冠', '美日': '美日之星',
                           '民意 1.1 手动 9座': '民意 1.1 手动 5-9座', 'POLO 1.': 'POLO-两厢 1.', '奥德赛 2.4 自动': '奥德赛 2.4 手自一体',
                           '2004款 飞度': '2004款 飞度-三厢', '2006款 飞度': '2006款 飞度-两厢',
                           '2012款 欧朗': '2012款 欧朗-三厢', '致胜': '蒙迪欧致胜', '快运 2.8T 柴油': '快运 2.8T 手动 柴油',
                           ' 金刚 ': ' 金刚-三厢 ', '550 Plug-in 1.5 自动': '550 Plug-in 1.5 双离合', 'L3 GT': 'L3 GT-三厢',
                           '天语SX4-两厢 1.6 手动 运动休旅版': '天语SX4-两厢 1.6 手动 运动休旅款',
                           '天语SX4-两厢 1.6 自动 运动休旅版': '天语SX4-两厢 1.6 自动 运动休旅款',
                           '世嘉-三厢 1.6 手动': '世嘉-三厢 1.6 手动 VTS版', '世嘉-三厢 2.0 手自一体': '世嘉-三厢 2.0 手自一体 VTS版',
                           '世嘉-三厢 1.6 手自一体': '世嘉-三厢 1.6 手自一体 VTS版', ' 马自达2 ': ' 马自达2两厢 ',
                           '世嘉-三厢 2.0 手动': '世嘉-三厢 2.0 手动 VTS版', ' 爱丽舍 ': ' 爱丽舍-三厢 ', ' S30 ': ' S30-三厢 ',
                           ' E系列 ': ' E系列-两厢 '
                           }

        # 剩余的数据
        self.left_data_list = list()

        # brand-factory:list(series_dict)
        self.brfa_series_dict = dict()

        # show_name:vehicle_type
        self.show_name_ve_dict = dict()

    # 京东车型适配到力洋车型,可每次都
    def init_liyang(self):
        liyang_show_dict = dict()
        liyang_array = self.monkey_dao.db.get_data(
            "select leyel_id,car_brand,factory_name,car_series,model_year,vehicle_type,market_name from db_car_info_all")
        for liyang_data in liyang_array:
            leyel_id = str(liyang_data['leyel_id'])
            car_brand = str(liyang_data['car_brand']).replace("·", "")
            factory_name = str(liyang_data['factory_name']).replace("·", "").replace("·", "")
            car_series = str(liyang_data['car_series'])
            model_year = str(liyang_data['model_year'])
            vehicle_type = str(liyang_data['vehicle_type'])
            market_name = str(liyang_data['market_name'])

            # brand-factory:list(series_dict)
            brfa_key = car_brand + "-" + factory_name
            if brfa_key in self.brfa_series_dict.keys():
                series_set = set(self.brfa_series_dict[brfa_key])
            else:
                series_set = set()
            series_set.add(car_series)
            self.brfa_series_dict[brfa_key] = series_set


            # 实际匹配dict
            show_key = car_brand + "-" + factory_name + "-" + car_series
            show_name = model_year + "款 " + vehicle_type + " " + market_name
            self.show_name_ve_dict[show_name] = vehicle_type

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

    # 初始匹配，最原始的对比
    def first_original_do(self, liyang_show_dict=dict()):
        jd_car_array = self.crawl_dao.db.get_data(
            "select car_uuid,jd_brand_name,jd_factory_name,jd_series_name,jd_model_name,liyang_id_list from jd_car ")
        for jd_car_data in jd_car_array:
            id = str(jd_car_data['car_uuid'])
            liyang_id_list = str(jd_car_data['liyang_id_list'])
            jd_brand_name = str(jd_car_data['jd_brand_name'])
            jd_factory_name = str(jd_car_data['jd_factory_name']).replace("·", "").replace("进口", "汽车")
            jd_series_name = str(jd_car_data['jd_series_name']).replace("（", "(").replace("）", ")").replace("(进口)", "")
            # 2013款 A1 Sportback 1.4TFSI 双离合 30TFSI Ego:liyang model_year款 vehicle_type market_name
            jd_model_name = str(jd_car_data['jd_model_name'])

            show_key = jd_brand_name + "-" + jd_factory_name + "-" + jd_series_name
            show_name = jd_model_name

            if show_key not in liyang_show_dict.keys():
                self.left_data_list.append(jd_car_data)
                continue
            show_dict = dict(liyang_show_dict[show_key])
            if show_name not in show_dict.keys():
                self.left_data_list.append(jd_car_data)
                continue
            leyel_list = list(show_dict[show_name])

            liyang_string = ",".join(leyel_list)

            if liyang_string != liyang_id_list:
                self.update_jd_car(liyang_string, id)

    # 根据规则获得数据处理
    def second_rule_do(self, liyang_show_dict=dict()):
        # the_data_list = self.crawl_dao.db.get_data(
        #     "select car_uuid,jd_brand_name,jd_factory_name,jd_series_name,jd_model_name,liyang_id_list from jd_car where the_type = 0")
        the_data_list = self.left_data_list
        for jd_car_data in the_data_list:
            car_uuid = str(jd_car_data['car_uuid'])
            liyang_id_list = str(jd_car_data['liyang_id_list'])
            jd_brand_name = str(jd_car_data['jd_brand_name']).replace("·", "")
            jd_factory_name = str(jd_car_data['jd_factory_name']).replace("·", "").replace("进口", "汽车")
            jd_series_name = str(jd_car_data['jd_series_name']).replace("（", "(").replace("）", ")").replace("(进口)", "")
            # 2013款 A1 Sportback 1.4TFSI 双离合 30TFSI Ego:liyang model_year款 vehicle_type market_name
            jd_model_name = str(jd_car_data['jd_model_name'])

            if '天语SX4' in jd_series_name:
                print("da")

            if jd_brand_name in self.brand_dict.keys():
                jd_brand_name = self.brand_dict[jd_brand_name]

            if jd_brand_name == '雪铁龙' and '神龙' in jd_factory_name:
                jd_factory_name = '东风雪铁龙'

            if jd_factory_name in self.factory_dict.keys():
                jd_factory_name = self.factory_dict[jd_factory_name]

            if jd_series_name in self.series_dict.keys():
                jd_series_name = self.series_dict[jd_series_name]
            else:
                brfa_key = jd_brand_name + "-" + jd_factory_name
                if brfa_key not in self.brfa_series_dict.keys():
                    continue
                series_set = set(self.brfa_series_dict[brfa_key])

                series_not_found = True
                # 匹配[xxx]
                for series_name in series_set:
                    if "[" + jd_series_name + "]" in series_name:
                        jd_series_name = series_name
                        series_not_found = False
                        break
                if series_not_found:
                    # 常规包含
                    for series_name in series_set:
                        if jd_series_name in series_name:
                            jd_series_name = series_name
                            break
            for key, value in self.model_dict.iteritems():
                jd_model_name = jd_model_name.replace(key, value)

            show_key = jd_brand_name + "-" + jd_factory_name + "-" + jd_series_name
            show_name = jd_model_name

            if show_key not in liyang_show_dict.keys():
                print "not have this show:%s" % show_key
                # self.left_data_list.append(jd_car_data)
                continue
            show_dict = dict(liyang_show_dict[show_key])

            show_dict_list = show_dict.keys()

            is_no = True
            if show_name not in show_dict_list:
                show_array = show_name.split(" ")
                # 排量去T 匹配
                show_vehicle_type = self.get_vehicle_type_in_jd(show_array,show_array[1])
                show_other_string = show_name.replace(" " + show_vehicle_type + " ", "").strip().replace("T ", " ")
                # 匹配[]
                for show_dict_key in show_dict_list:
                    key_vehicle_type = self.show_name_ve_dict[show_dict_key]
                    key_other_string = show_dict_key.replace(" " + key_vehicle_type + " ", "").strip().replace("T ",
                                                                                                               " ")
                    if "[" + show_vehicle_type + "]" in key_vehicle_type and show_other_string == key_other_string:
                        show_name = show_dict_key
                        is_no = False
                        break
                if is_no:
                    # 常规匹配
                    for show_dict_key in show_dict_list:
                        key_vehicle_type = self.show_name_ve_dict[show_dict_key]
                        key_other_string = show_dict_key.replace(" " + key_vehicle_type + " ", "").strip().replace("T ",
                                                                                                                   " ")
                        if show_vehicle_type in key_vehicle_type and show_other_string == key_other_string:
                            show_name = show_dict_key
                            is_no = False
                            break
            else:
                is_no = False

            if is_no:
                print "not have this show:%s" % show_key + " " + show_name
                continue

            leyel_list = list(show_dict[show_name])

            liyang_string = ",".join(leyel_list)

            if liyang_string != liyang_id_list:
                self.update_jd_car(liyang_string, car_uuid)

    def jd_car_to_liyang(self):
        # {品牌——厂商—车系：
        #           {model_year款 vehicle_type market_name：set(leyel_id)}
        # }
        print "===========start======================"
        liyang_show_dict = self.init_liyang()

        # 初次匹配：原始匹配
        self.first_original_do(liyang_show_dict)
        # 二次匹配，规则筛选后匹配
        self.second_rule_do(liyang_show_dict)

        print "===========end======================"

    # 根据jd 的名称 获得其中的vehicle_type
    def get_vehicle_type_in_jd(self, jd_name_array, show_vehicle_type, next_num=2):
        array_length = len(jd_name_array)
        if next_num > array_length - 1:
            return show_vehicle_type
        add_type = jd_name_array[next_num]
        number_pattern = re.compile(r'[\d*]\.[\d*]')
        match = number_pattern.search(add_type)
        if match:
            return show_vehicle_type
        else:
            return self.get_vehicle_type_in_jd(jd_name_array, show_vehicle_type + " " + add_type, next_num + 1)

    # ==============save==========
    def update_jd_car(self, liyang_string, uu_id):
        if self.is_test:
            pass
        else:
            try:
                self.crawl_dao.update_temple("jd_car", {'liyang_id_list': liyang_string, 'the_type': 1},
                                             {'car_uuid': uu_id})
            except:
                self.crawl_dao = CrawlDao.CrawlDao('dev_crawler', 'test')
                self.crawl_dao.update_temple("jd_car", {'liyang_id_list': liyang_string, 'the_type': 1},
                                             {'car_uuid': uu_id})


jdCarLiyang = JdCarLiyang()
jdCarLiyang.jd_car_to_liyang()
