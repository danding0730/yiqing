import requests
import json
import time
import pymysql
from selenium import webdriver
import re
from selenium.webdriver import Chrome, ChromeOptions
from lxml import etree
import sys


"""
返回历史数据和当日详细数据
"""
def get_conn():
    """
    :return: 连接，游标l
    """
    # 创建连接
    conn = pymysql.connect(host="localhost",
                           user="root",
                           password="1469a90da5f1896b",
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

def get_tencent_data():
    url = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5'
    url2 = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_other'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'Referer': 'https://xw.qq.com/act/qgfeiyan'
    }
    temp = requests.get(url,headers)
    temp2 = requests.get(url2,headers)
    res = json.loads(temp.text)  #json字符串转字典
    res2 = json.loads(temp2.text)  #json字符串转字典
    data_all = json.loads(res['data'])
    data_all2 = json.loads(res2['data'])

    history = {}  #历史数据h5

    for i in data_all2['chinaDayList']:
        ds = '2020.'+ i['date']
        tup = time.strptime(ds,'%Y.%m.%d')
        ds = time.strftime('%Y-%m-%d',tup)  # 改变时间格式,不然插入数据库会报错，数据库是datetime类型
        confirm = i['confirm']
        suspect = i['suspect']
        heal = i['heal']
        dead = i['dead']
        history[ds] = {'confirm':confirm,'suspect':suspect,'heal':heal,'dead':dead}
    for i in data_all2['chinaDayAddList']:
        ds = '2020.'+ i['date']
        tup = time.strptime(ds,'%Y.%m.%d')
        ds = time.strftime('%Y-%m-%d',tup)  # 改变时间格式,不然插入数据库会报错，数据库是datetime类型
        confirm = i['confirm']
        suspect = i['suspect']
        heal = i['heal']
        dead = i['dead']
        history[ds].update({'confirm_add':confirm,'suspect_add':suspect,'heal_add':heal,'deal_add':dead})

    details = []  # 当日详细数据
    update_time = data_all["lastUpdateTime"]
    data_province = data_all['areaTree'][0]["children"]
    for pro_infos in data_province:
        province = pro_infos["name"]  # 省名
        for city_infos in pro_infos["children"]:
            city = city_infos["name"]
            confirm = city_infos["total"]["confirm"]
            confirm_add = city_infos["today"]["confirm"]
            heal = city_infos["total"]["heal"]
            dead = city_infos["total"]["dead"]
            details.append([update_time, province, city, confirm, confirm_add, heal, dead])
    return history, details

def update_details():
    """
    更新 details 表
    :return:
    """
    cursor = None
    conn = None
    try:
        li = get_tencent_data()[1]  #  0 是历史数据字典,1 最新详细数据列表
        conn, cursor = get_conn()
        sql = "insert into details(update_time,province,city,confirm,confirm_add,heal,dead) values(%s,%s,%s,%s,%s,%s,%s)"
        sql_query = 'select %s=(select update_time from details order by id desc limit 1)' #对比当前最大时间戳
        cursor.execute(sql_query,li[0][0])
        if not cursor.fetchone()[0]:
            print(time.asctime(),"开始更新最新数据")
            for item in li:
                cursor.execute(sql, item)
            conn.commit()  # 提交事务 update delete insert操作
            print(time.asctime(),"更新最新数据完毕")
        else:
            print(time.asctime(),"已是最新数据！")
    except:
        pass
        #traceback.print_exc()
    finally:
        close_conn(conn, cursor)

def insert_history():
    """
        插入历史数据
    :return:
    """
    cursor = None
    conn = None
    try:
        dic = get_tencent_data()[0]  # 0 是历史数据字典,1 最新详细数据列表
        print(time.asctime(),"开始插入历史数据")
        conn, cursor = get_conn()
        sql = "insert into history values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        for k, v in dic.items():
            # item 格式 {'2020-01-13': {'confirm': 41, 'suspect': 0, 'heal': 0, 'dead': 1}
            print(v.get('confirm_add'))
            cursor.execute(sql, [k, v.get("confirm"), v.get("confirm_add"), v.get("suspect"),
                                 v.get("suspect_add"), v.get("heal"), v.get("heal_add"),
                                 v.get("dead"), v.get("deal_add")])
            print(sql)
        conn.commit()  # 提交事务 update delete insert操作
        print(time.asctime(),"插入历史数据完毕")
    except:
        pass
        #traceback.print_exc()
    finally:
        close_conn(conn, cursor)

def update_history():
    """
    更新历史数据
    :return:
    """
    cursor = None
    conn = None
    try:
        dic = get_tencent_data()[0]  #  0 是历史数据字典,1 最新详细数据列表
        print(time.asctime(),"开始更新历史数据")
        conn, cursor = get_conn()
        sql = "insert into history values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        sql_query = "select confirm from history where ds=%s"
        for k, v in dic.items():
            # item 格式 {'2020-01-13': {'confirm': 41, 'suspect': 0, 'heal': 0, 'dead': 1}
            if not cursor.execute(sql_query, k):
                cursor.execute(sql, [k, v.get("confirm"), v.get("confirm_add"), v.get("suspect"),
                                     v.get("suspect_add"), v.get("heal"), v.get("heal_add"),
                                     v.get("dead"), v.get("dead_add")])
        conn.commit()  # 提交事务 update delete insert操作
        print(time.asctime(),"历史数据更新完毕")
    except:
        pass
        #traceback.print_exc()
    finally:
        close_conn(conn, cursor)

def get_baidu_hot():
    '''
    return:返回百度疫情热搜 
    '''
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(executable_path="/root/yiqin/yiqing/chromedriver", options=options)

    url = 'https://voice.baidu.com/act/virussearch/virussearch?from=osari_map&tab=0&infomore=12'
    browser = driver
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


if __name__ == "__main__":
    l = len(sys.argv)
    if l == 1:
        s = """
        请输入参数
        参数说明：  
        up_his  更新历史记录表
        up_hot  更新实时热搜
        up_det  更新详细表
        """
        print(s)
    else:
        order = sys.argv[1]
        if order == "up_his":
            update_history()
        elif order == "up_det":
            update_details()
        elif order == "up_hot":
            update_hotsearch()
update_history()
update_details()
update_hotsearch()


