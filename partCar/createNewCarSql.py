# encoding=utf-8
# 2016-08-03 生成新品牌的sql
__author__ = 'zxg'

new_brand_dict = {"帝豪": "dhcar",
                  "全球鹰": "quanqiuying",
                  "英伦": "yinglun",
                  "菲亚特": "fiatauto",
                  "路虎": "landrover",
                  "三菱": "mitsubishi",
                  "沃尔沃": "volvocars",
                  "斯巴鲁": "subaru"}

new_brand_sql = "CREATE TABLE `db_monkey_part_liyang_relation_BRANDVALUE` ( " \
                "`id` int(11) unsigned NOT NULL AUTO_INCREMENT," \
  "`create_user_id` int(11) NOT NULL DEFAULT '0' COMMENT '创建者'," \
  "`update_user_id` int(11) NOT NULL DEFAULT '0' COMMENT '更新者'," \
  "`gmt_modified` datetime NOT NULL DEFAULT '1970-01-01 12:00:00' COMMENT '记录修改时间,如果时间是1970年则表示纪录未修改'," \
  "`gmt_create` datetime NOT NULL DEFAULT '1970-01-01 12:00:00' COMMENT '记录创建时间'," \
  "`goods_id` varchar(100) NOT NULL DEFAULT '0' COMMENT 'part_goods表uuid'," \
  "`pic_id` varchar(100) NOT NULL DEFAULT '' COMMENT 'part pic 的表'," \
  "`subjoin_id` varchar(100) NOT NULL DEFAULT '' COMMENT 'part subjoin 表的uuid'," \
  "`liyang_id` varchar(255) NOT NULL DEFAULT '' COMMENT '力洋id'," \
  "`part_liyang_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT 'db_monkey_part_liyang_base 的主键（已整理的配件库 力洋车型）'," \
  "PRIMARY KEY (`id`)," \
  "UNIQUE KEY `uk_gid_pid_lid` (`goods_id`,`liyang_id`,`pic_id`) USING BTREE" \
") ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=COMPACT COMMENT='BRANDNAME－数据配件力洋关系表'" \

create_list = list()
insert_list = list()
for brand_name,brand_value in new_brand_dict.iteritems():
    create_list.append(new_brand_sql.replace("BRANDVALUE",brand_value).replace("BRANDNAME",brand_name))
    insert_list.append("(now(),now(),'"+brand_name+"','db_monkey_part_liyang_relation_"+brand_value+"')")



create_file_object = open(r'/Users/zxg/Desktop/partBrandCar/1.create.sql', 'w')
insert_file_object = open(r'/Users/zxg/Desktop/partBrandCar/2.insert.sql', 'w')

try:
    create_file_object.writelines(";\n".join(create_list))

    insert_file_object.writelines("INSERT into db_monkey_part_liyang_table_relation(gmt_modified,gmt_create,car_brand_name,liyang_table) VALUES ")
    insert_file_object.writelines(",\n".join(insert_list))
finally:
    create_file_object.close()
    insert_file_object.close()