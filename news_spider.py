import schedule
import datetime
import time
import requests
from lxml import etree
import yagmail
from lxml.html import tostring
import re
from pywchat import Sender


def get_url(url):
    # 抓取url
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
        "Host": "mrxwlb.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    }
    date_time = (datetime.date.today() + datetime.timedelta(-1)).strftime("%Y-%#m-%#d").replace('-', '{}').format('年',
                                                                                                                  '月') + "日新闻联播文字版"
    url = url + "/{}".format(date_time)
    try:
        rsp = requests.get(url, headers=header, timeout=5)
        rsp.raise_for_status()
        rsp.encoding = rsp.apparent_encoding
        # print(rsp.text)
        return rsp.text
    except requests.RequestException as error:
        print(error)


def data_handle(data):
    # 提取标签中的html格式
    etr = etree.HTML(data)
    news_content = etr.xpath('//div[@class="posts-wrapper"]/article')[0]

    news_contens = tostring(news_content, encoding='utf-8').decode('utf-8')
    # print(news_contens)
    # print("*"*10)
    news_text = re.sub("————–<br>[\\s\\S]*", "", news_contens)

    # 增加对敏感字符的处理
    # news_text = re.sub('习近平', "习大大", news_text)
    #
    return news_text


def email_send(rsp):
    # 发送数据到邮箱
    yag = yagmail.SMTP(user='youremail', password='emailpassword', host='smtp.qq.com', port=465)

    subject = (datetime.date.today() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d") + " 新闻联播文字报"
    yag.send(to=["email"], subject=subject, contents=rsp)
    print('邮件已发送请查收...')


def send_wechat(url, **kwargs):
    date_time = (datetime.date.today() + datetime.timedelta(-1)).strftime("%Y-%#m-%#d").replace('-', '{}').format('年',
                                                                                                                  '月') + "日新闻联播文字版"
    url = url + "/{}".format(date_time)
    user = kwargs.pop("touser")
    Sender(**kwargs).send_textcard(date_time, date_time, url, touser=user)


def main(wechat=None, **kwargs):
    # 程序执行入口
    uri = "http://mrxwlb.com"

    if wechat:
        send_wechat(uri, **kwargs)
    else:
        rsp = get_url(uri)
        news_content = data_handle(rsp)
        # print(news_content)
        email_send(news_content)


if __name__ == '__main__':
    schedule.every().day.at("08:30").do(main)
    while True:
        schedule.run_pending()
        time.sleep(10)
