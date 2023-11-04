import requests
import json
import sqlite3
import matplotlib.pyplot as plt


conn = sqlite3.connect('../db/test2_02.db')
print("数据库打开成功")
c = conn.cursor()
c.execute('''CREATE TABLE SUBMIT_2
(ID INT ,
TITLE  TEXT ,
JUDGERESULT CHAR(10),
JUDGESCORE  INT,
TEMPLATETITLE char(10),
USERID INT)''')

print("数据表创建成功")
conn.commit()

print("开始爬取")

# 模拟登录状态


def login():
    login_url = "https://oj.qd.sdu.edu.cn/api/user/login"
    session_requests = requests.session()  # 创建一个session保存登陆状态
    # Create payload
    payload = {
        "password": "OL2023u003",
        "username": "OL2023u003"
    }
    head = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'no-cache, no-store, must-revalidate',
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://oj.qd.sdu.edu.cn',
        'referer': 'https://oj.qd.sdu.edu.cn/v2/login?to=/v2/home',
        'sec-ch-ua': '"Chromium";v="118", "Microsoft Edge";v="118", "Not=A?Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    }
    session_requests.post(login_url, data=json.dumps(payload), headers=head)
    return session_requests


# 获取提交信息


def get_submits():
    url = "https://oj.qd.sdu.edu.cn/api/contest/listSubmission"
    indexs = range(1, 4)
    head = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    }
    datas = []
    k = 0
    ret = login()
    for index in indexs:
        params = {
            "pageNow": index,
            "pageSize": 20,
            "contestId": 286
        }
        r = ret.get(url, headers=head, params=params, timeout=4).text
        # 将json转换为Python数据
        data = json.loads(r)
        if data["code"] != 0:
            print("ERROR")
            continue
        datas.append(data["data"]["rows"])
        print(k)
        k = k + 1
    return datas


datas = get_submits()

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
        id = submit["problemCode"]
        title = submit["problemTitle"]
        judgeResult = result_mapping.get(submit["judgeResult"],None)
        judgeScore = submit["judgeScore"]
        judgeTemplateTitle = submit["judgeTemplateTitle"]
        userid = submit["username"]
        c.execute("INSERT INTO SUBMIT_2 (ID, TITLE, JUDGERESULT, JUDGESCORE, TEMPLATETITLE, USERID) \
                   VALUES (?, ?, ?, ?, ?, ?)",(id, title, judgeResult, judgeScore, judgeTemplateTitle, userid)
                  )
# 将初始信息全部存入数据库


for data in datas:
    lxml_submits(data)
print("爬取完毕")
conn.commit()
print("已存入数据库")


# 分析某同学提交数据并进行可视化操作
c.execute('''
            SELECT  COUNT(*) AS ACCEPTNUM,(SELECT COUNT(*) FROM SUBMIT_2 WHERE  USERID = 202200300292) SUMBITNUM
            FROM SUBMIT_2
            WHERE USERID = 202200300292 AND JUDGERESULT = "测试通过"
            ''')
lists_1 = c.fetchall()


for list in lists_1:
    value_accept, value_submit = list

# 创建一个点数为 18 x 6 的窗口, 并设置分辨率为 80像素/每英寸
plt.figure(figsize=(18, 6), dpi=80)
labels = ["AC", "OTHER"]
plt.pie(x=[value_accept, value_submit - value_accept], labels=labels, colors=["#d5695d", "#5d8ca8"], explode=(0.2, 0), autopct='%.2f%%' )

plt.show()

c.execute('''
            SELECT  ID, TITLE
            FROM SUBMIT_2 
            WHERE USERID = 202200300292 AND 
                  ID NOT IN (
                  SELECT ID 
                  FROM SUBMIT_2
                  WHERE USERID = 202200300292 AND
                        JUDGERESULT = "测试通过"
                  )
            GROUP BY ID, TITLE
            ORDER BY ID
            ''')
lists_2 = c.fetchall()
print("未AC的题目:")
for list in lists_2:
    not_ac_id, not_ac_title = list
    print(f"{not_ac_id} {not_ac_title}")

conn.close()
