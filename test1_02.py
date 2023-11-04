import time

import requests
import json
import sqlite3
import matplotlib.pyplot as plt
import numpy as np

# 创建数据库
conn = sqlite3.connect('../db/test1_02.db')
print("数据库打开成功")
c = conn.cursor()
c.execute('''CREATE TABLE SUBMIT
(ID INT ,
TITLE  TEXT ,
JUDGERESULT CHAR(10),
JUDGESCORE  INT,
TEMPLATETITLE char(10))''')

print("数据表创建成功")
conn.commit()

print("开始爬取")

# 获取提交信息


def get_submits():
    url = "https://oj.qd.sdu.edu.cn/api/submit/list"
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.69"
    }
    datas = []
    k = 0
    indexs = range(1, 100)
    for index in indexs:
        params = {
            "pageNow": index,
            "pageSize": 20
        }
        r = requests.get(url, headers=head, params=params, timeout=5).text
        # 将json转换为Python数据
        data = json.loads(r)
        if data["code"] != 0:
            print("ERROR:"+data["message"])
            continue
        datas.append(data["data"]["rows"])
        print(k)
        k = k + 1
        # 设置延时
        if k % 6 == 0:
            time.sleep(1)
    return datas

# 对页面数据进行解析并存入数据库


def lxml_submits(submits):
    # 提交中可能出现的所有情况
    result_mapping = {
        1: "测试通过",
        6: "答案错误",
        8: "编译错误",
        4: "运行时错误",
        7: "格式错误",
        2: "时间超限"
    }
    for submit in submits:
        id = submit["problemId"]
        title = submit["problemTitle"]
        judgeResult = result_mapping.get(submit["judgeResult"],None)
        judgeScore = submit["judgeScore"]
        judgeTemplateTitle = submit["judgeTemplateTitle"]
        c.execute("INSERT INTO SUBMIT (ID, TITLE, JUDGERESULT, JUDGESCORE, TEMPLATETITLE) \
                   VALUES (?, ?, ?, ?, ?)",(id, title, judgeResult, judgeScore, judgeTemplateTitle)
                  )
        conn.commit()

# 绘图
# 1.AC次数前十


def show_accept():
    # 寻找AC次数前十的题目
    c.execute('''
                SELECT ID, TITLE, COUNT(*) AS ACCEPTNUM,(SELECT COUNT(*) FROM SUBMIT GROUP BY ID, TITLE) SUMBITNUM
                FROM SUBMIT
                WHERE JUDGERESULT = "测试通过"
                GROUP BY ID, TITLE
                ORDER BY ACCEPTNUM DESC
                LIMIT 10
                ''')
    lists = c.fetchall()
    # 创建一个点数为 18 x 6 的窗口, 并设置分辨率为 80像素/每英寸
    plt.figure(figsize=(18, 6), dpi=80)

    # 包含每个柱子下标的序列
    index = np.arange(10)
    # 包含每个柱子对应值的序列
    values_accept = []
    values_other = []
    # 每根柱子对应的名称
    labels = []
    for list in lists:
        ID, TITLE, ACCEPTNUM, SUBMITNUM = list
        values_accept.append(ACCEPTNUM)
        values_other.append(SUBMITNUM - ACCEPTNUM)
        labels.append(ID)

    plt.bar(index, values_accept, 0.4, label="AC", color="red")
    plt.bar(index, values_other, 0.4, label="OTHER", color="blue", bottom=values_accept)

    # 添加纵横轴的刻度
    plt.xticks(index, labels)
    plt.yticks(np.arange(0, 500, 50))
    # 设置横轴标签
    plt.xlabel('Problem')
    # 设置纵轴标签
    plt.ylabel('Situation')
    # 添加标题
    plt.title('AC_Problem_10 Situation')
    # 添加图例
    plt.legend(loc="upper right")
    # 绘制
    plt.show()

# 2.提交次数前十


def show_submit():
    # 寻找提交次数前十的题目
    c.execute('''
                SELECT ID, TITLE, COUNT(*) AS SUBMITNUM
                FROM SUBMIT
                GROUP BY ID, TITLE
                ORDER BY  COUNT(*)  DESC
                LIMIT 10
                ''')
    lists = c.fetchall()
    # 创建一个点数为 18 x 6 的窗口, 并设置分辨率为 80像素/每英寸
    plt.figure(figsize=(18, 6), dpi=80)

    # 包含每个柱子下标的序列
    index = np.arange(10)
    # 包含每个柱子对应值的序列
    values_submit = []
    # 每根柱子对应的名称
    labels = []
    for list in lists:
        ID, TITLE, SUBMITNUM = list
        values_submit.append(SUBMITNUM)
        labels.append(ID)

    plt.bar(index, values_submit, 0.4, color="red")

    # 添加纵横轴的刻度
    plt.xticks(index, labels)
    plt.yticks(np.arange(0, 500, 50))
    # 设置横轴标签
    plt.xlabel('Problem')
    # 设置纵轴标签
    plt.ylabel('Situation')
    # 添加标题
    plt.title('SUBMIT_Problem_10 Situation')
    # 绘制
    plt.show()


datas = get_submits()
# 将初始信息全部存入数据库
for data in datas:
    lxml_submits(data)
print("爬取完毕")

# 开始绘制
show_accept()
show_submit()

conn.close()





















