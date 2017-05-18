# encoding=utf-8
# 每月新增的三级分类数据
# 11.09
import datetime
import os

__author__ = 'zxg'

from util import CrawlDao, FileUtil


class Monkey_New_Cat:
    def __init__(self):
        self.monkey_dao = CrawlDao.CrawlDao("modeldatas", "local")
        self.file_dao = FileUtil.FileDao()

        # 最大的分类 id
        self.max_cat_id = 0
        # cat_id:cat_code
        self.cat_id_dict = dict()
        # cat_name+"_"+cat_pid: {cat_id,cat_code}
        self.cat_name_pid_dict = dict()
        # cat_pid:cat_max_code
        self.cat_pid_dict = dict()

        # third_cat_id:List<part>
        self.part_dict = dict()

        self.init_category()
        self.init_part()

        # === 保存===
        self.save_cat_list = list()
        self.save_part_list = list()

    # 初始化分类
    def init_category(self):
        cat_sql = "SELECT cat_id,cat_name,parent_id,cat_code from db_category where is_deleted = 'N'"
        cat_array = self.monkey_dao.db.get_data(cat_sql)
        for cat_data in cat_array:
            cat_id = str(cat_data['cat_id'])
            cat_name = str(cat_data['cat_name'])
            parent_id = str(cat_data['parent_id'])
            cat_code = str(cat_data['cat_code'])

            if int(cat_id) > self.max_cat_id:
                self.max_cat_id = int(cat_id)
            self.cat_id_dict[cat_id] = cat_code
            self.cat_name_pid_dict[cat_name + "_" + parent_id] = {'cat_id': cat_id, 'cat_code': cat_code}

            if parent_id in self.cat_pid_dict.keys():
                max_code = self.cat_pid_dict[parent_id]
                if int(max_code) < int(cat_code):
                    self.cat_pid_dict[parent_id] = cat_code
            else:
                self.cat_pid_dict[parent_id] = cat_code

    # 初始化 part
    def init_part(self):
        part_sql = "select part_name,part_code,third_cat_id from db_category_part where is_deleted = 'N'"
        part_array = self.monkey_dao.db.get_data(part_sql)
        for part_data in part_array:
            third_cat_id = str(part_data['third_cat_id'])
            if third_cat_id in self.part_dict.keys():
                part_list = list(self.part_dict[third_cat_id])
            else:
                part_list = list()
            part_list.append(part_data)
            self.part_dict[third_cat_id] = part_list

    # ============ private ============
    # 新增cat_code
    def cat_code_add(self, pid):
        max_code = self.cat_pid_dict[pid]

        the_code = str(int(max_code) + 1)

        while len(the_code) < len(max_code):
            the_code = "0" + the_code

        self.cat_pid_dict[pid] = the_code

        return the_code

    def get_cat_id(self, cat_name, pid, cat_level):
        the_key = cat_name + "_" + pid
        if the_key in self.cat_name_pid_dict.keys():
            cat_data = self.cat_name_pid_dict[the_key]
        else:
            self.max_cat_id += 1

            cat_id = str(self.max_cat_id)
            cat_code = self.cat_code_add(pid)
            cat_data = {'cat_id': cat_id, 'cat_code': cat_code}
            self.cat_name_pid_dict[the_key] = cat_data

            # 保存数据
            save_cat = {'cat_id': cat_id, 'cat_name': cat_name, 'parent_id': pid, 'cat_level': cat_level,
                        'cat_code': cat_code, 'vehicle_code': 'C'}
            if cat_level == '3':
                save_cat['is_leaf'] = 1
            self.save_cat_list.append(save_cat)

        return cat_data

    def get_need_part_code(self, part_name, third_cat_name):
        # 同样的名称
        part_array = part_name.split("(")
        if part_array[0] == third_cat_name:
            if len(part_array) == 1:
                return "00"
            part_remark = part_array[1]
            if "左)" in part_remark or "内)" in part_remark or "前)" in part_remark or "上)" in part_remark \
                    or "进气)" in part_remark or "进)" in part_remark or "正极)" in part_remark or "上段)" in part_remark:
                return "01"
            if "右)" in part_remark or "外)" in part_remark or "后)" in part_remark or "下)" in part_remark \
                    or "排气)" in part_remark or "出)" in part_remark or "负极)" in part_remark or "下段)" in part_remark:
                return "02"

        return ""

    def console_part(self, part_name, cat_data):
        third_cat_id = cat_data['third_cat_id']

        # 是否需要新增code，若true，code 叠加，若false，则用生成的code
        is_need_add_code = False
        max_part_code = 0
        need_part_code = self.get_need_part_code(part_name, cat_data['third_cat_name'])
        part_list = list()
        if third_cat_id in self.part_dict.keys():
            part_list = self.part_dict[third_cat_id]
            for part_data in part_list:
                part_code = str(part_data['part_code'])
                sql_part_name = str(part_data['part_name'])
                if part_name == sql_part_name:
                    # 已存在，无需添加，返回
                    print "error:the part_name has exist.part_name:%s,third_cat_id:%s" % (part_name, third_cat_id)
                    return False
                if int(max_part_code) < int(part_code):
                    max_part_code = int(part_code)

                if need_part_code == part_code:
                    # 已经存在
                    is_need_add_code = True

        # 需要在最大的code 上 +1 生成新的code，且code 不能为 00 01 02
        if need_part_code == "" or is_need_add_code:
            need_part_code = str(int(max_part_code) + 1)
            if int(need_part_code) < 3:
                need_part_code = "03"
            if len(need_part_code) == 1:
                need_part_code = "0" + need_part_code

        save_part = dict(cat_data)
        save_part['part_name'] = part_name
        save_part['part_code'] = need_part_code
        save_part['sum_code'] = cat_data['first_cat_code'] + cat_data['second_cat_code'] + cat_data[
            'third_cat_code'] + need_part_code
        save_part['cat_kind'] = '1'
        save_part['vehicle_code'] = 'C'

        save_part.pop('first_cat_code')
        save_part.pop('second_cat_code')
        save_part.pop('third_cat_code')
        self.save_part_list.append(save_part)

        part_list.append(save_part)
        self.part_dict[third_cat_id] = part_list

    def read_from_excel(self, excel_address):
        # 单个excle处理
        data = self.file_dao.open_excel(excel_address)
        #
        table = data.sheets()[0]

        n_rows = table.nrows  # 行数
        n_cols = table.ncols  # 列数
        print ('行数：%s ,列数：%s' % (n_rows, n_cols))

        for rownum in range(1, n_rows):
            row = table.row_values(rownum)
            first_cat_name = str(row[0]).strip()
            second_cat_name = str(row[1]).strip()
            third_cat_name = str(row[2]).strip()
            part_name = str(row[3]).strip().replace("（", "(").replace("）", ")")

            first_cat_data = self.get_cat_id(first_cat_name, "0", "1")
            first_cat_id = first_cat_data['cat_id']
            first_cat_code = first_cat_data['cat_code']

            second_cat_data = self.get_cat_id(second_cat_name, first_cat_id, "2")
            second_cat_id = second_cat_data['cat_id']
            second_cat_code = second_cat_data['cat_code']

            third_cat_data = self.get_cat_id(third_cat_name, second_cat_id, "3")
            third_cat_id = third_cat_data['cat_id']
            third_cat_code = third_cat_data['cat_code']

            cat_data = {
                'first_cat_id': first_cat_id, 'first_cat_code': first_cat_code, 'first_cat_name': first_cat_name,
                'second_cat_id': second_cat_id, 'second_cat_code': second_cat_code, 'second_cat_name': second_cat_name,
                'third_cat_id': third_cat_id, 'third_cat_code': third_cat_code, 'third_cat_name': third_cat_name,
            }
            self.console_part(part_name, cat_data)

    def create_sql(self):

        save_file_address = os.getcwd() + '/monkey_sql/'
        if os.path.exists(save_file_address):
            pass
        else:
            os.mkdir(save_file_address)

        save_file_address = save_file_address + datetime.datetime.now().strftime("%Y-%m-%d-%H")+".sql"

        sql_list = list()
        for cat_data in self.save_cat_list:
            cat_sql = self.monkey_dao.get_insert_sql('db_category', cat_data)
            print cat_sql
            sql_list.append(cat_sql)

        for part_data in self.save_part_list:
            part_sql = self.monkey_dao.get_insert_sql('db_category_part', part_data)
            print part_sql
            sql_list.append(part_sql)

        save_obj = open(save_file_address, 'w')
        try:
            save_obj.writelines(";\n".join(sql_list))
        finally:
            save_obj.close()

    def main_console(self, excel_address):
        print "======start====="
        # 处理数据
        self.read_from_excel(excel_address)
        # 生存sql
        self.create_sql()
        print "======end====="


excel_address = r'/Users/huangzhangting/Desktop/16.12.26.xls'
monkey_New_Cat = Monkey_New_Cat()
monkey_New_Cat.main_console(excel_address)
