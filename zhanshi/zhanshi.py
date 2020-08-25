import time
import json
import string
from utils import get_time,get_c1_data,get_c2_data,get_l1_data,get_l2_data,get_r1_data,get_r2_data
from flask import Flask
from flask import render_template
from flask import jsonify
from jieba.analyse import extract_tags

app = Flask(__name__)


@app.route('/')  #访问主页
def index():
    return render_template('main.html')


@app.route('/time')  #获取时间信息
def g_time():
    return get_time()

@app.route('/c1')  #获取当前总人数
def g_c1():
    temp = get_c1_data()
    return jsonify({'confirm':temp[0],'suspect':temp[1],'heal':temp[2],'dead':temp[3]})  #前端由ajax负责加载数据

@app.route('/c2')  #获取地图分布数据
def g_c2():
    temp = get_c2_data()
    return jsonify({'data':temp})  #前端由ajax负责加载数据


@app.route("/l1")  #总人数趋势
def get_l1():
    data = get_l1_data()
    day,confirm,suspect,heal,dead = [],[],[],[],[]
    for a,b,c,d,e in data[7:]:
        day.append(a.strftime("%m-%d")) #a是datatime类型
        confirm.append(b)
        suspect.append(c)
        heal.append(d)
        dead.append(e)
    return jsonify({"day":day,"confirm": confirm, "suspect": suspect, "heal": heal, "dead": dead})  #前端由ajax负责加载数据

@app.route("/l2")  #新增趋势
def get_l2():
    data = get_l2_data()
    day, confirm_add, suspect_add = [], [], []
    for a, b, c in data[7:]:
        day.append(a.strftime("%m-%d"))  # a是datatime类型
        confirm_add.append(b)
        suspect_add.append(c)
    return jsonify({"day": day, "confirm_add": confirm_add, "suspect_add": suspect_add})#前端由ajax负责加载数据

@app.route("/r1")  #单日前5
def get_r1():
    data = get_r1_data()
    city = []
    confirm = []
    for k, v in data:
        city.append(k)
        confirm.append(int(v))
    return jsonify({"city": city, "confirm": confirm})

@app.route("/r2")  #词云数据
def get_r2():
    data = get_r2_data()
    d = []
    for i in data:
        k = i[0].rstrip(string.digits)  #去除权重数字
        v = i[0][len(k):]  #获取热搜数字
        ks = extract_tags(k)  #使用jieba提取关键字
        for j in ks:
            if not j.isdigit():
                d.append({'name':j,'value':v})

    return jsonify({'kws':d})

if __name__ == '__main__':
    app.run()

