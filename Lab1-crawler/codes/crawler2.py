'''
使用selenium+xpath进行爬取
'''
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import datetime
import pandas as pd

starttime = datetime.datetime.now()
data = {'title': [1] * 30, 'date': [2] * 30, 'content': [3] * 30}

df = pd.DataFrame(data)
driver = webdriver.Chrome()
driver.get(
    "http://vip.stock.finance.sina.com.cn/corp/view/vCB_BulletinGather.php?stock_str=sh600168&gg_date=&ftype=0"
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

    title = driver.find_element(
        By.XPATH, "//*[@id='allbulletin']/thead/tr/th").text  # 纯文本内容
    # print(title)
    df.loc[i, 'title'] = title

    date = driver.find_element(By.XPATH,
                               "//*[@id='allbulletin']/tbody/tr[1]/td").text
    df.loc[i, 'date'] = date

    content = driver.find_element(By.XPATH, "//*[@id='content']").text
    # print(content)
    df.loc[i, 'content'] = content
    # print("\n")
    driver.back()  # 后退，回到原始页面目录页
    time.sleep(1)  # 留出加载时间

print("count:" + str(length))  # 打印列表长度，即有多少篇公告

df.to_csv('./crawler2.csv', index=0, encoding='utf-8')
endtime = datetime.datetime.now()
print("running time:" + str((endtime - starttime).seconds) + "s")
