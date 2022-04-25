# 1. Развернуть у себя на компьютере/виртуальной/хостинг MongoDB и реализовать функцию,
# записывающую собранные вакансии в созданную БД(добавление данных в БД по ходу сбора данных). І
#
# 2. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.
#
# 3. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой
# больше введённой суммы.
# Необязательно - возможность выбрать вакансии без указанных зарплат.

import time
import random
from bs4 import BeautifulSoup
import requests
import json
from pymongo import MongoClient
from pprint import pprint

client = MongoClient('127.0.0.1', 27017)
db = client['vacancies']
vac_db = db.vac_db  # переменная укзывающая на коллекцию в базе


def fill_list_of_vacancies(soup_vacancies):
    # заполняем список вакансий
    for div in soup_vacancies:
        info_name_link = div.find('a', class_="bloko-link")
        name = info_name_link.text
        link = info_name_link.get('href')
        info_wage = div.find('span', {'data-qa': "vacancy-serp__vacancy-compensation"})
        try:
            # если ожидаемая зарплата не указана то wage_min, wage_min = None
            wage_min = wage_str_to_digit(info_wage.text)[0]
            wage_max = wage_str_to_digit(info_wage.text)[1]

        except:  # AttributeError
            wage_min = None
            wage_max = None
        vacancies.clear()
        vacancies['name'] = name
        vacancies['wage_min'] = wage_min
        vacancies['wage_max'] = wage_max
        vacancies['link'] = link
        vacancies['source'] = 'https://hh.ru/'
        if is_doc_in_the_db(vacancies):
            vac_db.insert_one(vacancies)


def wage_str_to_digit(info_wage):
    # выбираем суммы минимальной и максимальной ставки
    wage = info_wage
    wage = wage.split()
    if wage[0] == 'от':
        wage_min = int(wage[1] + wage[2])
        wage_max = None
    elif wage[0] == 'до':
        wage_min = None
        wage_max = int(wage[1] + wage[2])
    else:
        wage_min = int(wage[0] + wage[1])
        wage_max = int(wage[3] + wage[4])

    return wage_min, wage_max


def is_doc_in_the_db(doc):
    # проверка на вхождение документа в базу
    if vac_db.find_one(doc):
        doc_in = False  # документ уже есть
    else:
        doc_in = True  # новый документ
    return doc_in


def find_wage():
    # производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.
    # Необязательно - возможность выбрать вакансии без указанных зарплат.
    wage = int(input('Введите сумму '))

    if wage == 0:  # выбираем вакансии без зарплат
        for doc in vac_db.find({'$and': [{'wage_min': None}, {'wage_max': None}]}):
            pprint(doc)
    else:  # выбираем вакансии больше введенной суммы
        for doc in vac_db.find({'$or': [{'wage_max': {'$gt': wage}}, {'$and': \
                               [{'wage_max': None}, {'wage_min': {'$gt': wage}}]}]}):
            pprint(doc)


url = 'https://hh.ru/vacancies/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/' 
                            '537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
vacancies = {}

next_page = True
page = 0
vacancy = input('Введите специальность ')

while next_page:
    # в цикле перебираем страницы с выборкой
    params = {'page': page,
              'hhtmFrom': 'vacancy_search_catalog'}
    response = requests.get(url+vacancy, params=params, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # проверяем есть ли ещё страница выборки
    if soup.find('a', {'data-qa': "pager-next"}) != None:
        page += 1
        time.sleep(random.randint(1, 5))
    else:
        next_page = False

    soup_vacancies = soup.find_all('div', class_="vacancy-serp-item")
    fill_list_of_vacancies(soup_vacancies)

find_wage()
