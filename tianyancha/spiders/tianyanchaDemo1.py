# encoding=utf-8
# author: haven
import random
import uuid
import re
import scrapy
import codecs
import json
import sys
import time
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider
from scrapy.utils.project import get_project_settings
from scrapy.utils.response import get_base_url
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.proxy import ProxyType
from selenium.webdriver.common.action_chains import *
# from selenium.webdriver import ActionChains
from tianyancha.items import TianyanchaItem
from tianyancha.settings import PHONE1, PASSWORD1
from tianyancha.util.regularPatternUtil import RegularPatternUtil
from zhilian_resume.items import ZhilianResumeItem
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from lib2to3.pgen2.tokenize import Ignore

reload(sys)
sys.setdefaultencoding('utf-8')
from scrapy.selector import Selector


class TianYanChaSpider(scrapy.Spider):
    """
    天眼查爬虫
    """
    name = "tianyancha"
    # start_urls = ['https://www.tianyancha.com/company/2943946021', ]
    # start_url = 'file:///C:/Users/haven/Desktop/tiatancha.html'
    login_url = 'https://bj.tianyancha.com/login'
    company_urls = ['https://www.tianyancha.com/company/2943946021',
                    'https://www.tianyancha.com/company/3793676',
                    'https://www.tianyancha.com/company/593038884',
                    'https://www.tianyancha.com/company/23303972',
                    'https://www.tianyancha.com/company/22822',
                    'https://www.tianyancha.com/company/139573020',
                    'https://www.tianyancha.com/company/711249800',
                    'https://www.tianyancha.com/company/1341875964',
                    'https://www.tianyancha.com/company/12321232',
                    'https://www.tianyancha.com/company/22991854'
                    ]

    def start_requests(self):
        yield scrapy.Request(self.login_url, callback=self.parse)

    def __init__(self):
        # 使用Firefox浏览器
        # self.driver = webdriver.Firefox(executable_path='I:\CIIC_Documents\geckodriver.exe')
        # self.driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe')
        # 使用PhantomJS浏览器引擎
        # proxy = Proxy(
        #     {
        #         'proxyType': ProxyType.MANUAL,
        #         'httpProxy': 'ip:port'  # 代理ip和端口
        #     }
        # )
        # # 新建一个“期望技能”，哈哈
        # desired_capabilities = webdriver.DesiredCapabilities.PHANTOMJS.copy()
        # # 把代理ip加入到技能中
        # proxy.add_to_capabilities(desired_capabilities)

        dcap = dict(webdriver.DesiredCapabilities.PHANTOMJS)  # 设置userAgent
        dcap[
            "phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0"
        self.driver = webdriver.PhantomJS(
            executable_path='I:\\CIIC_Documents\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe',
            desired_capabilities=dcap)

        # proxy = webdriver.Proxy()
        # proxy.proxy_type = ProxyType.MANUAL
        # proxy.http_proxy = '101.205.15.41:808'
        # # 将代理设置添加到webdriver.DesiredCapabilities.PHANTOMJS中
        # proxy.add_to_capabilities(webdriver.DesiredCapabilities.PHANTOMJS)
        # self.driver.start_session(webdriver.DesiredCapabilities.PHANTOMJS)
        self.driver.maximize_window()  # 设置全屏（最大化屏幕
        # self.driver.get('http://httpbin.org/ip')

    def set_sleep_time(self):
        """
        设置加载超时最大时长（单位：s）
        :return:
        """
        self.driver.implicitly_wait(30)  # 识别对象的智能等待时间
        self.driver.set_page_load_timeout(30)  # 设置页面完全加载的超时时间，完全加载即完全渲染完成，同步和异步脚本都执行完
        self.driver.set_script_timeout(30)  # 设置异步脚本的超时时间

    def parse(self, response):
        """
        解析页面内容
        :param response:
        :return:
        """
        print "你好：", response.url
        self.driver.get(response.url)
        self.set_sleep_time()
        # print self.driver.page_source
        self.driver.find_element_by_class_name('mobile_box').find_element_by_class_name('contactphone').send_keys(
            PHONE1)
        self.driver.find_element_by_class_name('mobile_box').find_element_by_class_name('contactword').send_keys(
            PASSWORD1)
        self.driver.find_element_by_class_name('mobile_box').find_element_by_class_name('login_btn').click()
        self.set_sleep_time()
        time.sleep(5)
        # print self.driver.page_source
        print "准备进入解析。。。。。"
        cookies = self.driver.get_cookies()
        print cookies
        for company_url in self.company_urls:
            print company_url
            seconds = random.randint(1, 5)
            time.sleep(seconds)
            print "停顿", seconds, "秒..............."
            yield scrapy.Request(url=company_url, cookies=cookies, callback=self.parse_company)
        print "结束。。。。。。。。。。。"
        # chain = ActionChains(self.driver)
        # implement = self.driver.find_element_by_class_name('mr15').find_element_by_class_name('new-c3')
        # chain.move_to_element(implement).perform()

        # chain = ActionChains(self.driver)  # 建立动作链
        # chain.move_to_element(
        #     self.driver.find_element_by_class_name('mr15').find_element_by_class_name('new-c3')).perform()
        # for divindex in self.driver.find_element_by_class_name('mr15').find_elements_by_class_name(
        #         'border-shadow-hover'):
        #     # print aindex.get_attribute('text')
        #     if divindex.find_element_by_tag_name('a').get_attribute('text') == '注册时间降序':
        #         print '找到了'
        #         divindex.find_element_by_tag_name('a').click()
        #         # print self.driver.page_source
        #         self.set_sleep_time()
        #         break

        # aa_button = self.driver.find_element_by_class_name('col-xs-10').find_element_by_tag_name('a')
        # print "准备进入解析。。。。。"
        # yield scrapy.Request(url="https://www.tianyancha.com/company/2943946021", callback=self.parse_company)
        # while True:
        #     for company in self.driver.find_elements_by_class_name('f18'):
        #         a_button = company.find_element_by_tag_name('a')
        #         yield scrapy.Request(url=a_button.get_attribute('href'), callback=self.parse_company)
        #         # a_button.click()
        #         # self.driver.switch_to_window(self.driver.current_window_handle)
        #         # print self.driver.page_source
        #         break
        #     break

    def parse_company(self, response):
        """
        解析网页内容
        :param response:
        :return:
        """
        print "开始解析网页 ... ... ... ..."
        print response.url
        # self.driver.get(response.url)
        self.set_sleep_time()
        # time.sleep(10)
        regularPatternUtil = RegularPatternUtil()  # 正则表达式工具类
        # print self.driver.page_source
        # phone = self.driver.find_element_by_class_name('mobile_box').find_element_by_class_name('contactphone')
        # print phone.get_attribute('class')
        # phone.send_keys("13021093200")
        # password = self.driver.find_element_by_class_name('mobile_box').find_element_by_class_name('contactword')
        # password.send_keys("weizeng1993")
        # self.driver.find_element_by_class_name('mobile_box').find_element_by_class_name('login_btn').click()
        # # self.set_sleep_time()
        # print "进入主页"
        # sreach_window = self.driver.current_window_handle
        # self.driver.switch_to_window(sreach_window)
        tianyanchaItem = TianyanchaItem()
        # self.selector = Selector(text=self.driver.page_source)
        selector = Selector(text=response.text)
        # print response.text
        # print self.driver.page_source
        tianyanchaItem['comp_name'] = regularPatternUtil.substituteStrFunc1(selector.css(
            "div.companyTitleBox55 div.company_header_width span.vertival-middle::text").extract_first())  # 提取企业名称
        companyTitle = selector.css(
            "div.companyTitleBox55 div.company_header_width div.new-c3 div.in-block span::text").extract()
        tianyanchaItem['phone_num'] = regularPatternUtil.substituteStrFunc1(old_str=companyTitle[1])  # 提取电话
        tianyanchaItem['mail'] = regularPatternUtil.substituteStrFunc1(old_str=companyTitle[3])  # 邮箱
        if len(companyTitle) != 8:
            tianyanchaItem['comp_url'] = regularPatternUtil.substituteStrFunc1(old_str=selector.css(
                "div.companyTitleBox55 div.company_header_width div.new-c3 div.in-block a::text").extract_first())  # 提取网址
            tianyanchaItem['address'] = regularPatternUtil.substituteStrFunc1(old_str=companyTitle[6])  # 地址
        else:
            tianyanchaItem['comp_url'] = regularPatternUtil.substituteStrFunc1(old_str=companyTitle[5])  # 提取网址
            tianyanchaItem['address'] = regularPatternUtil.substituteStrFunc1(old_str=companyTitle[7])  # 地址
        tianyanchaItem['legal_person'] = regularPatternUtil.substituteStrFunc1(old_str=selector.css(
            "div.company-human-box div.human-top div.overflow-width a::text").extract_first())  # 提取法人代表
        register_info = selector.css("div.baseInfo_model2017 div.pb10 div::text").extract()
        tianyanchaItem['register_capital'] = regularPatternUtil.substituteStrFunc1(old_str=register_info[0])  # 提取注册资金
        tianyanchaItem['register_time'] = regularPatternUtil.substituteStrFunc1(old_str=register_info[1])  # 提取注册时间
        tianyanchaItem['operate_state'] = regularPatternUtil.substituteStrFunc1(old_str=selector.css(
            "div.baseInfo_model2017 div.pt10 div.baseinfo-module-content-value::text").extract_first())  # 提取企业状态
        company_info = selector.css("div.base2017 div.c8 span::text").extract()
        tianyanchaItem['register_num'] = regularPatternUtil.substituteStrFunc1(old_str=company_info[0])  # 提取工商注册号
        tianyanchaItem['org_code'] = regularPatternUtil.substituteStrFunc1(old_str=company_info[1])  # 提取组织机构代码
        tianyanchaItem['credit_code'] = regularPatternUtil.substituteStrFunc1(old_str=company_info[2])  # 提取统一信用代码
        tianyanchaItem['comp_type'] = regularPatternUtil.substituteStrFunc1(old_str=company_info[3])  # 提取企业类型
        tianyanchaItem['taxpayer_iden_num'] = regularPatternUtil.substituteStrFunc1(old_str=company_info[4])  # 提取纳税人识别号
        tianyanchaItem['indu'] = regularPatternUtil.substituteStrFunc1(old_str=company_info[5])  # 提取行业
        tianyanchaItem['operat_date'] = regularPatternUtil.substituteStrFunc1(old_str=company_info[6])  # 提取经营期限
        tianyanchaItem['approve_date'] = regularPatternUtil.substituteStrFunc1(old_str=company_info[7])  # 提取核准日期
        tianyanchaItem['register_department'] = regularPatternUtil.substituteStrFunc1(old_str=company_info[8])  # 提取登机机关
        tianyanchaItem['register_address'] = regularPatternUtil.substituteStrFunc1(old_str=company_info[9])  # 提取注册地址
        tianyanchaItem['business_scope'] = regularPatternUtil.substituteStrFunc1(old_str=selector.css(
            "div.base2017 div.c8 span.js-full-container::text").extract_first())  # 提取经营范围
        tianyanchaItem['page_url'] = response.url  # 提取采集页面网址
        tianyanchaItem['page_title'] = regularPatternUtil.substituteStrFunc1(
            old_str=selector.css("title::text").extract_first())  # 提取采集页面标题
        tianyanchaItem['curr_time'] = time.strftime('%Y-%m-%d %X', time.localtime(time.time()))  # 存储采集页面时间
        UUID = str(uuid.uuid1())
        print UUID
        tianyanchaItem['tianyancha_uuid'] = UUID  # 设置UUID
        yield tianyanchaItem
