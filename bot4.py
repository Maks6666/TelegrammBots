# import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
# from aiogram.types import ParseMode

import logging
import spacy
import sqlite3
import os 

logging.basicConfig(level=logging.INFO)

bot = Bot('6409023209:AAE07CHYdHEczafUumAhnkMxjNkZyWvr0Sw')

dp = Dispatcher(bot)



dp.middleware.setup(LoggingMiddleware())

# Загружаем языковую модель spaCy для английского языка
nlp = spacy.load("en_core_web_sm")

async def get_user_db(user_id):
      return f"user_{user_id}.db"

user_data = {}
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    db_name = await get_user_db(user_id)  
    if not os.path.exists(db_name):
        conn = sqlite3.connect(db_name)  
        user_data[user_id] = {}
        user_data[user_id]['db_name'] = db_name  # Сохраняем имя базы данных в user_data
        cur = conn.cursor()

        cur.execute('''CREATE TABLE IF NOT EXISTS queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER, 
                    request_text TEXT,
                    result_text TEXT,
                    timestamp TIMESTAMP
                )''')
        conn.commit()
        # print("Table 'queries' created successfully.")
            
        cur.close()
        conn.close()
    user_data[user_id]['db_name'] = db_name 
    user_data[user_id]['user_id'] = user_id
    await message.answer("Hello! Input a sentence to find out it's parts of speech")

@dp.message_handler(content_types=['text'])
async def start(message: types.Message):
    text = message.text
    new_text = ''
    for char in text:
        if char.isalnum() or char.isspace():
            new_text += char

    doc = nlp(new_text)
    
    
    tokens = []
    for token in doc:
        tokens.append(f"Word: ' {token.text} ', Part of speech: '{token.pos_}'")
    result = "\n".join(tokens)


    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("History", callback_data='info'))

    await message.answer(result, reply_markup=markup)

    # markup = types.InlineKeyboardMarkup()
    # markup.add(types.InlineKeyboardButton("History", callback_data='history'))


#   definition: what is 'request_text' and 'result_text' for inserting them into table
#   in Telebot we put them as an arguments of function 
    request_text = message.text
    result_text = result
    user_id = message.from_user.id
    db_name = await get_user_db(user_id)  
    try:
        conn = sqlite3.connect(db_name)  
        cur = conn.cursor()
        cur.execute("INSERT INTO queries (user_id, request_text, result_text, timestamp) VALUES (?, ?, ?, datetime('now'))", (user_id, request_text, result_text))

        conn.commit()

        cur.close()
        conn.close()
    except Exception as e:
         print("Error:", e)
    #    user_id = message.from_user.id
    # db_name = await get_user_db(user_id)  
    # conn = sqlite3.connect(db_name)  
    # cur = conn.cursor()

    # cur.execute('''CREATE TABLE IF NOT EXISTS queries (
    #             id INTEGER PRIMARY KEY AUTOINCREMENT,
    #             user_id INTEGER, 
    #             request_text TEXT,
    #             result_text TEXT,
    #             timestamp TIMESTAMP
    #         )''')
    # conn.commit()
    # # print("Table 'queries' created successfully.")
        
    # cur.close()
    # conn.close()

    
@dp.callback_query_handler(lambda c: c.data == 'info')
async def history(call):
    
    user_id = call.from_user.id
    db_name = user_data[user_id]['db_name']
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute("SELECT request_text, result_text, timestamp FROM queries WHERE user_id=?", (user_id,))
    history = cur.fetchall()


    info =""
    if not history:
        await call.answer("No query history found.")
    else:
        for row in history:
            info += f"Time: {row[2]}\n, Query: {row[0]}\n, Result: {row[1]}\n"
            chunks = [info[i:i+4000] for i in range(0, len(info), 4000)]
            
            for chunk in chunks:
                

                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("Сlear history", callback_data='clear'))

        await call.message.answer(chunk, reply_markup=markup)
    cur.close()
    conn.close()
   


    # with open("history.txt", "w") as file:
    #     file.write(info)

    # await message.answer_document(document=open("history.txt", "rb"), caption="История запросов")

    # await call.answer(info)


@dp.callback_query_handler(lambda c: c.data == 'clear')
async def clear(call):
    user_id = call.from_user.id
    db_name = user_data[user_id]['db_name']
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute("DELETE FROM queries")

    conn.commit()
    cur.close()
    conn.close()

    await call.message.answer("History is cleared. Continue please:) ")
    


executor.start_polling(dp)

# for photos, videos and etc...
# @dp.message_handler(content_types=['photo']

# to answer by photo or any file:
# file = open("/some.png", 'rb')
# await message.answer_photo(file)

# @dp.message_handler(content_types=['photo'])
# async def start(message: types.Message):
#     await bot.send_message(message.chat.id, 'Hello')
#     await message.answer("Hello 1")



# @dp.message_handler(commands=["inline"])
# async def start(message: types.Message):
#     markup = types.InlineKeyboardMarkup()
#     markup.add(types.InlineKeyboardButton("Site", url='https://www.president.gov.ua/ru'))
#     markup.add(types.InlineKeyboardButton("Hello", callback_data='hello'))
#     await message.reply('Hello', reply_markup=markup)




# @dp.callback_query_handler()
# async def callback(call):
#     await call.message.answer(call.data)



# @dp.message_handler(commands=['reply'])
# async def reply(message: types.Message):
#     markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
#     markup.add(types.KeyboardButton('Site'))
#     markup.add(types.KeyboardButton('Website'))
#     await message.answer('Hello', reply_markup=markup)


























# aiogram 3


# from aiogram import Bot, Dispatcher
# import asyncio
# from aiogram.types import Message
# import logging


# token='6564113207:AAEkY7LHbOEp-WYt83JC-bkM5rzG-Ze9yEE'


# async def start_bot(bot: Bot):
#     await bot.send_message(1117010229, text='Bot is working')


# async def stop_bot(bot: Bot):
#     await bot.send_message(1117010229, text='Bot is stopped')



# # formats of strings
# # async def get_start(message: Message, bot: Bot):
# #     await bot.send_message(message.from_user.id, f"<b>Hello, {message.from_user.id}, glad to see you!</b>")
# #     await message.answer(f"<s>Hello, {message.from_user.first_name}, glad to see you!</s>")
# #     await message.reply(f"<tg-spoiler>Hello, {message.from_user.first_name}, glad to see you!</tg-spoiler>")



# async def get_start(message: Message, bot: Bot):
#     await bot.send_message(message.from_user.id, f"Hello, {message.from_user.id}, glad to see you!")
#     await message.answer(f"Hello, {message.from_user.first_name}, glad to see you!")
#     await message.reply(f"Hello, {message.from_user.first_name}, glad to see you!")
#     await bot.send_message(message.chat.id, f"Информация о сообщении:\n\n{message}")


    
# async def start():
#     # remember it of u wanna to format strings
#     # bot = Bot(token=token, parse_mode='HTML')
#     logging.basicConfig(level=logging.INFO, 
#                         format="%(asctime)s - [%(levelname)s] - %(name)s - "
#                                 "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
#                         )
#     bot = Bot(token=token)





#     dp = Dispatcher()

#     dp.startup.register(start_bot)
#     dp.shutdown.register(stop_bot)
#     dp.message.register(get_start)
#     try:
#         await dp.start_polling(bot)
#     finally:
#         await bot.session.close()

# if __name__ =='__main__':
#     asyncio.run(start())