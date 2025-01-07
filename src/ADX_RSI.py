import pandas as pd
import numpy as np

# ADX CALCULATION
def get_adx(high, low, close, lookback):
    plus_dm = high.diff()
    minus_dm = low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0
    
    tr1 = pd.DataFrame(high - low)
    tr2 = pd.DataFrame(abs(high - close.shift(1)))
    tr3 = pd.DataFrame(abs(low - close.shift(1)))
    frames = [tr1, tr2, tr3]
    tr = pd.concat(frames, axis = 1, join = 'inner').max(axis = 1)
    atr = tr.rolling(lookback).mean()
    
    plus_di = 100 * (plus_dm.ewm(alpha = 1/lookback).mean() / atr)
    minus_di = abs(100 * (minus_dm.ewm(alpha = 1/lookback).mean() / atr))
    dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100
    adx = ((dx.shift(1) * (lookback - 1)) + dx) / lookback
    adx_smooth = adx.ewm(alpha = 1/lookback).mean()
    return plus_di, minus_di, adx_smooth

# RSI CALCULATION
def get_rsi(close, lookback):
    ret = close.diff()
    up = []
    down = []
    
    for i in range(len(ret)):
        if ret[i] < 0:
            up.append(0)
            down.append(ret[i])
        else:
            up.append(ret[i])
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
def adx_rsi_strategy(prices, adx, pdi, ndi, rsi):
    buy_price = []
    sell_price = []
    adx_rsi_signal = []
    signal = 0
    
    for i in range(len(prices)):
        if adx[i] > 35 and pdi[i] < ndi[i] and rsi[i] < 50:
            if signal != 1:
                buy_price.append(prices[i])
                sell_price.append(np.nan)
                signal = 1
                adx_rsi_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                adx_rsi_signal.append(0)
                
        elif adx[i] > 35 and pdi[i] > ndi[i] and rsi[i] > 50:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(prices[i])
                signal = -1
                adx_rsi_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                adx_rsi_signal.append(0)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            adx_rsi_signal.append(0)
                        
    return buy_price, sell_price, adx_rsi_signal


def get_adx_rsi_signal(data):
    plus_di, minus_di, adx = get_adx(data['High'], data['Low'], data['Close'], 14)
    print(plus_di)
    print(minus_di)
    print(adx)
    data['plus_di'] = plus_di
    data['minus_di'] = minus_di
    data['adx'] = adx
    data = data.dropna()

    data['rsi_14'] = get_rsi(data['Close'], 14)
    data = data.dropna()

    buy_price, sell_price, adx_rsi_signal = adx_rsi_strategy(data['Close'], data['adx'], data['plus_di'], data['minus_di'], data['rsi_14'])
    
    print("Buy Price: ", buy_price)
    print("Sell Price: ", sell_price)

    # POSITION
    position = []
    for i in range(len(adx_rsi_signal)):
        if adx_rsi_signal[i] > 1:
            position.append(1)
        else:
            position.append(0)
            
    for i in range(len(data['Close'])):
        if adx_rsi_signal[i] == 1:
            position[i] = 1
        elif adx_rsi_signal[i] == -1:
            position[i] = 0
        else:
            position[i] = position[i-1]
            
    data['adx_rsi_signal'] = adx_rsi_signal
    data['position'] = position

    return data