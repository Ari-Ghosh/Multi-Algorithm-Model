import yfinance as yf
import pandas as pd
import numpy as np
import csv
from src.ADX_RSI import get_adx_rsi_signal
from src.BollingerBands_KeltnerChannel_RSI import get_bb_rc_rsi_signal
from src.BollingerBands_Stochastic import get_bb_stoch_signal
from src.Stochastics_MACD import get_stoch_macd_signal
from src.SuperTrend import get_st_signal
from src.WilliamsR_MACD import get_wr_macd_signal

def get_historical_data(symbol, start_date):
    df = yf.download(symbol, start=start_date)
    df = df[['High', 'Low', 'Close']]
    df.columns = ['High', 'Low', 'Close']
    return df

if __name__ == '__main__':
    ticker = 'TCS.NS'
    start_date = '2020-01-01'

    data = get_historical_data(ticker, start_date)

    adx_rsi_data = get_adx_rsi_signal(data)
    adx_rsi_data.to_csv('data/adx_rsi_data.csv')
    bb_rc_rsi_data = get_bb_rc_rsi_signal(data)
    bb_rc_rsi_data.to_csv('data/bb_rc_rsi_data.csv')
    bb_stoch_data = get_bb_stoch_signal(data)
    bb_stoch_data.to_csv('data/bb_stoch_data.csv')
    stoch_macd_data = get_stoch_macd_signal(data)
    stoch_macd_data.to_csv('data/stoch_macd_data.csv')
    st_data = get_st_signal(data)
    st_data.to_csv('data/st_data.csv')
    wr_macd_data = get_wr_macd_signal(data)
    wr_macd_data.to_csv('data/wr_macd_data.csv')

    print("Data saved to CSV files.")