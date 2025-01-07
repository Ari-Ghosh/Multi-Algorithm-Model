import numpy as np
import pandas as pd

# BOLLINGER BANDS CALCULATION
def sma(data, lookback):
    sma = data.rolling(lookback).mean()
    return sma

def get_bb(data, lookback):
    std = data.rolling(lookback).std()
    upper_bb = sma(data, lookback) + std * 2
    lower_bb = sma(data, lookback) - std * 2
    middle_bb = sma(data, lookback)
    return upper_bb, lower_bb, middle_bb

# STOCHASTIC OSCILLATOR CALCULATION
def get_stoch_osc(high, low, close, k_lookback, d_lookback):
    lowest_low = low.rolling(k_lookback).min()
    highest_high = high.rolling(k_lookback).max()
    k_line = ((close - lowest_low) / (highest_high - lowest_low)) * 100
    d_line = k_line.rolling(d_lookback).mean()
    return k_line, d_line

# TRADING STRATEGY
def bb_stoch_strategy(prices, k, d, upper_bb, lower_bb):
    buy_price = []
    sell_price = []
    bb_stoch_signal = []
    signal = 0
    
    for i in range(len(prices)):
        if k[i-1] > 30 and d[i-1] > 30 and k[i] < 30 and d[i] < 30 and prices[i] < lower_bb[i]:
            if signal != 1:
                buy_price.append(prices[i])
                sell_price.append(np.nan)
                signal = 1
                bb_stoch_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                bb_stoch_signal.append(0)
        elif k[i-1] < 70 and d[i-1] < 70 and k[i] > 70 and d[i] > 70 and prices[i] > upper_bb[i]:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(prices[i])
                signal = -1
                bb_stoch_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                bb_stoch_signal.append(0)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            bb_stoch_signal.append(0)
    
    sell_price[-1] = prices[-1]
    bb_stoch_signal[-1] = -1
    return buy_price, sell_price, bb_stoch_signal

def get_bb_stoch_signal(data):
    data['upper_bb'], data['middle_bb'], data['lower_bb'] = get_bb(data['Close'], 20)
    data = data.dropna()
    data['%k'], data['%d'] = get_stoch_osc(data['High'], data['Low'], data['Close'], 14, 3)
    buy_price, sell_price, bb_stoch_signal = bb_stoch_strategy(data['Close'], data['%k'], data['%d'], 
                                                                data['upper_bb'], data['lower_bb'])
    
    data['buy_price'] = buy_price
    data['sell_price'] = sell_price

    # POSITION
    position = []
    for i in range(len(bb_stoch_signal)):
        if bb_stoch_signal[i] > 1:
            position.append(0)
        else:
            position.append(1)
            
    for i in range(len(data['Close'])):
        if bb_stoch_signal[i] == 1:
            position[i] = 1
        elif bb_stoch_signal[i] == -1:
            position[i] = 0
        else:
            position[i] = position[i-1]
        

    data["bb_stoch_signal"] = pd.DataFrame(bb_stoch_signal).rename(columns = {0:'bb_stoch_signal'}).set_index(data.index)
    data["position"] = pd.DataFrame(position).rename(columns = {0:'bb_stoch_position'}).set_index(data.index)
    
    return data