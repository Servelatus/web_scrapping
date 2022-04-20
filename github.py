# Задание 1

# Написать функцию возвращающую список репозиториев для конкретного
# пользователя с GitHab и сохраняющую JSON - вывод в файл *.json.

import json
import requests

list_repos = []

def repositories():
    user = input('Имя юзера ')
    r_all = requests.get(f'https://api.github.com/users/{user}/repos')
    with open('data.json', 'w') as outfile:
         json.dump(r_all.json(), outfile)
    for repo in r_all.json():
        if not repo['private']:
            list_repos.append(repo['html_url'])

    return list_repos

print(repositories())

# Задание 2

# Написать функцию, которая получает погоду в данный момент для города,
# название доя которого получается через input.  https://.openweathermap.org

import os
import requests
from dotenv import load_dotenv
load_dotenv("./.env")
token = os.getenv("WEATHER_TOKEN", None)


def weather():
    city = input('Введите город: ')
    # получаем координаты города
    coordinates = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=5&{token}')
    city_coordinates =coordinates.json()
    lat = city_coordinates[2]['lat']
    lon = city_coordinates[2]['lon']

    # получаем погоду в городе
    weather = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&{token}#&units=metric')
    return weather.json()

city_weather = weather()
city_name = city_weather['name']
temp = round(city_weather['main']['temp'] - 273.15,1)
print(f'Температура в {city_name} {temp} градусов' )
