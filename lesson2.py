# Необходимо собрать информацию о вакансиях вводимую должность (используем input) с сайтов
# На Superjob(необязательно) и НН(обязательно).
# Приложение должно анализировать несколько страниц сайта (также вводим через input).
# Получившийся список должен содержать в себе минимум:
#
# Наименование вакансии.
#
# Предлагаемую зарплату (отдельно минимальную и максимальную).
#
# Ссылку на саму вакансию.
#
# Сайт, откуда собрана вакансия.
#
# По желанию можно добавить еще параметры вакансии (например, работодателя и расположение)
# Структура должна быть одинаковая для вакансий с обоих сайтов. Сохраните результат в json-файл


import time
import random

from bs4 import BeautifulSoup
import requests
import json
from pprint import pprint


def fill_list_of_vacancies(soup_vacancies):
    # заполняем список вакнсий
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

        vacancies.append(name)
        vacancies.append(wage_min)
        vacancies.append(wage_max)
        vacancies.append(link)
        vacancies.append('https://hh.ru/')

    vacancies_list.append(vacancies)
    return vacancies_list


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


url = 'https://hh.ru/vacancies/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                            '537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
vacancies = []
vacancies_list = []
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


with open('data.txt', 'w') as outfile:
    json.dump(vacancies_list, outfile)
