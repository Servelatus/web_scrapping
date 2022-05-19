# Написать программу, которая собирает посты из группы https://vk.com/tokyofashion
#
# 1) в программе должен быть ввод, который передается в поисковую строку по постам группы
#
# 2) Соберите данные постов:

# - Дата поста

# - Текст поста
# - Ссылка на пост(полная)

# - Ссылки на изображения(если они есть; необязательно)

# - Количество лайков,
# "поделиться
# и просмотров поста
# 3) Сохраните собранные данные в MongoDB
#
# 4) Скролльте страницу, чтобы получить больше постов(хотя бы 2-3 раза)
#
# 5) (Дополнительно, необязательно) Придумайте как можно скроллить "до конца" до тех пор пока посты не перестанут добавляться
#
# Чем пользоваться?
#
# Selenium, можно пользоваться Ixml, BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import random
from pymongo import MongoClient

from bs4 import BeautifulSoup

def check_None(elem):
    # проверка на отсутствие лайков, ссылок и просмотров
    if elem != None:
        return elem.text

def is_doc_in_the_db(doc):
    # проверка на вхождение документа в базу
    if tokyo_fashion_db.find_one(doc):
        doc_in = False  # документ уже есть
    else:
        doc_in = True  # новый документ
    return doc_in

# Mongo
client = MongoClient('127.0.0.1', 27017)
db = client['tokyo_fashion']
tokyo_fashion_db = db.tokyo_fashion_db  # переменная укзывающая на коллекцию в базе


find_word = input('?')
driver = webdriver.Chrome(executable_path='./chromedriver.exe')
# driver.implicitly_wait(15)
driver.get('https://vk.com/tokyofashion')

find = driver.find_element(By.XPATH, "//a[contains(@class,'ui_tab_search')]")
find.click()
#

#
find_text = driver.find_element(By.ID, "wall_search")
# find_text.send_keys('Казуки')
find_text.send_keys(find_word)
find_text.send_keys(Keys.ENTER)
i = 0

prev_count = 0
while True:

    find_text.send_keys(Keys.PAGE_DOWN)
    time.sleep(random.randint(1, 2))
    find_count = driver.find_elements(By.XPATH, "//div[contains(@id,'page_search_posts')]")

    count_of_posts = driver.find_elements(By.XPATH, "//div[contains(@id,'post-')]")

    print(len(count_of_posts), 'i = ', i)
    if i == 2:
        # закрываем всплывающее окно с предложение зарегистрироваться
        close_btn = driver.find_element(By.CLASS_NAME, "UnauthActionBox__close")
        close_btn.click()


    if not(i % 21):
        if len(count_of_posts) == prev_count:
            break # если количество постов после очередной прокрутки не меняется значит докрутили страничку до конца
        else:
            prev_count = len(count_of_posts)
    i += 1

full_page = driver.page_source

soup = BeautifulSoup(full_page, 'html.parser')
search_block = soup.find('div', id='page_search_posts')
posts = search_block.find_all('div', class_="_post post page_block post--withPostBottomAction post--with-likes closed_comments deep_active")

for post in posts:
    post_info = {}
    date = post.find('span',{'class':"rel_date"})
    post_info['date'] = date.text

    info = post.find('div', {'class':"wall_post_text"})
    post_info['text'] = info.text

    link = post.find('a', {'class':"post_link"}).get('href')
    post_info['link'] = 'https://vk.com/tokyofashion?w=' + link[1:]


    likes = post.find('div', class_="PostButtonReactions__title _counter_anim_container")

    post_info['likes'] = check_None(likes)

    links_to_post = post.find('span', сlass_="PostBottomAction__count _like_button_count _counter_anim_container PostBottomAction__count--withBg")

    post_info['links_to_post'] = check_None(links_to_post)

    views = post.find('span', {'class': "_views"})
    post_info['views'] = check_None(views)


    if is_doc_in_the_db(post_info):
        tokyo_fashion_db.insert_one(post_info)


driver.quit()



