# encoding=utf-8
# 2015.11.23 分类的编码规则改变和新增部分类目
# 一级、二级无法区分是否 为全车件或易损件
__author__ = 'zxg'

import sys

from util import CrawlDao, FileUtil, StringUtil

reload(sys)
sys.setdefaultencoding("utf-8")


class ChangeCate:
    def __init__(self):
        self.dao = CrawlDao.CrawlDao("modeldatas")
        self.fileDao = FileUtil.FileDao()
        self.stringUtil = StringUtil.StringUtil()
        self.sql_category_table = 'db_category'
        self.sql_part_table = 'db_category_part'

        # 已更新的分类 name+level+parent_id
        self.category_have_list = list()
        # 已更新的part name+level
        self.part_have_list = list()

        self.label_dict = {u'字标': '1', u'灯泡': '2', u'四滤': '3', u'': '0'}
        self.cat_kind_dict = {u'全车件': 1, u'易损件': 0}
        # 分类无法判断标识
        self.cat_kind_not = '3'
        self.aliss_name_text = ''
        self.label_text = ''

        # db_category level:dict(name+parent_id)
        self.level_name = self.init_category()
        # db_category_part name+cate_id:dict(part)
        # self.part_name = self.init_part()
        self.init_part()

        # name+level+parent_id:id
        self.category_id_dict = dict()

        # name+level+parent_id:vehicle_code
        self.category_code_dict = dict()

        # cat_id:cat_name
        self.cat_id_name = dict()
        # 是否是新增的类目
        self.is_new = False

    # 取出所有的category
    def init_category(self):
        # db_category level:dict(name)
        level_name = dict()
        category_sql = 'select cat_id,parent_id,cat_name,cat_code,vehicle_code,cat_level,is_leaf from db_category  '
        category_array = self.dao.db.get_data(category_sql)
        for category_data in category_array:
            category__dict = {
                'cat_id': category_data['cat_id'],
                'code': category_data['cat_code'],
                'vehicle_code': category_data['vehicle_code'],
                # 'cat_kind': category_data['cat_kind'],
                'is_leaf': category_data['is_leaf']
            }
            cat_name = category_data['cat_name']
            parent_id = category_data['parent_id']

            key = cat_name + str(parent_id)
            level = int(category_data['cat_level'])
            if level in level_name.keys():
                name_dict = level_name[level]
            else:
                name_dict = dict()
            name_dict[key] = category__dict
            level_name[level] = name_dict

        # 所有分类置为删除状态
        delete_sql = "update db_category set is_deleted = 'Y'"
        self.dao.db.update_data(delete_sql)
        return level_name

    def init_part(self):
        # name_dict = dict()
        # part_sql = "select id,part_name,code,cate_id,sum_code,cat_kind from db_category_part "
        # part_array = self.dao.db.get_data(part_sql)
        # for part_data in part_array:
        #     part_dict = {
        #         'id': part_data['id'],
        #         'code': part_data['code'],
        #         'sum_code': part_data['sum_code'],
        #         'cat_kind': part_data['cat_kind'],
        #         'cate_id': part_data['cate_id']
        #     }
        #     part_name = part_data['part_name']
        #
        #     name_dict[part_name + str(part_data['cate_id'])] = part_dict

        # 所有part置为删除状态
        delete_sql = "update db_category_part set is_deleted = 'Y'"
        self.dao.db.update_data(delete_sql)
        # return name_dict

    # ==============业务处理=========================================

    # 主函数
    def main(self, excle_name):
        # 单个excle处理
        data = self.fileDao.open_excel(excle_name)
        table = data.sheets()[0]
        n_rows = table.nrows  # 行数
        n_cols = table.ncols  # 列数

        print ('行数：%s ,列数：%s' % (n_rows, n_cols))
        self.aliss_name_text = ''
        self.label_text = ''
        # 第二行开始
        for row_num in range(1, n_rows):
            row = table.row_values(row_num)

            excle_vehicle_code = row[1].strip()
            first_name = self.stringUtil.change_cn_en_bracket(row[2].strip())
            first_code = row[3].strip()
            second_name = self.stringUtil.change_cn_en_bracket(row[4].strip())
            second_code = row[5].strip()
            third_name = self.stringUtil.change_cn_en_bracket(row[6].strip())
            third_code = row[7].strip()
            part_name = self.stringUtil.change_cn_en_bracket(row[8].strip())
            part_code = row[9].strip()
            sum_code = row[10].strip()
            self.label_text = row[11].strip().replace("，", ',')
            self.aliss_name_text = row[12].strip().replace("，", ',')
            kind_name = row[13].strip()
            kind_value = self.cat_kind_dict[kind_name]

            if part_name == u'飞轮驱动板':
                print 'this is'

            self.is_new = False
            # first
            first_id = self.first_cate_update(first_name, first_code, kind_value, excle_vehicle_code)
            if self.is_new:
                # 一级、二级、三级、part均为新增
                first_id = str(self.save_category(first_name, first_code, self.cat_kind_not, excle_vehicle_code))
                second_id = str(
                    self.save_category(second_name, second_code, self.cat_kind_not, excle_vehicle_code, first_id, '2'))
                third_id = str(
                    self.save_category(third_name, third_code, kind_value, excle_vehicle_code, second_id, '3'))
                self.save_part(part_name, part_code, excle_vehicle_code, first_id, second_id, third_id, sum_code,
                               kind_value)
                continue
            # second
            key = second_name + str(first_id)
            second_name_dict = dict(self.level_name[2])
            if key not in second_name_dict.keys():
                # 均为新增
                self.is_new = True
                second_id = str(
                    self.save_category(second_name, second_code, self.cat_kind_not, excle_vehicle_code, first_id, '2'))
                third_id = str(
                    self.save_category(third_name, third_code, kind_value, excle_vehicle_code, second_id, '3'))
                self.save_part(part_name, part_code, excle_vehicle_code,first_id, second_id, third_id, sum_code, kind_value)
                continue
            else:
                # 判断是否需要更新
                name_dict = dict(second_name_dict[key])
                second_id = name_dict['cat_id']
                is_leaf = name_dict['is_leaf']
                if int(is_leaf) == 1:
                    # 更新二级分类的叶子节点
                    second_id = self.save_category(second_name, second_code, self.cat_kind_not, excle_vehicle_code,
                                                   first_id,
                                                   '2', '0',
                                                   second_id, True)
                    # 新加三级分类，更新part
                    third_id = str(
                        self.save_category(third_name, third_code, kind_value, excle_vehicle_code, second_id, '3'))
                    self.save_part(part_name, part_code, excle_vehicle_code, first_id, second_id, third_id, sum_code, kind_value,
                                   second_id,
                                   True)
                else:
                    # 更新数据
                    second_id = self.save_category(second_name, second_code, self.cat_kind_not, excle_vehicle_code,
                                                   first_id,
                                                   '2', '0',
                                                   second_id, True)
            # third
            third_id = self.third_cate_do(third_name, third_code, kind_value, excle_vehicle_code, second_id)
            if self.is_new:
                # 三级、part均为新增
                third_id = str(
                    self.save_category(third_name, third_code, kind_value, excle_vehicle_code, second_id, '3'))
                self.save_part(part_name, part_code, excle_vehicle_code, first_id, second_id, third_id, sum_code, kind_value)
                continue

            # part
            self.save_part(part_name, part_code, excle_vehicle_code, first_id, second_id, third_id, sum_code, kind_value,
                           third_id,
                           True)

    # 对 第一分类进行处理
    def first_cate_update(self, first_name, first_code, kind_value, excle_vehicle_code):
        cate_id = 0
        # 一级
        first_name_dict = dict(self.level_name[1])
        key = first_name + '0'

        if key not in first_name_dict.keys():
            # 均为新增
            self.is_new = True
        else:
            # 判断是否需要更新
            name_dict = dict(first_name_dict[key])
            cate_id = name_dict['cat_id']
            # 更新数据
            cate_id = self.save_category(first_name, first_code, self.cat_kind_not, excle_vehicle_code, '0', '1', '0',
                                         cate_id,
                                         True)

        return cate_id

    # 对三级分类处理
    def third_cate_do(self, third_name, third_code, kind_value, excle_vehicle_code, parent_id):
        cate_id = 0
        # 3级
        third_name_dict = dict(self.level_name[3])
        key = third_name + str(parent_id)

        if key not in third_name_dict.keys():
            # 均为新增
            self.is_new = True
        else:
            # 判断是否需要更新
            name_dict = dict(third_name_dict[key])
            cate_id = name_dict['cat_id']
            # 更新数据
            cate_id = self.save_category(third_name, third_code, kind_value, excle_vehicle_code, parent_id, '3', '1',
                                         cate_id,
                                         True)

        return cate_id

    # ===================save=======================
    def save_category(self, cat_name, cat_code, kind, vehicle_code, parent_id='0', level='1', is_leaf='0',
                      cat_id=0, replace=False):
        save_data = {
            'cat_name': cat_name,
            'cat_code': cat_code,
            # 'cat_kind': kind,
            'vehicle_code': vehicle_code,
            'cat_level': level,
            'parent_id': parent_id,
            'is_leaf': is_leaf,
            'is_deleted': 'N'
        }
        if level == '3':
            # 叶子节点
            save_data['is_leaf'] = 1

        save_key = str(cat_name) + str(cat_code) + str(parent_id) + str(level)

        # 若之前更新过一次，则下次就新建一个
        add_list_value = str(cat_name) + str(parent_id) + str(level)

        if replace:
            # 更新
            if save_key not in self.category_id_dict:
                # if add_list_value not in self.category_have_list:
                self.dao.update_temple(self.sql_category_table, save_data, {"cat_id": cat_id})
                self.category_id_dict[save_key] = cat_id
                self.category_code_dict[save_key] = str(vehicle_code)
                # self.category_have_list.append(add_list_value)
                self.cat_id_name[str(cat_id)] = cat_name

                return cat_id

        # 新增
        # name+vehicle+level+parent_id:id
        if save_key in self.category_id_dict:
            cat_id = self.category_id_dict[save_key]
            old_vehicle_code = self.category_code_dict[save_key]
            if old_vehicle_code != str(vehicle_code) and str(vehicle_code) != 'CH':
                # 此分类 为ch
                self.dao.update_temple(self.sql_category_table, {'vehicle_code': 'CH'}, {"cat_id": cat_id})
        else:
            cat_id = self.dao.insert_without_exit(self.sql_category_table, save_data, save_data, 'cat_id')
            self.category_id_dict[save_key] = cat_id
            self.category_code_dict[save_key] = str(vehicle_code)

        self.cat_id_name[str(cat_id)] = cat_name
        return cat_id

    def save_part(self, part_name='', code='', vehicle_code='', first_cate_id='0', second_cate_id='0',
                  third_cate_id='0', sum_code='',
                  cate_kind='',
                  old_cate_id='', replace=False):
        part_data = {
            'part_name': part_name,
            'part_code': code,
            'first_cat_id': first_cate_id,
            'first_cat_name': self.cat_id_name[str(first_cate_id)],
            'second_cat_id': second_cate_id,
            'second_cat_name': self.cat_id_name[str(second_cate_id)],

            'third_cat_id': third_cate_id,
            'third_cat_name': self.cat_id_name[str(third_cate_id)],

            'sum_code': sum_code,
            'cat_kind': cate_kind,
            'is_deleted': 'N',
            'vehicle_code': vehicle_code
        }
        part_exit_data = {
            'part_name': part_name,
            'part_code': code,
            'second_cat_id': second_cate_id,
            'third_cat_id': third_cate_id,
        }
        if self.aliss_name_text != '':
            part_data['aliss_name_text'] = self.aliss_name_text
        if self.label_text != '':
            part_data['label_name_text'] = self.label_text

        have_data = str(part_name) + str(code)

        # if replace:
        #     key = part_name + str(old_cate_id)
        #     if key in self.part_name.keys():
        #         if have_data not in self.part_have_list:
        #             # 第一次出现
        #             part_name_dict = dict(self.part_name[key])
        #             part_id = part_name_dict['id']
        #             # 更新
        #             self.dao.update_temple(self.sql_part_table, part_data, {'id': part_id})
        #             self.part_have_list.append(have_data)
        #
        #             if self.label_text != '':
        #                 label_id = self.label_dict[self.label_text]
        #                 self.save_part_label(label_id, part_id)
        #             return None

        part_id = self.dao.insert_or_update_without_exit(self.sql_part_table, part_data, part_exit_data)

        if self.label_text != '':
            label_id = self.label_dict[self.label_text]
            self.save_part_label(label_id, part_id)

    def save_part_label(self, label_id='', part_id=''):
        save_data = {
            'label_id': label_id,
            'part_id': part_id
        }
        self.dao.insert_without_exit('db_category_part_label', save_data, save_data)


excle_file = r'/Users/zxg/Documents/work/PythonExcle/标准分类体系excle/配件标准模板v106版（碰撞+车类）.xlsx'
test = ChangeCate()
test.main(excle_file)
