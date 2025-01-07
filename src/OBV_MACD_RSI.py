import pandas as pd
import numpy as np

# OBV CALCULATION
def get_obv(close, volume):
    obv = [0]
    for i in range(1, len(close)):
        if close[i] > close[i-1]:
            obv.append(obv[-1] + volume[i])
        elif close[i] < close[i-1]:
            obv.append(obv[-1] - volume[i])
        else:
            obv.append(obv[-1])
    return pd.Series(obv, index=close.index)

# MACD CALCULATION
def get_macd(close, fast_period=12, slow_period=26, signal_period=9):
    ema_fast = close.ewm(span=fast_period, adjust=False).mean()
    ema_slow = close.ewm(span=slow_period, adjust=False).mean()
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=signal_period, adjust=False).mean()
    macd_hist = macd - macd_signal
    return macd, macd_signal, macd_hist

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

# STRATEGY IMPLEMENTATION
def obv_macd_rsi_strategy(prices, obv, macd, macd_signal, rsi, rsi_lower=30, rsi_upper=70):
    buy_price = []
    sell_price = []
    obv_macd_rsi_signal = []
    signal = 0

    for i in range(len(prices)):
        if rsi[i] < rsi_lower and macd[i] > macd_signal[i] and obv[i] > obv[i-1]:
            if signal != 1:
                buy_price.append(prices[i])
                sell_price.append(np.nan)
                signal = 1
                obv_macd_rsi_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                obv_macd_rsi_signal.append(0)

        elif rsi[i] > rsi_upper and macd[i] < macd_signal[i] and obv[i] < obv[i-1]:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(prices[i])
                signal = -1
                obv_macd_rsi_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                obv_macd_rsi_signal.append(0)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            obv_macd_rsi_signal.append(0)

    return buy_price, sell_price, obv_macd_rsi_signal

# INTEGRATE EVERYTHING
def get_obv_macd_rsi_signal(data):
    # OBV
    data['obv'] = get_obv(data['Close'], data['Volume'])

    # MACD
    data['macd'], data['macd_signal'], data['macd_hist'] = get_macd(data['Close'])

    # RSI
    data['rsi_14'] = get_rsi(data['Close'], 14)

    # Drop NaN values for calculation
    data = data.dropna()

    # Generate Buy/Sell Signals
    buy_price, sell_price, obv_macd_rsi_signal = obv_macd_rsi_strategy(
        data['Close'], data['obv'], data['macd'], data['macd_signal'], data['rsi_14']
    )

    data['buy_price'] = buy_price
    data['sell_price'] = sell_price

    # POSITION
    position = []
    for i in range(len(obv_macd_rsi_signal)):
        if obv_macd_rsi_signal[i] > 1:
            position.append(1)
        else:
            position.append(0)

    for i in range(len(data['Close'])):
        if obv_macd_rsi_signal[i] == 1:
            position[i] = 1
        elif obv_macd_rsi_signal[i] == -1:
            position[i] = 0
        else:
            position[i] = position[i-1]

    data['obv_macd_rsi_signal'] = obv_macd_rsi_signal
    data['position'] = position

    return data
