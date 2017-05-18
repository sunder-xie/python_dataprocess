# encoding=utf-8
# 分类的导入，匹配对应关系的主
__author__ = 'ximeng'

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from excle.Cate import CatePython, CatePythonSpecial, CateMatch, CateLCVRelation, CateToolRelation
from util import CrawlDao
dao = CrawlDao.CrawlDao()

sql_table = 'db_category'
# 查询库中最大的一个id
sql_string = 'select cat_id from '+sql_table+' where 1=1 order by cat_id desc limit 1'
result = dao.db.get_data(sql_string)
# 初始数据准备final_id = 1233
final_id = 0
# if result:
#     final_id = str(result[0]['cat_id'])
print '==========================final_id:%s===========' % final_id
# final_id = str(1247)
# 除油品保养件以外的数据excle
main_excle = r'D:\PythonExcle\cate\0630\main.xls'
# 油品保养件的数据
youping_excle = r'D:\PythonExcle\cate\0630\youping.xls'
# 人工对应的数据
rengong_excle = r'D:\PythonExcle\cate\0630\rengong.xlsx'
# update 操作存入的text路径
file_name = r'D:\PythonExcle\cate\0630\updateCate.txt'

# X类的一级目录名称，做新老映射
lcv_new_parent_name = '商用车'
lcv_old__parent_name = '商用车'

# tool_new_parent_name = '设备工具'
tool_old__parent_name = '汽保产品'

# 导入除油品保养件以外的数据
cate = CatePython.Cate()
cate.main(main_excle, str(final_id), file_name)
# 导入油品保养件的数据
cateSpecial = CatePythonSpecial.CateSpecial()
cateSpecial.main(youping_excle, final_id, file_name)
# 人工对应上的映射关系存入数据库
catMatch = CateMatch.CateMatch()
catMatch.main(rengong_excle, final_id)
# 商用车和设备工具的映射关系存表
lcv_relation = CateLCVRelation.CateLCVRelation()
lcv_relation.main(final_id, lcv_old__parent_name, lcv_new_parent_name)

cateTool = CateToolRelation.CateTool()
cateTool.main(final_id, tool_old__parent_name)
