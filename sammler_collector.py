import requests
import mysql.connector as msql
import schedule
from progress.bar import Bar
import configparser
import datetime
import time
import argparse
import getpass
import sys
import re
import os
import platform

class PasswordPromptAction(argparse.Action):
    def __init__(self,
             option_strings,
             dest=None,
             nargs=0,
             default=None,
             required=False,
             type=None,
             metavar=None,
             help=None):
        super(PasswordPromptAction, self).__init__(
             option_strings=option_strings,
             dest=dest,
             nargs=nargs,
             default=default,
             required=required,
             metavar=metavar,
             type=type,
             help=help)

    def __call__(self, parser, args, values, option_string=None):
        password = getpass.getpass()
        setattr(args, self.dest, password)
        
config = configparser.ConfigParser()
config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'configuration.ini')
config.read(config_file)

DATABASE_SERVER = config["DATABASE"]["DATABASE_SERVER"]
DATABASE_NAME = config["DATABASE"]["DATABASE_NAME"]
DATABASE_USERNAME = config["DATABASE"]["DATABASE_USERNAME"]

def get_tables(db_connection):
  EXISTING_TABLES = []
  showdb_query = 'SHOW TABLES FROM '+DATABASE_NAME+';'
  db_cursor = db_connection.cursor()
  db_cursor.execute(showdb_query)
  for (table_in_db,) in db_cursor:
    EXISTING_TABLES.append(table_in_db)
    
  return(EXISTING_TABLES)

def check_table_availability(db_connection, DATABASE_TABLE, DATABASE_NAME):
  EXISTING_TABLES = []
  TABLE_COUNTER = 0
  BOOL_TABLE = False
  showdb_query = 'SHOW TABLES FROM '+DATABASE_NAME+';'
  db_cursor = db_connection.cursor()
  db_cursor.execute(showdb_query)
  for (table_in_db,) in db_cursor:
    EXISTING_TABLES.append(table_in_db)
    TABLE_COUNTER += 1
  for table_name in range(TABLE_COUNTER):
    if DATABASE_TABLE == EXISTING_TABLES[table_name]:
      print('\nGreat! The table with name: '+DATABASE_TABLE+' exists\n')
      BOOL_TABLE = True
  if BOOL_TABLE == False :
    print('\nTable with name: '+DATABASE_TABLE+' not exist\n')
    print('Create the table with name '+DATABASE_TABLE+'\n')
    create_table_query = 'CREATE TABLE IF NOT EXISTS '+DATABASE_TABLE+'( Number INT AUTO_INCREMENT PRIMARY KEY, Name VARCHAR(255) NOT NULL, Price_USD FLOAT NOT NULL, Market_Capitalization_USD FLOAT NOT NULL, Date_Stamp VARCHAR(255) NOT NULL) ENGINE=INNODB;'
    table_cursor = db_connection.cursor()
    table_cursor.execute(create_table_query)
    print('Table with name: '+DATABASE_TABLE+' was created!\n')

def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"

def success_notification():
  os_details = platform.platform()
  if re.search(r'\bmacOS\b', str(os_details)):
    os.system('afplay success_login.wav&')
  elif re.search(r'\bLinux\b', str(os_details)):
    os.system('aplay success_login.wav&')

price_in_USD = 0

def write_data_to_sql(currency, token, DATABASE_TABLE, db_connection):
  #API Call 
  global_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol='+currency+'&convert=USD'
  headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': token,
  }
  request = requests.get(global_url, headers=headers)
  results = request.json()

  ERROR_CODE = results['status']['error_code']
  if ERROR_CODE != 0:
    print('\nError code: '+str(ERROR_CODE))
    print(results['status']['error_message'])
    sys.exit()

  global currency_name
  global price_in_USD
  global global_cap_in_USD
  global time_stamp
  currency_name = results['data'][currency]['name']
  price_in_USD = results['data'][currency]['quote']['USD']['price']
  global_cap_in_USD = results['data'][currency]['quote']['USD']['market_cap']
  now = datetime.datetime.now()
  time_stamp = now.strftime("%Y-%m-%d %H:%M:%S")
  print(currency_name)

  sql_query = "INSERT INTO " + str(DATABASE_TABLE) + "(Name, Price_USD, Market_Capitalization_USD, Date_Stamp) VALUES (%s, %s, %s, %s)"
  sql_values = (currency_name, toFixed(price_in_USD, 3), toFixed(global_cap_in_USD, 3), time_stamp)
  db_cursor = db_connection.cursor()
  db_cursor.execute(sql_query, sql_values)
  db_connection.commit()

