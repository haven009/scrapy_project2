# encoding=utf-8
# author: haven

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
from tianyancha.settings import PHONE1, PASSWORD1
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
    start_urls = ['https://www.tianyancha.com/search', ]

    def __init__(self):
        # 使用Firefox浏览器
        # self.driver = webdriver.Firefox(executable_path='G:\statisticData\geckodriver.exe')
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
        self.driver.start_session(webdriver.DesiredCapabilities.PHANTOMJS)
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
        print "你好：", get_base_url(response)
        self.driver.get(response.url)
        self.set_sleep_time()
        print self.driver.page_source
        self.driver.find_element_by_class_name('mobile_box').find_element_by_class_name('contactphone').send_keys(
            PHONE1)
        self.driver.find_element_by_class_name('mobile_box').find_element_by_class_name('contactword').send_keys(
            PASSWORD1)
        self.driver.find_element_by_class_name('mobile_box').find_element_by_class_name('login_btn').click()
        # print self.driver.page_source
        # chain = ActionChains(self.driver)
        # implement = self.driver.find_element_by_class_name('mr15').find_element_by_class_name('new-c3')
        # chain.move_to_element(implement).perform()
        chain = ActionChains(self.driver)  # 建立动作链
        chain.move_to_element(
            self.driver.find_element_by_class_name('mr15').find_element_by_class_name('new-c3')).perform()
        for divindex in self.driver.find_element_by_class_name('mr15').find_elements_by_class_name(
                'border-shadow-hover'):
            # print aindex.get_attribute('text')
            if divindex.find_element_by_tag_name('a').get_attribute('text') == '注册时间降序':
                print '找到了'
                divindex.find_element_by_tag_name('a').click()
                # print self.driver.page_source
                self.set_sleep_time()
                break
        while True:
            for company in self.driver.find_elements_by_class_name('f18'):
                company.find_element_by_tag_name('a').click()
                self.driver.switch_to_window(self.driver.current_window_handle)
                # print self.driver.page_source
                break
            break
