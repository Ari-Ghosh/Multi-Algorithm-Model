import pandas as pd
import numpy as np


# STOCHASTIC OSCILLATOR CALCULATION
def get_stoch_osc(high, low, close, k_lookback, d_lookback):
    lowest_low = low.rolling(k_lookback).min()
    highest_high = high.rolling(k_lookback).max()
    k_line = ((close - lowest_low) / (highest_high - lowest_low)) * 100
    d_line = k_line.rolling(d_lookback).mean()
    return k_line, d_line

# MACD CALCULATION
def get_macd(price, slow, fast, smooth):
    exp1 = price.ewm(span = fast, adjust = False).mean()
    exp2 = price.ewm(span = slow, adjust = False).mean()
    macd = pd.DataFrame(exp1 - exp2).rename(columns = {'close':'macd'})
    signal = pd.DataFrame(macd.ewm(span = smooth, adjust = False).mean()).rename(columns = {'macd':'signal'})
    hist = pd.DataFrame(macd['macd'] - signal['signal']).rename(columns = {0:'hist'})
    return macd, signal, hist


# TRADING STRATEGY
def implement_stoch_macd_strategy(prices, k, d, macd, macd_signal):    
    buy_price = []
    sell_price = []
    stoch_macd_signal = []
    signal = 0

    for i in range(len(prices)):
        if k[i] < 30 and d[i] < 30 and macd[i] < -2 and macd_signal[i] < -2:
            if signal != 1:
                buy_price.append(prices[i])
                sell_price.append(np.nan)
                signal = 1
                stoch_macd_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                stoch_macd_signal.append(0)
                
        elif k[i] > 70 and d[i] > 70 and macd[i] > 2 and macd_signal[i] > 2:
            if signal != -1 and signal != 0:
                buy_price.append(np.nan)
                sell_price.append(prices[i])
                signal = -1
                stoch_macd_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                stoch_macd_signal.append(0)
        
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            stoch_macd_signal.append(0)
            
    return buy_price, sell_price, stoch_macd_signal

def get_stoch_macd_signal(data):
    data['%k'], data['%d'] = get_stoch_osc(data['High'], data['Low'], data['Close'], 14, 3)
    data['macd'] = get_macd(data['Close'], 26, 12, 9)[0]
    data['macd_signal'] = get_macd(data['Close'], 26, 12, 9)[1]
    data['macd_hist'] = get_macd(data['Close'], 26, 12, 9)[2]
    data = data.dropna()   
    buy_price, sell_price, stoch_macd_signal = implement_stoch_macd_strategy(data['Close'], data['%k'], data['%d'], data['macd'], data['macd_signal'])

    print("Buy Signal: ", buy_price)
    print("Sell Signal: ", sell_price)

    # POSITION
    position = []
    for i in range(len(stoch_macd_signal)):
        if stoch_macd_signal[i] > 1:
            position.append(0)
        else:
            position.append(1)
            
    for i in range(len(data['Close'])):
        if stoch_macd_signal[i] == 1:
            position[i] = 1
        elif stoch_macd_signal[i] == -1:
            position[i] = 0
        else:
            position[i] = position[i-1]

    data["stoch_macd_signal"] = pd.DataFrame(stoch_macd_signal).rename(columns = {0:'stoch_macd_signal'}).set_index(data.index)
    data["position"] = pd.DataFrame(position).rename(columns = {0:'stoch_macd_position'}).set_index(data.index)
    
    return data