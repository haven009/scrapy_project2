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
    base_url = 'http://localhost:8080'
    start_urls = ['https://www.tianyancha.com', ]

    def __init__(self):
        # 使用Firefox浏览器
        self.driver = webdriver.Firefox(executable_path='G:\statisticData\geckodriver.exe')
        # 使用PhantomJS浏览器引擎
        # dcap = dict(webdriver.DesiredCapabilities.PHANTOMJS)  # 设置userAgent
        # dcap[
        #     "phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0"
        # self.driver = webdriver.PhantomJS(
        #     executable_path='I:\\CIIC_Documents\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe',
        #     desired_capabilities=dcap)
        self.driver.maximize_window()  # 设置全屏（最大化屏幕）

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
        print "开始点击"
        # time.sleep(5)
        self.driver.find_element_by_class_name('index_loginin').find_element_by_tag_name('a').click()
        self.set_sleep_time()
        print "进入主页"
        sreach_window = self.driver.current_window_handle
        self.driver.switch_to_window(sreach_window)
        self.driver.find_element_by_id('datagrid-row-r5-2-1').find_element_by_tag_name('a').click()
        self.set_sleep_time()
        page_content = self.driver.page_source  # 获取完整网页内容
        page_selector = Selector(text=page_content)
        td_list = page_selector.css("td[field*=fetchUrl]").extract()  # 提取td内容，由于网页中的标签几乎没有id
        td_list.pop(0)  # 移除第一个
        for td in td_list:
            td_selector = Selector(text=td)
            resume_url = td_selector.css("a::attr(href)").extract_first()
            print self.base_url + resume_url
            yield scrapy.Request(self.base_url + resume_url, self.parse_resume)

        print "=====================循环开始了============================"
        while True:
            # 获取下一页的按钮点击
            pager = self.driver.find_element_by_class_name('datagrid-pager')
            print len(pager.find_elements_by_tag_name('td'))
            pagedown = pager.find_elements_by_tag_name('td')[9].find_element_by_tag_name('a')
            print "标签属性：", str(pagedown.get_attribute("class"))
            # 首先判断按钮是否失效，失效即当前已是最后一页，直接退出
            if re.search(pattern="disabled",
                         string=pagedown.get_attribute("class").encode('unicode-escape').decode('string_escape'),
                         # get_attribute()得到的是unicode类型，需要经过转码得到string类型
                         flags=0) == None:
                print "点击了"
                pagedown.click()
                self.set_sleep_time()
                page_content = self.driver.page_source  # 获取完整网页内容
                selector = Selector(text=page_content)
                td_list = selector.css("td[field*=fetchUrl]").extract()  # 提取td内容，由于网页中的标签几乎没有id
                td_list.pop(0)  # 移除第一个
                print "=================简历个数:", len(td_list), "==============="
                for td in td_list:
                    td_selector = Selector(text=td)
                    resume_url = td_selector.css("a::attr(href)").extract_first()
                    print self.base_url + resume_url
                    yield scrapy.Request(self.base_url + resume_url, self.parse_resume)
            else:
                print "失效了"
                break
        print "=================循环结束了======================"

    def parse_resume(self, response):
        """
        解析简历内容
        :param response:
        :return:
        """
        print "到了"
        zhilianResumeItem = ZhilianResumeItem()
        zhilianResumeItem.setAll()  # 设置item所有属性缺省值为None
        resume_selector = Selector(text=response.text)
        zhilianResumeItem["resume_name"] = resume_selector.css("strong[id=resumeName]::text").extract_first()
        zhilianResumeItem["expect_work"] = resume_selector.css("strong[id=desireIndustry]::text").extract_first()
        zhilianResumeItem["update_date"] = resume_selector.css("strong[id=resumeUpdateTime]::text").extract_first()
        zhilianResumeItem["resume_id"] = \
            resume_selector.css("span.resume-left-tips-id::text").extract_first().split(":")[1]
        zhilianResumeItem["person_info"] = resume_selector.css("div.summary-top").extract_first()
        content = resume_selector.css("div.resume-preview-all").extract()
        for cont in content:
            contselector = Selector(text=cont)
            print contselector.css("h3::text").extract_first().encode('utf8')
            # unicode("求职意向", "utf8")
            if contselector.css("h3::text").extract_first().encode('utf8') == "求职意向":
                print "========找到了=========="
                tr_list = contselector.css("tr").extract()
                for tr in tr_list:
                    tr_selector = Selector(text=tr)
                    if tr_selector.css("td::text").extract_first().encode('utf8').split('：')[0] == "期望工作地区":
                        print tr_selector.css("td::text").extract()[1].encode('utf8')
                        zhilianResumeItem["expect_work_city"] = tr_selector.css("td::text").extract()[1].encode('utf8')
                        continue
                    if tr_selector.css("td::text").extract_first().encode('utf8').split('：')[0] == "期望月薪":
                        print tr_selector.css("td::text").extract()[1].encode('utf8')
                        zhilianResumeItem["expect_sal"] = tr_selector.css("td::text").extract()[1].encode('utf8')
                        continue
                    if tr_selector.css("td::text").extract_first().encode('utf8').split('：')[0] == "目前状况":
                        print tr_selector.css("td::text").extract()[1].encode('utf8')
                        zhilianResumeItem["current_situation"] = tr_selector.css("td::text").extract()[1].encode('utf8')
                        continue
                    if tr_selector.css("td::text").extract_first().encode('utf8').split('：')[0] == "期望工作性质":
                        print tr_selector.css("td::text").extract()[1].encode('utf8')
                        zhilianResumeItem["expect_job_nature"] = tr_selector.css("td::text").extract()[1].encode('utf8')
                        continue
                    if tr_selector.css("td::text").extract_first().encode('utf8').split('：')[0] == "期望从事职业":
                        print tr_selector.css("td::text").extract()[1].encode('utf8')
                        zhilianResumeItem["expect_job"] = tr_selector.css("td::text").extract()[1].encode('utf8')
                        continue
                    if tr_selector.css("td::text").extract_first().encode('utf8').split('：')[0] == "期望从事行业":
                        print tr_selector.css("td::text").extract()[1].encode('utf8')
                        zhilianResumeItem["exxpect_indu"] = tr_selector.css("td::text").extract()[1].encode('utf8')
                        continue
                continue
            if contselector.css("h3::text").extract_first().encode('utf8') == "自我评价":
                self_evalList = contselector.css("div.rd-break::text").extract()
                zhilianResumeItem["self_eval"] = "".join(self_evalList)
                continue
            if contselector.css("h3::text").extract_first().encode('utf8') == "工作经历":
                zhilianResumeItem["work_exper"] = cont
                continue
            if contselector.css("h3::text").extract_first().encode('utf8') == "项目经历":
                zhilianResumeItem["project_exper"] = cont
                continue
            if contselector.css("h3::text").extract_first().encode('utf8') == "教育经历":
                zhilianResumeItem["edu_exper"] = contselector.css("div.resume-preview-dl::text").extract_first()
                continue
            if contselector.css("h3::text").extract_first().encode('utf8') == "在校学习情况":
                study_situationList = contselector.css("div.resume-preview-dl::text").extract()
                zhilianResumeItem["study_situation"] = "".join(study_situationList)
                continue
            if contselector.css("h3::text").extract_first().encode('utf8') == "在校实践经验":
                practical_experList = contselector.css("div.resume-preview-dl::text").extract()
                zhilianResumeItem["practical_exper"] = "".join(practical_experList)
                continue
            if contselector.css("h3::text").extract_first().encode('utf8') == "培训经历":
                zhilianResumeItem["train_exper"] = cont
                continue
            if contselector.css("h3::text").extract_first().encode('utf8') == "证书":
                certificateList = contselector.css("h2::text").extract()
                zhilianResumeItem["certificate"] = "".join(certificateList)
                continue
            if contselector.css("h3::text").extract_first().encode('utf8') == "语言能力":
                languageList = contselector.css("div.resume-preview-dl::text").extract()
                zhilianResumeItem["language"] = "".join(languageList)
                continue
            if contselector.css("h3::text").extract_first().encode('utf8') == "专业技能":
                profess_skillList = contselector.css("div.resume-preview-dl::text").extract()
                zhilianResumeItem["profess_skill"] = "".join(profess_skillList)
                continue
            if contselector.css("h3::text").extract_first().encode('utf8') == "爱好":
                hobbyList = contselector.css("div.resume-preview-dl::text").extract()
                zhilianResumeItem["hobby"] = "".join(hobbyList)
                continue
            if contselector.css("h3::text").extract_first().encode('utf8') == "社会活动":
                social_activList = contselector.css("div.resume-preview-dl::text").extract()
                zhilianResumeItem["social_activ"] = "".join(social_activList)
                continue
            if contselector.css("h3::text").extract_first().encode('utf8') == "获得荣誉":
                achieving_honorList = contselector.css("div.resume-preview-dl::text").extract()
                zhilianResumeItem["achieving_honor"] = "".join(achieving_honorList)
                continue
            if contselector.css("h3::text").extract_first().encode('utf8') == "荣誉":
                honorList = contselector.css("div.resume-preview-dl::text").extract()
                zhilianResumeItem["honor"] = "".join(honorList)
                continue
            if contselector.css("h3::text").extract_first().encode('utf8') == "特殊技能":
                special_skillList = contselector.css("div.resume-preview-dl::text").extract()
                zhilianResumeItem["special_skill"] = "".join(special_skillList)
                continue
            if contselector.css("h3::text").extract_first().encode('utf8') == "特长职业目标":
                special_occu_targetList = contselector.css("div.resume-preview-dl::text").extract()
                zhilianResumeItem["special_occu_target"] = "".join(special_occu_targetList)
                continue
            if contselector.css("h3::text").extract_first().encode('utf8') == "专利":
                patentList = contselector.css("div.resume-preview-dl::text").extract()
                zhilianResumeItem["patent"] = "".join(patentList)
                continue
            if contselector.css("h3::text").extract_first().encode('utf8') == "著作/论文":
                paperList = contselector.css("div.resume-preview-dl::text").extract()
                zhilianResumeItem["paper"] = "".join(paperList)
                continue
            if contselector.css("h3::text").extract_first().encode('utf8') == "推荐信":
                recommendationList = contselector.css("div.resume-preview-dl::text").extract()
                zhilianResumeItem["recommendation"] = "".join(recommendationList)
                continue
            if contselector.css("h3::text").extract_first().encode('utf8') == "专业组织":
                professional_orgList = contselector.css("div.resume-preview-dl::text").extract()
                zhilianResumeItem["professional_org "] = "".join(professional_orgList)
                continue
            if contselector.css("h3::text").extract_first().encode('utf8') == "宗教信仰":
                religionList = contselector.css("div.resume-preview-dl::text").extract()
                zhilianResumeItem["religion "] = "".join(religionList)
                continue
        zhilianResumeItem["page_url"] = get_base_url(response)
        zhilianResumeItem["page_title"] = resume_selector.css("title::text").extract_first()
        zhilianResumeItem["curr_time"] = time.strftime('%Y-%m-%d %X', time.localtime(time.time()))
        yield zhilianResumeItem
