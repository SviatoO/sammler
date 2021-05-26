import os
import re
import types
import telebot
from telebot import types
import configparser
import mysql.connector as msql
from flask import Flask, request
import sammler_collector as sammler
import plot

KEY_NAMES = []
SYSTEM_KEY_NAMES = []
EXISTING_TABLES = []

config = configparser.ConfigParser()
config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'configuration.ini')
config.read(config_file)

DATABASE_SERVER = config["DATABASE"]["DATABASE_SERVER"]
DATABASE_NAME = config["DATABASE"]["DATABASE_NAME"]
DATABASE_USERNAME = config["DATABASE"]["DATABASE_USERNAME"]
DATABASE_PASSWORD = config["DATABASE"]["DATABASE_PASSWORD"]
db_connection = msql.connect(host=DATABASE_SERVER, user=DATABASE_USERNAME, password=DATABASE_PASSWORD, database=DATABASE_NAME)


app = Flask(__name__)
bot = telebot.TeleBot(config["TELEGRAM_BOT"]["BOT_TOKEN"])
bot.set_webhook(url="https://e056d19ed073.ngrok.io")

@app.route('/', methods=['POST'])
def webhook():
    bot.process_new_updates(
        [telebot.types.Update.de_json(request.stream.read().decode("utf-8"))]
    )
    return "ok"
@app.route('/', methods=['POST', 'GET'])
def hello_world():
    return 'Hello World!'


counter = 0

for table in sammler.get_tables(db_connection):
    EXISTING_TABLES.append(table)
    table_acronym = table.replace('_USD_DATA', '')
    SYSTEM_KEY_NAMES.append('key_'+table_acronym)
    KEY_NAMES.append(table_acronym)

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, 'Hello 👋\nMy name is Sammler and I can show you basic data about cryptocurrency 🪙')
@bot.message_handler(commands=['coin'])
def set_coin(message):
    #bot.send_message(message.chat.id, 'Please sellect currency👋')
    bot_keyboard = types.InlineKeyboardMarkup()
    for i in range(len(SYSTEM_KEY_NAMES)):
        SYSTEM_KEY_NAMES[i] = types.InlineKeyboardButton(text=KEY_NAMES[i], callback_data=KEY_NAMES[i])
        bot_keyboard.add(SYSTEM_KEY_NAMES[i])
    bot.send_message(message.chat.id, text='Please sellect currency', reply_markup=bot_keyboard)

photo = open('Desktop/CryproBoard/Sammler/sammler-0.2/images/plot_to_send', 'rb')

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    for table in KEY_NAMES:
        if call.data == table:
            sammler.check_table_availability(db_connection, table+'_USD_DATA', DATABASE_NAME)
            sammler.write_data_to_sql(table, config['COIN_API']['API_TOKEN'], table+'_USD_DATA', db_connection)
            plot.build_plot(table)
            message = 'Name: '+sammler.currency_name+'\n'+'Price USD: '+str(sammler.price_in_USD)+'\n'+'Market Capitalization USD: '+str(sammler.global_cap_in_USD)+'\n'+'Time: '+str(sammler.time_stamp)+'\n'
            bot.send_message(call.message.chat.id, message)
            bot.send_photo(call.message.chat.id, photo)
            plot.delete_image()
            
            
        
bot.polling()



if __name__ == "__main__":
    app.run(host=config['WEB_SERVER']['HOST'], port=config['WEB_SERVER']['PORT'])