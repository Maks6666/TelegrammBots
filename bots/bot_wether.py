#Telegramm link to the bot: @TeleSynopticBot
#Before code running remember to download next pictures: sun.png, rain.png, srain.png, cloudd.png and suncloud.png and save them to "bots" directory or any directory you like 
#This bot is working without code running because of using PythonAnywhere platform

import telebot
import requests
import json
import sqlite3
from telebot import types
# import random

user_id = None 
# # Получение текущего рабочего каталога
# current_directory = os.getcwd()

# # Создание полного пути к изображению
# image_filename = 'sun.png'  # Имя вашего изображения
# image_path = os.path.join(current_directory, image_filename)

# print(f"Полный путь к изображению: {image_path}")


bot = telebot.TeleBot('{here is a place for bot personal token}')
# old API
# API = '3d9de74844d28377e81415151cbe6a66'
# New one
API = '205e6505f3d8f5e88f7a402125d4e477'
user_data = {}
def get_user_db(user_id):
      return f"user_{user_id}.db"

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Hi! Glad to see you:) Just input city name and calm down:)')
    
    
    
    user_id = message.from_user.id
      user_data[user_id] = {}
    db_name = get_user_db(user_id)

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT,
                
                temp REAL, 
                clouds INTEGER,
                rain REAL,
                city_name TEXT)
            ''')
    

    # to add any column to already created table (if u have problem like "table has no some column"), use that
    # but each new column which was created will be added to the end of table
    # so be carefull with indexes
    cur.execute('''PRAGMA table_info(weather_data)''')
    columns = cur.fetchall()
    has_rain_column = any(column[1] == 'rain' for column in columns)

    if not has_rain_column:
        # Если столбец rain не существует, добавляем его
        cur.execute('ALTER TABLE weather_data ADD COLUMN rain REAL')
    conn.commit()


    cur.execute('''PRAGMA table_info(weather_data)''')
    columns = cur.fetchall()
    has_rain_column = any(column[1] == 'city_name' for column in columns)

    if not has_rain_column:
        # Если столбец city_name не существует, добавляем его
        cur.execute('ALTER TABLE weather_data ADD COLUMN city_name TEXT')
    conn.commit()
# bot.send_message(message.chat.id, list1[x])
# list1 = ["1", "2", "3"]
# x = random.randint(1, 3)
# #'Hi! Glad to see you:) Just input city name and calm down:)'

@bot.message_handler(content_types=['text'])
def get_weather(message):
        user_id = message.from_user.id
        city = message.text.strip().lower()
        res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')
        if res.status_code == 200: #if status is existing 
            data = json.loads(res.text)
            temp = data["main"]["temp"]
            clouds = data["clouds"]["all"]
            if "rain" in data and "1h" in data["rain"]:
                rain = data["rain"]["1h"]
            else:
                rain = 0
            city_name = data.get("name", "")

            # rain = data["rain"]["1h"]
            if clouds < 50 and rain == 0:
                image = 'sun.png'
            elif clouds > 50 and rain > 0:
                image = 'rain.png'
            elif clouds < 50 and rain >= 0:
                image = 'srain.png'
            elif clouds > 50 and rain == 0:
                image = 'cloudd.png'
            else:
                image = 'sunrain.png'


            conn = sqlite3.connect(get_user_db(user_id))
            cur = conn.cursor()

            cur.execute('INSERT INTO weather_data (city, city_name, temp, clouds, rain) VALUES (?, ?, ?, ?, ?)', (city, city_name, temp, clouds, rain))
            conn.commit()
            cur.close()
            conn.close()
            # image = 'sun.png' if clouds < 50 else 'cloudd.png'

            
            file = open(image, 'rb')
            bot.send_photo(message.chat.id, file)
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton("History", callback_data="weather_data"))
            # markup.add(telebot.types.InlineKeyboardButton("Clear history", callback_data="clear_database"))
            # button added to next message
            bot.send_message(message.chat.id, f'Current temperature in {city_name}: {data["main"]["temp"]}°C \nClouds: {data["clouds"]["all"]}% \nRain {rain}%', reply_markup=markup)


            
            # file = open('bots/' + image, 'rb')
            # bot.send_photo(message.chat.id, file)
            # bot.reply_to(message, f'Current temperature: {data["main"]["temp"]}C \nClouds: { data["clouds"]["all"]} \nRain {rain}')
        else:
            bot.reply_to(message, "Sorry, id does not exist :( \nAtleast now😉")
   
# info, which button returnes
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

      user_id = call.from_user.id  
      if call.data == 'weather_data':
            conn = sqlite3.connect(get_user_db(user_id))
            cur = conn.cursor()

          
            cur.execute("SELECT * FROM weather_data")

            weather_data = cur.fetchall()

            info = ""
            for el in weather_data:
                info += f"City: {el[5]}, Temperature: {el[2]}°C, Clouds: {el[3]}%, Rain: {el[4]}% \n"


            cur.close()
            conn.close()
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton("Clear history", callback_data="clear_database"))
            bot.send_message(call.message.chat.id, info, reply_markup=markup)
        
      elif call.data == 'clear_database':
                conn = sqlite3.connect(get_user_db(user_id))
                cur = conn.cursor()

                #It cleares weather_data table
                cur.execute("DELETE FROM weather_data")

                conn.commit()
                cur.close()
                conn.close()

                bot.send_message(call.message.chat.id, "History is cleared. Continue please😁")
#to prevent timeout issue
bot.polling(interval=5)

