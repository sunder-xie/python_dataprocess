# encoding=utf-8
# 查询出所有excel中，相同的oe 不同的 标准零件名称
__author__ = 'zxg'
import sys

reload(sys)
sys.setdefaultencoding("utf-8")
from util import CrawlDao, FileUtil


class Choose:
    def __init__(self):
        self.dao = CrawlDao.CrawlDao("test", "local")

        # 标准零件编号 写入 dict 中 part_code:part_name
        self.part_dict = dict()
        part_array = self.dao.db.get_data(
            "SELECT part_name,sum_code FROM db_category_part WHERE is_deleted = 'N'")
        for part_data in part_array:
            self.part_dict[str(part_data['sum_code'])] = str(part_data['part_name'])

    def main(self):
        oe_array = self.dao.db.get_data("select oe_trim from dif group by oe_trim")
        for oe_data in oe_array:
            oe_trim_num = str(oe_data['oe_trim'])

            # 公共的前缀
            new_start_code = None
            # 是否是新增的
            is_need_added = 0
            # 此oe码下面 的part 是否均为 仅左右上下的区别
            is_ok = True

            part_array = self.dao.db.get_data(
                "select part_code,part_name from dif where oe_trim = '" + oe_trim_num + "'")
            for part_data in part_array:
                # part_name = str(part_data['part_name'])
                part_code = str(part_data['part_code'])

                if new_start_code is None:
                    new_start_code = part_code[:-1]
                if new_start_code not in part_code:
                    is_ok = False
                    break

            if is_ok:
                new_part_name = str(part_array[0]['part_name']).replace("（", "(").split("(")[0]
                new_part_code = new_start_code + "0"
                if new_part_code in self.part_dict.keys():
                    new_part_name = self.part_dict[new_part_code]
                else:
                    is_need_added = 1

                self.update_dif(oe_trim_num,new_part_name,new_part_code,is_need_added)

    def update_dif(self, oe_trim, new_part_name, new_part_code, is_need_added):
        update_dict = {
            "new_part_name": new_part_name,
            "new_part_code": new_part_code,
            "is_need_add": is_need_added,
        }

        self.dao.update_temple("dif", update_dict, {"oe_trim": oe_trim})


chooseDO = Choose()
chooseDO.main()