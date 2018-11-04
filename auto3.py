# coding=utf8
# 面向对象
import re

import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver


class Wnku(object):
    options = None
    driver = None
    html = None
    soup = None

    def __init__(self, url, wait_time=10):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--headless")  # 隐藏窗口,为什么每次的成功率不定呢，因为等待加载的时间问题
        self.options.add_argument('user-agent="Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19"')  # 以手机端打开
        self.driver = webdriver.Chrome(chrome_options=self.options)
        self.driver.implicitly_wait(wait_time)  # seconds设置隐式等待
        self.driver.get(url)

        self.click()
        self.get_html()

    # def __del__(self):
    #     self.driver.quit()  # 关闭窗口，其实也不用了

    # 模拟点击加载，获取大页面
    def click(self):
        # foldpagewg-text
        element = self.driver.find_element_by_class_name('foldpagewg-text')
        self.driver.execute_script("arguments[0].click();", element)
        # pagerwg-button*3 差不多1+3次加载后一片文章就可以加载完成了，不确定，注意！！！
        for i in range(3):
            element3 = self.driver.find_element_by_class_name('pagerwg-button')
            self.driver.execute_script("arguments[0].click();", element3)

    # 获取源码
    def get_html(self):
        self.html = self.driver.page_source
        self.soup = BeautifulSoup(self.html, 'lxml')  # 使用lxml格式解析网页

    # 抽取文字p
    def parse_txt(self):
        texts = []  # 用于存储所有文档内容
        # soup = BeautifulSoup(self.html, 'lxml')
        title = self.soup.find('div', {"class": 'doc-title'}).get_text().encode('utf-8').replace('\n', '').replace(' ', '')  # 获取标题
        texts.append(title)
        pages = self.soup.find_all('div', {"data-page": re.compile(r'\d+')})  # 获取所有页内容
        # print len(pages),  # 13页
        for page in pages:
            lines = page.find_all('p')  # 获取每页内所有段内容,文库中内容肯定在p中
            # print len(lines)
            for line in lines:  # 获取每段内容
                txt = line.get_text().encode('utf-8').strip()
                texts.append(txt)

        world = '\n'.join(texts)  # 以换行符连接
        return title, world, len(pages)

    # 抽取图片
    def parse_img(self):
        imgs = self.soup.find_all('p', {"class": 'rtcscls5_r_30 noIndent'})  # 这些都应该根据文档调整
        # print len(imgs)
        for img in imgs:
            src = img.find('img')['data-loading-src']
            # print src
            r = requests.get(src, stream=True)
            image_name = imgs.index(img)  # 随便造个图片名吧
            with open('./img/%s.jpg' % image_name, 'wb') as f:
                for chunk in r.iter_content(chunk_size=128):
                    f.write(chunk)
            print "saved %s,jpg " % image_name


if __name__ == "__main__":
    start = time.clock()
    # url = "https://wk.baidu.com/view/aa31a84bcf84b9d528ea7a2c?pcf=2&pcf=2&pcf=2&pcf=2&pcf=2&pcf=2&pcf=2"
    url = "https://wenku.baidu.com/view/b5ef6c6259fafab069dc5022aaea998fcc2240ac.html"
    w = Wnku(url)

    w.parse_img()
    title, world, page_len = w.parse_txt()
    print ("title: %s \n world: %s \n world num: %d \n page_len: %d" % (title, world, len(world) / 3, page_len))

    def write_to_file(file_name, str):
        with open(file_name.decode('utf-8'), "wb") as f:
            f.write(str)
        f.close()

    write_to_file("./res/" + title + "2.txt", world)
    end = time.clock()
    print "耗时: ", end - start

    # del w  # 调用析构方法
