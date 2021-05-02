import json
import requests
import mysql.connector as msql
import datetime
import time
import threading

#Connect to MySQL Server host 34.66.112.81 port 3306
DATABASE_SERVER = '35.192.200.165'
DATABASE_NAME = 'CRYPTO_MAIN_DATA'
DATABASE_USERNAME = 'opsadmin'
DATABASE_PASSWORD = 'labNULP!21'
db_connection = msql.connect(host=DATABASE_SERVER, user=DATABASE_USERNAME, password=DATABASE_PASSWORD, database=DATABASE_NAME)
print(db_connection)
sql_query = "INSERT IN TO BTC_USD_DATA (Name, Price_USD, Market_Capitalization_USD, Date_Stamp)"


def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"

def write_data_to_sql():

  #API Call 
  global_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol=BTC&convert=USD'
  headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': 'ec439c57-2a67-4b54-8195-d47115e35155',
  }
  request = requests.get(global_url, headers=headers)
  results = request.json()

  currency_name = results['data']['BTC']['name']
  last_updated = results['data']['BTC']['last_updated']
  price_in_USD = results['data']['BTC']['quote']['USD']['price']
  global_cap_in_USD = results['data']['BTC']['quote']['USD']['market_cap']
  now = datetime.datetime.now()
  time_stamp = now.strftime("%Y-%m-%d %H:%M:%S")

  sql_query = "INSERT INTO BTC_USD_DATA (Name, Price_USD, Market_Capitalization_USD, Date_Stamp) VALUES (%s, %s, %s, %s)"
  sql_values = (currency_name, toFixed(price_in_USD, 3), toFixed(global_cap_in_USD, 3), time_stamp)
  db_cursor = db_connection.cursor()
  db_cursor.execute(sql_query, sql_values)
  db_connection.commit()

#write_data_to_sql()

#start_time = time.time()


def admin_menu():
  print('   _____                           __         ')
  print('  / ___/____ _____ ___  ____ ___  / /__  _____')
  print('  \__ \/ __ `/ __ `__ \/ __ `__ \/ / _ \/ ___/')
  print(' ___/ / /_/ / / / / / / / / / / / /  __/ /    ')
  print('/____/\__,_/_/ /_/ /_/_/ /_/ /_/_/\___/_/     ')
  print('                                              ')

admin_menu()

#while True:
#  write_data_to_sql()
#  time.sleep(1200.0 - ((time.time() - start_time) % 1200.0))

