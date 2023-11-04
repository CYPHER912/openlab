import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from PIL import Image
import re
import sqlite3
import ddddocr

# 创建数据库
conn = sqlite3.connect('../db/test3.db')
print("数据库打开成功")
c = conn.cursor()
c.execute('''CREATE TABLE NOTICE
(TITLE TEXT ,
URL  CHAR(100) ,
PUBLISHTIME CHAR(20),
CURRENTTIME  CHAR(20))''')

print("数据表创建成功")
conn.commit()

print("开始爬取")

# 进行截图
driver = webdriver.Chrome()
# 设置浏览器窗口最大化
driver.maximize_window()


# 获取html并对工作通知网页截图保存PDF
def get_html():
    # 设置爬取页数
    indexs = range(1, 2)
    htmls = []
    head = {  # 模拟浏览器头部信息
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 80.0.3987.122  Safari / 537.36"
    }
    k = 0
    for index in indexs:
        # 获取HTML
        url = f"https://www.bkjx.sdu.edu.cn/sanji_list.jsp?totalpage=167&PAGENUM={index}&urltype=tree.TreeTempUrl&wbtreeid=1010"
        r = requests.get(url, timeout=4, headers=head)
        if r.status_code != 200:
            print("error")
            continue
        print(k)
        k = k + 1
        htmls.append(r.text)
        # 截取工作通知页面
        # 打开网站
        driver.get(url)
        # 设置截图保存路径
        png_path = r"F:\Pythoncode\OpenLab\png\Job_notice\%s.png" % k
        # 截取当前页面
        driver.save_screenshot(png_path)
        # 打开截图文件
        screenshot = Image.open(png_path)
        rgb_image =screenshot.convert("RGB")
        # 设置PDF保存路径
        pdf_path = r"F:\Pythoncode\OpenLab\pdf\Job_notice\%s.pdf" % k
        # 将截图另存为PDF
        rgb_image.save(pdf_path, 'PDF', resolution=100.0)
    return htmls


# 解析HTML
def lxml_html(html):
    soup = BeautifulSoup(html,"lxml")  # 初始化
    articles = (
        soup.find("div", id="div_more_news")
            .find_all("div", class_="leftNews3")
    )
    for article in articles:
        base_url = article.find("a")["href"]
        # 使用正则表达式匹配参数部分
        pattern = r"wbtreeid=(\d+)&wbnewsid=(\d+)"
        match = re.search(pattern, base_url)
        if match:
            wbtreeid = match.group(1)
            wbnewsid = match.group(2)
        else:
            continue
        url = f"https://www.bkjx.sdu.edu.cn/content.jsp?urltype=news.NewsContentUrl&wbtreeid={wbtreeid}&wbnewsid={wbnewsid}"
        title = article.find("a").text
        publish_time = article.find("div", style="float:right;").text.replace("[", "").replace("]", "")
        current_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
        print(f"{url} {title}")
        # 将数据插入数据库
        c.execute("INSERT INTO NOTICE (TITLE, URL, PUBLISHTIME, CURRENTTIME) \
                   VALUES (?, ?, ?, ?)",(title, url, publish_time, current_time)
                  )
        conn.commit()
        # 截取通知详情页面
        # 打开网站
        driver.get(url)
        # 设置截图保存路径
        png_path = r"F:\Pythoncode\OpenLab\png\Notification_page\%s-%s.png" % (title, current_time)
        # 截取当前页面
        driver.save_screenshot(png_path)
        # 打开截图文件
        screenshot = Image.open(png_path)
        rgb_image = screenshot.convert("RGB")
        # 设置PDF保存路径
        pdf_path = r"F:\Pythoncode\OpenLab\pdf\Notification_page\%s-%s.pdf" % (title, current_time)
        # 将截图另存为PDF
        rgb_image.save(pdf_path, 'PDF', resolution=100.0)

        # 获取附件url
        r = requests.get(url).text
        soup = BeautifulSoup(r, "lxml")
        file_ul = soup.find("ul", style="list-style-type:none;text-align:left;")
        # 如果file_ul不存在，说明此通知页面无附件
        if not file_ul:
            print("未找到指定的内容。")
            continue
        file_tags = file_ul.find_all("a")
        for file_tag in file_tags:
            down_file(file_tag)


# 下载附件
def down_file(file_tag):
    file = file_tag["href"]
    file_url = f"https://www.bkjx.sdu.edu.cn{file}"
    # 打开浏览器
    driver.get(file_url)
    # 获得页面源码(动态加载后的)
    page_source = driver.page_source
    # 进行解析，获取验证码图片url
    soup = BeautifulSoup(page_source, 'lxml')
    img_tag = soup.find('img', id='codeimg')
    print(img_tag['src'])
    img = img_tag['src']
    img_url = f"https://www.bkjx.sdu.edu.cn{img}"
    ret = requests.get(img_url)
    img_data = ret.content
    # ocr获得验证码
    ocr = ddddocr.DdddOcr(show_ad=False)
    code = ocr.classification(img_data)
    cookies = ret.cookies
    # 发送请求并下载附件
    response = requests.get(file_url+"&codeValue="+code, cookies=cookies)
    file_name = file_tag.string
    with open(f"F:\Pythoncode\OpenLab\\file\{file_name}", "wb") as f:
        f.write(response.content)


htmls = get_html()
for html in htmls:
    lxml_html(html)

driver.quit()

print("爬取完毕")






