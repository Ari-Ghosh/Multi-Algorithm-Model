import yfinance as yf
import pandas as pd
import numpy as np
from src.ADX_RSI import get_adx_rsi_signal
from src.BollingerBands_KeltnerChannel_RSI import get_bb_rc_rsi_signal
from src.BollingerBands_Stochastic import get_bb_stoch_signal
from src.Stochastics_MACD import get_stoch_macd_signal
from src.SuperTrend import get_st_signal
from src.WilliamsR_MACD import get_wr_macd_signal
from src.OBV_MACD_RSI import get_obv_macd_rsi_signal
import os

def get_historical_data(symbol, start_date):
    df = yf.download(symbol, start=start_date)
    df = df[['High', 'Low', 'Close', 'Volume']]
    df.columns = ['High', 'Low', 'Close', 'Volume']
    return df

if __name__ == '__main__':
    tickers = [
        'ADANIENT.NS', 'ADANIPORTS.NS', 'APOLLOHOSP.NS', 'ASIANPAINT.NS', 'AXISBANK.NS', 'BAJAJ-AUTO.NS', 'BAJFINANCE.NS', 'BAJAJFINSV.NS', 'BEL.NS', 'BPCL.NS', 'BHARTIARTL.NS', 
        'BRITANNIA.NS', 'CIPLA.NS', 'COALINDIA.NS', 'DRREDDY.NS', 'EICHERMOT.NS', 'GRASIM.NS', 'HCLTECH.NS', 'HDFCBANK.NS', 'HDFCLIFE.NS', 'HEROMOTOCO.NS', 'HINDALCO.NS', 'HINDUNILVR.NS',
        'ICICIBANK.NS', 'ITC.NS', 'INDUSINDBK.NS', 'INFY.NS', 'JSWSTEEL.NS', 'KOTAKBANK.NS', 'LT.NS', 'M&M.NS', 'MARUTI.NS', 'NTPC.NS', 'NESTLEIND.NS', 'ONGC.NS', 'POWERGRID.NS', 'RELIANCE.NS',
        'SBILIFE.NS', 'SHRIRAMFIN.NS', 'SBIN.NS', 'SUNPHARMA.NS', 'TCS.NS', 'TATACONSUM.NS', 'TATAMOTORS.NS', 'TATASTEEL.NS', 'TECHM.NS', 'TITAN.NS', 'TRENT.NS', 'ULTRACEMCO.NS', 'WIPRO.NS'   
    ]

    start_date = '2020-01-01'

    for ticker in tickers:
        data = get_historical_data(ticker, start_date)
        
        print("Processing data for", ticker)

        folder_path = f'data/{ticker}'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        adx_rsi_data = get_adx_rsi_signal(data)
        adx_rsi_data.to_csv(f'data/{ticker}/adx_rsi_data.csv')
        bb_rc_rsi_data = get_bb_rc_rsi_signal(data)
        bb_rc_rsi_data.to_csv(f'data/{ticker}/bb_rc_rsi_data.csv')
        bb_stoch_data = get_bb_stoch_signal(data)
        bb_stoch_data.to_csv(f'data/{ticker}/bb_stoch_data.csv')
        stoch_macd_data = get_stoch_macd_signal(data)
        stoch_macd_data.to_csv(f'data/{ticker}/stoch_macd_data.csv')
        st_data = get_st_signal(data)
        st_data.to_csv(f'data/{ticker}/st_data.csv')
        wr_macd_data = get_wr_macd_signal(data)
        wr_macd_data.to_csv(f'data/{ticker}/wr_macd_data.csv')
        obv_macd_rsi_data = get_obv_macd_rsi_signal(data)
        obv_macd_rsi_data.to_csv(f'data/{ticker}/obv_macd_rsi_data.csv')

    print("Data saved to CSV files.")