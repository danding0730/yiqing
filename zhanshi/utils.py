import time
import pymysql

def get_time():
    time_str = time.strftime('%Y{} %m{} %d{} %X')
    return time_str.format('年','月','日')

def get_conn():
    """
    :return: 连接，游标l
    """
    # 创建连接
    conn = pymysql.connect(host="localhost",
                           user="root",
                           password="qwedasd345",
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

def query(sql,*args):
    """
    封装通用查询
    :param sql: 
    :param args: 
    :return: 返回查询到的结果，（（），（））的形式
    """
    conn,cursor = get_conn()
    cursor.execute(sql,args)
    res = cursor.fetchall()
    close_conn(conn,cursor)
    return res

def get_c1_data():
    """
    
    :return: 返回累计确诊死亡新增案例
    """
    sql = """SELECT SUM(confirm),(SELECT suspect FROM history ORDER BY ds DESC LIMIT 1),SUM(heal),SUM(dead)
FROM details
WHERE update_time = (SELECT update_time FROM details ORDER BY update_time DESC LIMIT 1);"""
    res = query(sql)
    return res[0]


def get_c2_data():
    """

    :return: 返回累计确诊死亡新增案例
    """
    sql = """SELECT province,SUM(confirm)
FROM details
WHERE update_time = (SELECT update_time FROM details ORDER BY update_time DESC LIMIT 1 )
GROUP BY province;"""
    s = query(sql)
    ret = []
    for i in s:
        ret.append({'name':i[0],'value':i[1]})

    return ret


def get_l1_data():
    """

    :return: 返回累计确诊死亡新增案例
    """
    sql = """
    SELECT ds,confirm,suspect,heal,deal FROM history;
    """
    s = query(sql)
    ret = []

    return s

def get_l2_data():
    """

    :return: 返回累计确诊死亡新增案例
    """
    sql = """
    SELECT ds,confirm_add,suspect_add FROM history;
    """
    s = query(sql)

    return s

def get_r1_data():
    """
    :return:  返回非湖北地区城市确诊人数前5名
    """
    sql = """SELECT province,SUM(confirm_add)
FROM details 
WHERE update_time=(SELECT update_time FROM details ORDER BY update_time DESC LIMIT 1)
GROUP BY province
ORDER BY SUM(confirm_add) DESC
LIMIT 5;"""
    res = query(sql)
    return res

def get_r2_data():
    """
    :return:  返回非湖北地区城市确诊人数前5名
    """
    sql = """SELECT content
FROM hotsearch
WHERE dt=(SELECT dt FROM hotsearch ORDER BY dt DESC LIMIT 1);"""
    res = query(sql)
    return res


if __name__ == '__main__':
    print(get_r2_data())