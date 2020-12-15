import schedule
import datetime
import time
import requests
from lxml import etree
import yagmail
from lxml.html import tostring
import re


def get_url(url):
    # 抓取url
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
        "Referer": "http://www.xwlbo.com/"
    }
    try:
        rsp = requests.get(url, headers=header, timeout=5)
        rsp.raise_for_status()
        rsp.encoding = rsp.apparent_encoding
        # print(rsp.text)
        return rsp.text
    except requests.RequestException as error:
        print(error)


def data_handle(data):
    # 提取数据
    date_time = (datetime.date.today() + datetime.timedelta(-1)).strftime("%Y-%#m-%#d").replace('-', '{}').format('年',
                                                                                                                  '月') + "日新闻联播文字完整版内容"
    tree = etree.HTML(data)
    new_url = tree.xpath('//*[contains(text(),"{}")]/@href'.format(date_time))[0]
    news_rsp = get_url(new_url)

    # 提取标签中的html格式
    etr = etree.HTML(news_rsp)
    news_content = etr.xpath('//div[@class="text_content"]')[0]

    news_contens = tostring(news_content, encoding='utf-8').decode('utf-8')

    # 增加对敏感字符的处理
    news_text = re.sub('习近平', "习大大", news_contens)

    return news_text


def email_send(rsp):
    # 发送数据到邮箱
    yag = yagmail.SMTP(user='youremail', password='yourpassword', host='smtp.qq.com', port=465)

    subject = (datetime.date.today() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d") + " 新闻联播文字报"
    yag.send(to=['email'], subject=subject, contents=rsp)
    print('邮件已发送请查收...')


def serverjiang(rsp):
    # 通过server酱发送消息

    data = {
        'text': (datetime.date.today() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d") + " 新闻联播文字报",
        'desp': rsp
    }
    check_rsp = requests.post('https://sc.ftqq.com/youkey.send',
                              data=data)
    print(check_rsp)


def main():
    # 程序执行入口
    rsp = get_url("http://www.xwlbo.com/txt.html")
    news_content = data_handle(rsp)
    email_send(news_content)
    # serverjiang(news_content)


if __name__ == '__main__':
    schedule.every().day.at("08:30").do(main)
    while True:
        schedule.run_pending()
        time.sleep(10)
