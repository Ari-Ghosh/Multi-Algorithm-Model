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
    return upper_bb, middle_bb, lower_bb

# KELTNER CHANNEL CALCULATION
def get_kc(high, low, close, kc_lookback, multiplier, atr_lookback):
    tr1 = pd.DataFrame(high - low)
    tr2 = pd.DataFrame(abs(high - close.shift()))
    tr3 = pd.DataFrame(abs(low - close.shift()))
    frames = [tr1, tr2, tr3]
    tr = pd.concat(frames, axis = 1, join = 'inner').max(axis = 1)
    atr = tr.ewm(alpha = 1/atr_lookback).mean()
    
    kc_middle = close.ewm(kc_lookback).mean()
    kc_upper = close.ewm(kc_lookback).mean() + multiplier * atr
    kc_lower = close.ewm(kc_lookback).mean() - multiplier * atr
    
    return kc_middle, kc_upper, kc_lower

# RSI CALCULATION
def get_rsi(close, lookback):
    ret = close.diff()
    up = []
    down = []
    for i in range(len(ret)):
        if ret.iloc[i] < 0:
            up.append(0)
            down.append(ret.iloc[i])
        else:
            up.append(ret.iloc[i])
            down.append(0)
    up_series = pd.Series(up)
    down_series = pd.Series(down).abs()
    up_ewm = up_series.ewm(com = lookback - 1, adjust = False).mean()
    down_ewm = down_series.ewm(com = lookback - 1, adjust = False).mean()
    rs = up_ewm/down_ewm
    rsi = 100 - (100 / (1 + rs))
    rsi_df = pd.DataFrame(rsi).rename(columns = {0:'rsi'}).set_index(close.index)
    rsi_df = rsi_df.dropna()
    return rsi_df[3:]

# TRADING STRATEGY
def bb_kc_rsi_strategy(prices, upper_bb, lower_bb, kc_upper, kc_lower, rsi):
    buy_price = []
    sell_price = []
    bb_kc_rsi_signal = []
    signal = 0
    
    for i in range(len(prices)):
        if lower_bb[i] < kc_lower[i] and upper_bb[i] > kc_upper[i] and rsi[i] < 30:
            if signal != 1:
                buy_price.append(prices[i])
                sell_price.append(np.nan)
                signal = 1
                bb_kc_rsi_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                bb_kc_rsi_signal.append(0)
                
        elif lower_bb[i] < kc_lower[i] and upper_bb[i] > kc_upper[i] and rsi[i] > 70:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(prices[i])
                signal = -1
                bb_kc_rsi_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                bb_kc_rsi_signal.append(0)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            bb_kc_rsi_signal.append(0)
                        
    return buy_price, sell_price, bb_kc_rsi_signal

def get_bb_rc_rsi_signal(data):                                                           
    data['upper_bb'], data['middle_bb'], data['lower_bb'] = get_bb(data['Close'], 20)
    data['kc_middle'], data['kc_upper'], data['kc_lower'] = get_kc(data['High'], data['Low'], data['Close'], 20, 2, 10)
    data['rsi_14'] = get_rsi(data['Close'], 14)
    data = data.dropna()
    buy_price, sell_price, bb_kc_rsi_signal = bb_kc_rsi_strategy(data['Close'], data['upper_bb'], data['lower_bb'],
                                                            data['kc_upper'], data['kc_lower'], data['rsi_14'])
    
    data['buy_price'] = buy_price
    data['sell_price'] = sell_price

    # POSITION
    position = []
    for i in range(len(bb_kc_rsi_signal)):
        if bb_kc_rsi_signal[i] > 1:
            position.append(0)
        else:
            position.append(1)
            
    for i in range(len(data['Close'])):
        if bb_kc_rsi_signal[i] == 1:
            position[i] = 1
        elif bb_kc_rsi_signal[i] == -1:
            position[i] = 0
        else:
            position[i] = position[i-1]
        

    data["bb_kc_rsi_signal"] = pd.DataFrame(bb_kc_rsi_signal).rename(columns = {0:'bb_kc_rsi_signal'}).set_index(data.index)
    data["position"] = pd.DataFrame(position).rename(columns = {0:'bb_kc_rsi_position'}).set_index(data.index)
    
    return data

