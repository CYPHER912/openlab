import requests
import json
import sqlite3


print("开始爬取")
conn = sqlite3.connect('../db/test2_01.db')
print("数据库打开成功")
c = conn.cursor()
c.execute('''CREATE TABLE PROBLEM_2
(ID INT ,
TITLE  TEXT,
TIMELIMIT INT)''')

print("数据表创建成功")
conn.commit()

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

# 获取页面数据


def get_problems():
    indexs = range(1, 7)
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    }
    url = "https://oj.qd.sdu.edu.cn/api/contest/queryProblem"
    datas = []
    k = 0
    ret = login()
    for index in indexs:
        params = {
            "contestId": 286,
            "problemCode": index
        }
        r = ret.get(url, timeout=4, headers=head, params=params).text
        data = json.loads(r)
        if data["code"] != 0:
            print("ERROR")
            continue
        datas.append(data["data"])
        print(k)
        k = k + 1
    return datas

# 对页面数据进行解析并存入数据库


def lxml_problems(problems):
    id = problems["problemCode"]
    title = problems["problemTitle"]
    timelimit = problems["timeLimit"]
    c.execute("INSERT INTO PROBLEM_2 (ID, TITLE, TIMELIMIT) \
                VALUES (?, ?, ?)", (id, title, timelimit)
                )


datas = get_problems()
for data in datas:
    lxml_problems(data)

conn.commit()
conn.close()
print("爬取完毕")