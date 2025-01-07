import yfinance as yf
import pandas as pd
import numpy as np
from src.ADX_RSI import get_adx_rsi_signal
from src.BollingerBands_KeltnerChannel_RSI import get_bb_rc_rsi_signal
from src.BollingerBands_Stochastic import get_bb_stoch_signal
from src.Stochastics_MACD import get_stoch_macd_signal
from src.SuperTrend import get_st_signal
from src.WilliamsR_MACD import get_wr_macd_signal

def get_historical_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

if __name__ == '__main__':
    ticker = 'TCS.NS'
    start_date = '2020-01-01'
    end_date = '2025-01-01'
    data = get_historical_data(ticker, start_date, end_date)
    data = pd.DataFrame(data)
    print(data.head())
    print(data.tail())
    print(data.shape)
    adx_rsi_data = get_adx_rsi_signal(data)
    print(adx_rsi_data.head())
    print(adx_rsi_data.tail())
    print(adx_rsi_data.shape)