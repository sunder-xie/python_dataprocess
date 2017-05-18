# encoding=utf8
import sys

__author__ = 'ximeng'

reload(sys)
sys.setdefaultencoding("utf-8")

import os
import xlrd


class FileDao:
    def __init__(self):
        pass

    def get_file_list(self, file_dir, file_list):
        if os.path.isfile(file_dir):
            file_list.append(file_dir.decode('utf-8'))
        elif os.path.isdir(file_dir):
            for s in os.listdir(file_dir):
                # 如果需要忽略某些文件夹，使用以下代码
                # if s == "xxx":
                # continue
                newDir = os.path.join(file_dir, s)
                self.get_file_list(newDir, file_list)
        return file_list

    # 获得当前文件相对路径
    @staticmethod
    def get_now_address():
        path = os.path.abspath(os.path.dirname(sys.argv[0]))
        return path

    @staticmethod
    def save_file(file_dir, save_list=list()):
        file_object = open(file_dir, 'w')
        try:
            file_object.writelines(",".join(save_list))
        finally:
            file_object.close()

    # ============excel==========================

    # 打开excle
    @staticmethod
    def open_excel(file_name):
        try:
            data = xlrd.open_workbook(file_name)
            return data
        except Exception, e:
            print str(e)
