# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TianyanchaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    comp_name = scrapy.Field()  # 企业名称
    phone_num = scrapy.Field()  # 电话
    comp_url = scrapy.Field()  # 网址
    mail = scrapy.Field()  # 邮箱
    address = scrapy.Field()  # 地址
    legal_person = scrapy.Field()  # 法人代表
    register_capital = scrapy.Field()  # 注册资金
    register_time = scrapy.Field()  # 注册时间
    operate_state = scrapy.Field()  # 经营状况
    register_num = scrapy.Field()  # 工商注册号
    credit_code = scrapy.Field()  # 统一信用代码
    indu = scrapy.Field()  # 行业
    approve_date = scrapy.Field()  # 核准日期
    org_code = scrapy.Field()  # 组织机构代码
    comp_type = scrapy.Field()  # 企业类型
    operat_date = scrapy.Field()  # 经营期限
    register_department = scrapy.Field()  # 登机机关
    register_address = scrapy.Field()  # 注册地址
    business_scope = scrapy.Field()  # 经营范围
    page_url = scrapy.Field()  # 采集页面网址
    page_title = scrapy.Field()  # 采集页面标题
    curr_time = scrapy.Field()  # 采集页面时间

    def setAll(self):
        """
        设置item属性缺省值
        :return:
        """
        self["comp_name"] = None
        self["phone_num"] = None
        self["comp_url"] = None
        self["mail"] = None
        self["address"] = None
        self["legal_person"] = None
        self["register_capital"] = None
        self["register_time"] = None
        self["operate_state"] = None
        self["register_num"] = None
        self["credit_code"] = None
        self["indu"] = None
        self["approve_date"] = None
        self["org_code"] = None
        self["comp_type"] = None
        self["operat_date"] = None
        self["register_department"] = None
        self["register_address"] = None
        self["business_scope"] = None
        self["page_url"] = None
        self["page_title"] = None
        self["curr_time"] = None
