import re
import requests
from lxml import etree
import datetime
import yagmail

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4651.0 Safari/537.36'
}


# 获取新闻
def get_hanlder(url):
    try:
        rsp = requests.get(url, headers=headers, timeout=5)
        rsp.raise_for_status()
        rsp.encoding = rsp.apparent_encoding
        return rsp.text
    except requests.RequestException as error:
        print(error)
        exit()


def get_news(url):
    """
    新闻联播获取函数
    """
    rsp = get_hanlder(url)
    etr = etree.HTML(rsp)
    titles = etr.xpath("//div[@class='title']/text()")
    hrefs = etr.xpath("//li/a/@href")

    news = []
    summary = None
    for title, href in zip(titles, hrefs):
        if '《新闻联播》' in title:
            # 获取新闻概要
            title_rsp = get_hanlder(href)
            summary = '<div>' + re.search(r'</em>本期节目主要内容：[\s\S]*。', title_rsp).group(
                0) + "</div>\n\n\n"
            continue

        # 新闻标题去掉视频并处理成超链接  橙色 #D2691E
        tit = title.replace("[视频]", "")
        subtitle = f'<a href=\"{href}\" style="color:#4682B4"><b>{tit}</b></a>'
        summary = re.sub(tit, subtitle, summary)

        # 获取新闻正文并添加到news
        news_text = get_hanlder(href)
        news_th = re.findall(r'.*(<div class="cnt_bd"><!--repaste.body.begin-->.*?</div>).*', news_text)[0]
        news.append(f"{subtitle}\n{news_th}")

    news.insert(0,summary)
    return news


def email_send(rsp,strdate):
    # 发送数据到邮箱
    yag = yagmail.SMTP(user='sendQQemail', password='emailpassword', host='smtp.qq.com', port=465)
    yag.send(to=["receiveemai"], subject=f"{strdate}日新闻联播推送", contents=rsp)
    print('邮件已发送请查收...')


def scf_run(event, context):
    # 获取日期
    strTime = (datetime.date.today() + datetime.timedelta(-1)).strftime("%Y%m%d")

    url = f'https://tv.cctv.com/lm/xwlb/day/{strTime}.shtml'

    news_text = get_news(url)
    email_send(news_text, strTime)

