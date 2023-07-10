'''
使用selenium+beautifulsoup进行爬取
'''
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import datetime
import pandas as pd
from bs4 import BeautifulSoup

starttime = datetime.datetime.now()
data = {'title': [1] * 30, 'date': [2] * 30, 'content': [3] * 30}

df = pd.DataFrame(data)
driver = webdriver.Chrome()
driver.get(
    "http://vip.stock.finance.sina.com.cn/corp/view/vCB_BulletinGather.php?stock_str=sh600168&page_index=1"
)
time.sleep(3)  # 加载时间

links = driver.find_elements(
    By.XPATH, "/html/body/div/div[5]/table/tbody/tr/th/a[1]")  # 获取所有a标签组成列表
length = len(links)  # 一共有多少个标签

for i in range(0, length):  # 遍历列表的循环，逐一点击链接
    links = driver.find_elements(
        By.XPATH,
        "/html/body/div/div[5]/table/tbody/tr/th/a[1]")  # 每次循环时都重新获取a标签，组成列表
    link = links[i]  # 逐一将列表里的a标签赋给link
    url = link.get_attribute('href')  # 提取a标签内的链接（type:str）
    driver.get(url)
    time.sleep(1)  # 加载时间

    # 解析网页，第二个参数为解析器
    soup = BeautifulSoup(driver.page_source, "lxml")
    title = soup.find("th", class_="head").get_text()
    print(title)
    df.loc[i, 'title'] = str(title)

    date = soup.find("td", class_="head").get_text()
    print(date)
    df.loc[i, 'date'] = str(date)

    content = soup.find("div", id="content").contents
    # print(text)
    text = str()
    for p in content:
        text = text + "\n" + p.text
    df.loc[i, 'content'] = text

    driver.back()  # 后退，回到原始页面目录页
    time.sleep(1)  # 留出加载时间

print("count:" + str(length))  # 打印列表长度，即有多少篇公告

df.to_csv('./crawler3.csv', index=0, encoding='utf-8')
endtime = datetime.datetime.now()
print("running time:" + str((endtime - starttime).seconds) + "s")
