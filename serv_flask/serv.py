# python C:\Users\atlas\Desktop\yrck\serv_flask\serv.py
from flask import Flask, jsonify
from flask import abort
from flask import request
from flask import Response
import requests as req
import codecs
from bs4 import BeautifulSoup
import re
import json
import psycopg2
import os
import time
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from flask_cors import CORS


app = Flask(__name__)
# cors = CORS(app, resources={r"/api/v1.0/*": {"origins": "*"}})
CORS(app, supports_credentials=True)

conn = psycopg2.connect(dbname='db_site', user='postgres',
                        password='qwerty', host='localhost',
                        port='5432')
cursor = conn.cursor()

def request_yandex(city):
    print('Выполняется поиск.. \n' + city +' широта и долгота')

    input_prem = ''
    input_prem1 = ''
    temp_value = []
    arr_1 = []
    text = ''
    arr = []

    print(1)
    options = FirefoxOptions()
    options.add_argument("--headless")

    gecko = os.path.normpath(os.path.join(os.path.dirname(__file__), 'geckodriver'))
    binary = FirefoxBinary(r'C:\Program Files\Mozilla Firefox\firefox.exe')
    # driver = webdriver.Firefox(firefox_binary=binary, executable_path=gecko+'.exe')
    driver = webdriver.Firefox(firefox_binary=binary, executable_path=gecko+'.exe', options=options)

    driver.get('http://yandex.ru')
    element = driver.find_element_by_class_name("input__input")
    g_req = city + ' ' + 'широта и долгота'
    element.send_keys(g_req, Keys.RETURN)
    time.sleep(5)
    str = driver.page_source

    with open('C:/Users/atlas/Desktop/yrck/serv_flask/test.html', 'wb') as output_file:
        output_file.write(str.encode('utf-8'))
    print(2)
    driver.quit()

    with codecs.open('C:/Users/atlas/Desktop/yrck/serv_flask/test.html', "r", "utf_8_sig" ) as file_obj:
        for i in file_obj:
            text += i

    soup = BeautifulSoup(text)

    movie_link = soup.find_all('span', {'class': 'extended-text__full'})

    for i in range(len(movie_link)):
        arr.append(re.sub(r'[°:()<>A-Za-z]','',movie_link[i].text.lower()))

    movie_link_prem1 = ''
    movie_link_prem2 = []
    movie_link_prem2_2 = ''

    try:
        movie_link_prem1 += soup.find('span', {'class': 'text-cut2'}).text
        movie_link_prem2.append(soup.find_all('li', {'class': 'key-value__item'}))
        print(3)
    except Exception as e:
        print()

    try:
        for i in movie_link_prem2[0]:
            movie_link_prem2_2 += (i.text + '\n')
    except Exception as e:
        movie_link_prem2_2 += 'Нет данных!'

    for i in arr:
        temp_value.append(i.split(' '))

    print(4)
    for i in range(len(temp_value)):
        for j in range(len(temp_value[i])):
            try:
                if int(temp_value[i][j][0:2]) :
                    if len(temp_value[i][j]) > 6:
                        arr_1.append(float(temp_value[i][j]))
            except Exception as e:
                continue

    input_prem = re.sub(r'✓ ','',movie_link[0].text)
    input_prem = re.sub(r'Скрыть', '', input_prem)
    input_prem1_1 = (movie_link_prem1 + '\n' + movie_link_prem2_2 + '\n')
    input_ds = arr_1[0]
    input_hs = arr_1[1]

    write_db(city, input_ds, input_hs, input_prem, input_prem1_1)
    print(city, input_ds, input_hs, input_prem, input_prem1_1)
    print(5)
    dt = read_db(city)

    request_data = {'s': dt[0],
                    'd': float(dt[1]),
                    'h': float(dt[2]),
                    'p': re.sub(r'-', ' ', dt[3]),
                    'p1': re.sub(r'-', ' ', dt[4])}

    return json.dumps(request_data)

def code(data):
    data = data.decode('utf-8')
    input_data = re.sub(r'[^а-яА-ЯЁё]','',data)
    return input_data

def write_db(city, sh, dg, prem, prem1):
    value = "INSERT INTO maps_data (city, sh, dg, prem, prem1) VALUES ('{0}', {1}, {2}, '{3}', '{4}');".format(str(city), float(sh), float(dg), str(prem), str(prem1))
    cursor.execute(value)
    conn.commit()

def read_db(city):
    cursor.execute("SELECT * FROM maps_data")
    db_data = []
    for i in range(10):
        row = cursor.fetchone()
        if type(row) == type(tuple()):
            db_data.append(row)

    for j in range(len(db_data)):
        if db_data[j][0] == city:
            return db_data[j]

@app.route('/api/v1.0/city', methods=['POST'])
def get_city():
    data = request.data
    reqves = request_yandex(code(data))

    return reqves

@app.route('/api/v1.0/city/del', methods=['POST'])
def del_city():
    data_del = request.data
    i = "DELETE FROM maps_data WHERE city = '{}'".format(str(code(data_del)))
    cursor.execute(i)
    conn.commit()

    cursor.execute("SELECT * FROM maps_data")
    db_data = []

    for i in range(11):
        row = cursor.fetchone()
        if type(row) == type(tuple()):
            db_data.append(row)

    arr = {'s': [],
           'd': [],
           'h': [],
           'p': [],
           'p1': []}

    for i in db_data:
        arr['s'].append(i[0])
        arr['d'].append(i[1])
        arr['h'].append(i[2])
        arr['p'].append(i[3])
        arr['p1'].append(i[4])

    return json.dumps(arr)

if __name__ == '__main__':
    app.run(debug=False)
