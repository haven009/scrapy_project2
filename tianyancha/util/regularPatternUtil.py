# encoding=utf-8
# author: haven
import re


class RegularPatternUtil(object):
    """
    正则表达式工具类
    """

    def pattern1(self):
        """
        模式1：匹配"\n", " ", "\t", "\r"
        :return:
        """
        return re.compile('["\n", " ", "\t", "\r"]*')  # 用于编译正则表达式并返回对象

    def substituteStrFunc1(self, old_str):
        """
        使用模式1替换字符
        :param old_str:
        :return:
        """
        new_str = re.sub(pattern=self.pattern1(), repl="", string=old_str)
        return new_str
