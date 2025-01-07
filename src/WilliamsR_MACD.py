import numpy as np
import pandas as pd

# WILLIAMS %R CALCULATION
def get_wr(high, low, close, lookback):
    highh = high.rolling(lookback).max() 
    lowl = low.rolling(lookback).min()
    wr = -100 * ((highh - close) / (highh - lowl))
    return wr

# MACD CALCULATION
def get_macd(price, slow, fast, smooth):
    exp1 = price.ewm(span = fast, adjust = False).mean()
    exp2 = price.ewm(span = slow, adjust = False).mean()
    macd = pd.DataFrame(exp1 - exp2).rename(columns = {'close':'macd'})
    signal = pd.DataFrame(macd.ewm(span = smooth, adjust = False).mean()).rename(columns = {'macd':'signal'})
    hist = pd.DataFrame(macd['macd'] - signal['signal']).rename(columns = {0:'hist'})
    return macd, signal, hist

# TRADING STRATEGY
def implement_wr_macd_strategy(prices, wr, macd, macd_signal):    
    buy_price = []
    sell_price = []
    wr_macd_signal = []
    signal = 0

    for i in range(len(wr)):
        if wr[i-1] > -50 and wr[i] < -50 and macd[i] > macd_signal[i]:
            if signal != 1:
                buy_price.append(prices[i])
                sell_price.append(np.nan)
                signal = 1
                wr_macd_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                wr_macd_signal.append(0)
                
        elif wr[i-1] < -50 and wr[i] > -50 and macd[i] < macd_signal[i]:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(prices[i])
                signal = -1
                wr_macd_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                wr_macd_signal.append(0)
        
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            wr_macd_signal.append(0)
            
    return buy_price, sell_price, wr_macd_signal

def get_wr_macd_signal(data):
    data['wr_14'] = get_wr(data['High'], data['Low'], data['Close'], 14)
    data['macd'] = get_macd(data['Close'], 26, 12, 9)[0]
    data['macd_signal'] = get_macd(data['Close'], 26, 12, 9)[1]
    data['macd_hist'] = get_macd(data['Close'], 26, 12, 9)[2]
    data = data.dropna()
    buy_price, sell_price, wr_macd_signal = implement_wr_macd_strategy(data['Close'], data['wr_14'], data['macd'], data['macd_signal'])

    print("Buy Price: ", buy_price)
    print("Sell Price: ", sell_price)

    # POSITION
    position = []
    for i in range(len(wr_macd_signal)):
        if wr_macd_signal[i] > 1:
            position.append(0)
        else:
            position.append(1)
            
    for i in range(len(data['Close'])):
        if wr_macd_signal[i] == 1:
            position[i] = 1
        elif wr_macd_signal[i] == -1:
            position[i] = 0
        else:
            position[i] = position[i-1]

    data["wr_macd_signal"] = pd.DataFrame(wr_macd_signal).rename(columns = {0:'wr_macd_signal'}).set_index(data.index)
    data["position"] = pd.DataFrame(position).rename(columns = {0:'wr_macd_position'}).set_index(data.index)
