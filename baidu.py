import requests
import json
import time
import pymysql
from selenium import webdriver
import re
from selenium.webdriver import Chrome, ChromeOptions

from lxml import etree
import csv
def get_conn():
    """
    :return: 连接，游标l
    """
    # 创建连接
    conn = pymysql.connect(host="localhost",
                           user="root",
                           password="QJM7146689",
                           db="yiqin",
                           charset="utf8")
    # 创建游标
    cursor = conn.cursor()  # 执行完毕返回的结果集默认以元组显示
    return conn, cursor


def close_conn(conn, cursor):
    if cursor:
        cursor.close()
    if conn:
        conn.close()

def get_baidu_hot():
    '''
    return:返回百度疫情热搜 
    '''
    option = ChromeOptions()  #创建浏览器设置
    #option.add_argument('--headless')  #隐藏浏览器
    option.add_argument('--no-sandbox')

    driver_path = r'D:\pcong\chromedriver_win32\chromedriver_win32\chromedriver.exe'  # 此路径为你安装chromedriver这个软件的路径
    url = 'https://voice.baidu.com/act/virussearch/virussearch?from=osari_map&tab=0&infomore=12'
    browser = Chrome(executable_path=driver_path)
    browser.get(url)

    browser.find_element_by_xpath("//div[@class='VirusHot_1-5-5_1Fqxy-']").click()
    text = browser.page_source
    selector = etree.HTML(text)
    time.sleep(1)
    news = selector.xpath('//*[@id="ptab-0"]/div/div[2]/section/a//text()')
    l = [i for i in news if len(i) > 2][2:]
    l2 = []
    for i in range(0, len(l), 2):
        temp = l[i] + l[i - 1]
        l2.append(temp)
    return l2


def update_hotsearch():
    """
    将疫情热搜插入数据库
    :return:
    """
    cursor = None
    conn = None
    try:
        context = get_baidu_hot()
        print(time.asctime(),"开始更新热搜数据")
        conn, cursor = get_conn()
        sql = "insert into hotsearch(dt,content) values(%s,%s)"
        ts = time.strftime("%Y-%m-%d %X")
        for i in context:
            cursor.execute(sql, (ts, i))  # 插入数据
        conn.commit()  # 提交事务保存数据
        print(time.asctime(),"数据更新完毕")
    except:
        pass
    finally:
        close_conn(conn, cursor)

if __name__ == '__main__':
    update_hotsearch()
    #get_baidu_hot()
