import requests
import json
import sqlite3

conn = sqlite3.connect('../db/test1_01.db')
print("数据库打开成功")
c = conn.cursor()
c.execute('''CREATE TABLE COMPANY
(ID INT PRIMARY KEY,
TITLE  TEXT ,
ACCEPTNUM INT,
SUBMITNUM INT,
SOCUSE  CHAR(20) )''')

print("数据表创建成功")
conn.commit()

print("开始爬取")
indexs = range(1, 6)
# 获取页面数据


def get_problems():
    url = "https://oj.qd.sdu.edu.cn/api/problem/list"
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.69"
    }
    datas = []
    k = 0
    for index in indexs:
        params = {
            "pageNow": index,
            "pageSize": 20
        }
        r = requests.get(url, headers=head, params=params,timeout=4).text
        # 将json转换为Python数据
        data = json.loads(r)
        if data["code"] != 0:
            print("ERROR")
            continue
        datas.append(data["data"]["rows"])
        print(k)
        k = k + 1
    return datas


# 对页面数据进行解析并存入数据库


def lxml_problems(problems):
    for problem in problems:
        id = problem["problemId"]
        title = problem["problemTitle"]
        ac_num = problem["acceptNum"]
        sub_num = problem["submitNum"]
        source = problem["source"]
        c.execute("INSERT INTO COMPANY (ID,TITLE,ACCEPTNUM,SUBMITNUM,SOCUSE) \
                   VALUES (?, ?, ?, ?, ?)",(id, title, ac_num, sub_num, source)
                  )


datas = get_problems()
for data in datas:
    lxml_problems(data)

conn.commit()
conn.close()
print("爬取完毕")






















