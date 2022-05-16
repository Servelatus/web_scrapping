# 1) Написать приложение, которое собирает основные новости с сайтов news.mail.ru, lenta.ru, yandex.news
# Для парсинга использовать храth.
# Структура данных должна содержать:
# Название источника,
# Дата публикации
# наименование новости,
# ссылку на новость,
#
# 2) Сложить все новости в БД: без дубликатов, с обновлениями

import datetime
from pymongo import MongoClient

from lxml import html
import requests
from pprint import pprint

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                            '537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}


sources = {'https://lenta.ru/': [["//a[contains(@class,'card-mini')]",".//span[contains(@class,'mini__title')]/text()",
                                  ".//time[contains(@class,'card-mini__date')]/text()","./@href"],
                                 ["//a[contains(@class,'card-big')]", ".//span[contains( @class ,'card-big__rightcol')]/text()",
                                  ".//time[contains(@class,'card-big__date')]/text()", "./@href"]],
           'https://news.mail.ru/': ["//li",".//a[contains(@class,'list__text')]/text()",".//a[contains(@class,'list__text')]/text()",".//@href"],
           'https://yandex.ru/news/':["//h2[contains(@class,'card__title')]"] }
source = 'https://lenta.ru/'
response = requests.get(source, headers=header)

dom = html.fromstring(response.text)

news= []

# Mongo
client = MongoClient('127.0.0.1', 27017)
db = client['news']
news_db = db.news_db  # переменная укзывающая на коллекцию в базе


# новости lenta.ru без картинок   //span[contains(@class,'mini__title')]
# c картинками  //span[contains(@class,'card-big__rightcol')]


# //div[contains(@class,'card-big')]
#//span[contains(@class,'mini__title')] | //span[contains(@class,'card-big__rightcol')]

# новости https://news.mail.ru/ без картинок //li
# c картинками три верхние новости //a[contains(@class,'topnews')]
# картинки тематических блоков //a[contains(@class,'newsitem')]

# https://yandex.ru/news
# //h2[contains(@class,'card__title')]



# //a[contains(@class,'card-big')]
#.//span[contains( @class ,'card-big__rightcol')] /
items = dom.xpath("//a[contains(@class,'card-mini')]")

i = 0

def is_doc_in_the_db(doc):
    # проверка на вхождение документа в базу
    if news_db.find_one(doc):
        doc_in = False  # документ уже есть
    else:
        doc_in = True  # новый документ
    return doc_in

def if_no_date(date):
    # Если у новости нет даты, то дата ставится текущая
    now = datetime.datetime.now()
    month = {1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля', 5: 'мая', 6: 'июня',
             7: 'июля', 8: 'августа', 9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'}
    if not date or len(date[0]) < 7:
        date = now.strftime("%d-%m-%Y")
        convert_date = date[:2] + ' ' + month[now.month] + ' ' + date[6:]
    else:
        convert_date = date[0][7:]
    return convert_date



for item in items:
    news = {}
    date = item.xpath(".//time[contains(@class,'card-mini__date')]/text()")
    date = if_no_date(date)
    news['title'] = item.xpath(".//span[contains(@class,'mini__title')]/text()")
    news['date'] = date
    news['link'] = item.xpath("./@href")
    news['source'] = source

    if is_doc_in_the_db(news):
        news_db.insert_one(news)





items = dom.xpath("//a[contains(@class,'card-big')]")
for item in items:
    news = {}
    news['title'] = item.xpath(".//span[contains( @class ,'card-big__rightcol')]/text()")
    date = item.xpath(".//time[contains(@class,'card-big__date')]/text()")
    date = if_no_date(date)
    news['date'] = date
    # link = item.xpath("a[contains(@class,'card-big')]/@gref")
    link = item.xpath("./@href")

    segment_of_link = link[0][:5]
    if segment_of_link != 'https':
        segment_of_link = 'https:/' + link[0]
        link[0] = segment_of_link

    news['link'] = link
    news['source'] = source
    if is_doc_in_the_db(news):
        news_db.insert_one(news)


source = 'https://news.mail.ru/'
response = requests.get(source, headers=header)

dom = html.fromstring(response.text)

items = dom.xpath("//li")
for item in items:
    news = {}
    news['title'] = item.xpath(".//a[contains(@class,'list__text')]/text()")
    date = ''
    date = if_no_date(date)
    news['date'] = 'if_no_date(date)'
    news['link'] = item.xpath(".//@href")
    news['source'] = source
    if is_doc_in_the_db(news):
        news_db.insert_one(news)

source = 'https://yandex.ru/news/'
response = requests.get(source, headers=header)

dom = html.fromstring(response.text)

news= []

items = dom.xpath("//h2[contains(@class,'card__title')]")
for item in items:
    news = {}
    date = item.xpath("../span[contains(@class,'time')]/text()")
    date = if_no_date(date)
    news['title'] = item.xpath(".//a/text()")
    # date = ''
    news['date'] = date
    news['link'] = item.xpath(".//@href")
    news['source'] = source
    if is_doc_in_the_db(news):
        news_db.insert_one(news)

for doc in news_db.find():
    pprint(doc)

print('############'  )