# encoding=utf8
import sys

__author__ = 'zxg'

reload(sys)
sys.setdefaultencoding("utf-8")


class StringUtil:
    def __init__(self):
        pass

    @staticmethod
    def change_cn_en_bracket(the_string):
        """

        :rtype : String 中文括号转英文括号
        """
        return the_string.replace("（", "(").replace("）", ")")

    @staticmethod
    def get_true_oe(oe_number):
        return str(oe_number).strip().replace("（", "(").replace("）", ")").replace(".0", "").replace("-", "").replace(
            ".", "").replace(" ", "").replace("*", "").upper()
