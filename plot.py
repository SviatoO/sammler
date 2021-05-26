import requests
import pandas as pd
import numpy as np
import datetime as dt
import plotly.graph_objects as go
import configparser
import plotly.io as pio
import os

global dir_path
dir_path = os.path.dirname(os.path.realpath(__file__))
config = configparser.ConfigParser()
config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'configuration.ini')
config.read(config_file)

def build_plot(currency):

    url = 'https://rest.coinapi.io/v1/ohlcv/BITSTAMP_SPOT_'+currency+'_USD/latest?period_id=15MIN'
    headers = {'X-CoinAPI-Key' : config["COIN_API"]["PLOT_COIN_API"]}
    response = requests.get(url, headers=headers)

    data = pd.read_json(response.text, orient='records', dtype={
        'time_close': np.datetime64,
        'time_open': np.datetime64,
        'time_period_end': np.datetime64,
        'time_period_start': np.datetime64,
    })
    data.drop(['trades_count', 'time_open', 'time_close', 'volume_traded'], axis= 'columns', inplace=True)
    data.head()

    figure = go.Figure(
        data = [go.Candlestick(
            x = data['time_period_end'],
            low = data['price_low'],
            high = data['price_high'],
            close = data['price_close'],
            open = data['price_open'],
            increasing_line_color = 'green',
            decreasing_line_color = 'red'
        )
        ]
    )

    #figure.show()
    pio.write_image(figure, dir_path+'/images/plot_to_send', format='png')
   
def delete_image():
    os.remove(dir_path+'/images/plot_to_send.png')