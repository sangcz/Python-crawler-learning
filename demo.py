from lxml import etree
import requests
import pymongo
import re
from multiprocessing import Pool
import time

client = pymongo.MongoClient('127.0.0.1', 27017) # 配置成自己的mongo数据库地址
mydb = client['mydb']
generalData = mydb['generalData']
checkStr = ['blockchain', 'digital+currency', 'crypto+currency', 'token', 'virtual+currency', 'private+keys', 'sharing+community', 'EOS', 'Bitcoin', 'Ethereum', 'Zec', 'Bts', 'Litecoin', 'VitalikButerin','Amber+Baldet', 'Jihan', 'Erik+Voorhees', 'Joe+Lubin', 'Jamie+Dimon', 'Dorian+S.+Nakamoto']
localTime = time.time()

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
}

def get_url(url):
    articleType = url.split('?s=')[-1]
    html = requests.get(url, headers=header, proxies={"http": "http://{}".format(getIpInfo())})
    selector = etree.HTML(html.text)
    infos = selector.xpath('//div[@class="posts-row"]/article')
    for info in infos:
        try:
            article_url_part = info.xpath('div/a/@href')[0]
            article_img = info.xpath('div/a/img/@src')[0]
            get_info(article_url_part, article_img, articleType)
        except IndexError:
            pass

def get_info(url, imgSrc, type):
    html = requests.get(url, headers=header)
    selector = etree.HTML(html.text)
    title = selector.xpath('//section/article/header/h1/text()')[0]
    author = selector.xpath('//footer/div[2]/div[1]/div/span[2]/text()')[0]
    date = selector.xpath('//header/div/time/@datetime')[0]
    date1 = date[0:10] + ' ' + date[11:19]
    timeNum = time.mktime(time.strptime(date1,"%Y-%m-%d %H:%M:%S"))
    content = re.findall('<p>(.*?)</p>', html.content.decode('utf-8'), re.S)

    data = {
        'articleImg': imgSrc,
        'title': title,
        'author': author,
        'date': timeNum,
        'content': content,
        'keywords': type,
        'source': 'ccn'
    }
    print(data)
    if (timeNum > (localTime - 7200)):
        print('插入一条新数据！')
        generalData.insert_one(data)
    else:
        print('暂无可爬取的新内容!')

# 请求代理
def getIpInfo():
    req = requests.get('proxy address') # 配置成自己的代理地址
    if (req.status_code == 200):
        for item in req.json():
            return item['protocol'] + "://" + item['host']

if __name__ == '__main__':
    urls = ['https://www.ccn.com/?s={}'.format(checkStr[i]) for i in range(19)]
    pool = Pool(processes=4)
    pool.map(get_url, urls)
