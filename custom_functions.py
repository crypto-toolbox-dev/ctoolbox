import requests
import talib
import math
import pandas as pd

from talib import abstract
from pyti.smoothed_moving_average import smoothed_moving_average as smma


def function_choser(indicator):
    if indicator == 'ADXS':
        custom_function = adx_system
    elif indicator == 'BOP14':
        custom_function = bop_14
    elif indicator == 'CCI20':
        custom_function = cci_20
    elif indicator == 'CCI40':
        custom_function = cci_40
    elif indicator == 'CMO14':
        custom_function = cmo_14
    elif indicator == 'CMO20':
        custom_function = cmo_20
    elif indicator == 'MOM9':
        custom_function = mom9
    elif indicator == 'MOM14':
        custom_function = mom14
    elif indicator == 'MOM21':
        custom_function = mom21
    elif indicator == 'NVT':
        custom_function = networkvalue2transactions
    elif indicator == 'NVTS':
        custom_function = networkvalue2transactionsignal
    elif indicator == 'EFI2':
        custom_function = efi_2
    elif indicator == 'EFI13':
        custom_function = efi_13
    elif indicator == 'EFI30':
        custom_function = efi_30
    elif indicator == 'EFI100':
        custom_function = efi_100
    elif indicator == 'AROONI25':
        custom_function = aroon_indicator_25
    elif indicator == 'AROONI75':
        custom_function = aroon_indicator_75
    elif indicator == 'AROONO25':
        custom_function = aroon_oscillator_25
    elif indicator == 'AROONO75':
        custom_function = aroon_oscillator_75
    elif indicator == 'MM':
        custom_function = mayermultiple
    elif indicator == 'PPOS':
        custom_function = ppo_signal
    elif indicator == 'PPOSL':
        custom_function = ppo_signal_long
    elif indicator == 'STOCH_MID':
        custom_function = stoch_mid
    elif indicator == 'STOCH_LONG':
        custom_function = stoch_long
    elif indicator == 'STOCHF_MID':
        custom_function = stochf_mid
    elif indicator == 'STOCHF_LONG':
        custom_function = stochf_long
    elif indicator == 'STOCHRSI20':
        custom_function = stoch_rsi_twenty
    elif indicator == 'RSI20':
        custom_function = rsi_twenty
    else:
        pass

    return custom_function

def rsi_twenty(data):
    df = data.copy()
    rsi = abstract.RSI(df, timeperiod=20)

    return rsi

def stochf_long(data):
    stochastic = abstract.STOCH(data, 21, 14, 0)

    return stochastic

def stochf_mid(data):
    stochastic = abstract.STOCH(data, 21, 7, 0)

    return stochastic

def stoch_long(data):
    stochastic = abstract.STOCH(data, 21, 14, 0, 14, 0)

    return stochastic

def stoch_mid(data):
    stochastic = abstract.STOCH(data,21,7,0,7,0)

    return stochastic

def mom9(data,window=9):
    mom = abstract.MOM(data)
    ema = talib.EMA(mom,window)
    oscillator = pd.concat([mom, ema], axis=1)
    oscillator.rename(columns={0: 'mom', 1: 'ema'}, inplace=True)

    return oscillator

def mom14(data,window=14):
    mom = abstract.MOM(data)
    ema = talib.EMA(mom,window)
    oscillator = pd.concat([mom, ema], axis=1)
    oscillator.rename(columns={0: 'mom', 1: 'ema'}, inplace=True)

    return oscillator

def mom21(data,window=21):
    mom = abstract.MOM(data)
    ema = talib.EMA(mom,window)
    oscillator = pd.concat([mom, ema], axis=1)
    oscillator.rename(columns={0: 'mom', 1: 'ema'}, inplace=True)

    return oscillator

def aroon_indicator_25(data,window=25):

    aroon = abstract.AROON(data,window)

    return aroon


def aroon_indicator_75(data, window=75):
    aroon = abstract.AROON(data, window)

    return aroon


def aroon_oscillator_25(data, window=25):
    aroon = abstract.AROONOSC(data, window)

    return aroon


def aroon_oscillator_75(data, window=75):
    aroon = abstract.AROONOSC(data, window)

    return aroon

def bop_14(data, window=14):

    bop = abstract.BOP(data)
    bop_sma = talib.SMA(bop,window)

    return bop_sma

def cci_20(data,window=20):
    cci = abstract.CCI(data,window)

    return cci

def cci_40(data, window=40):
    cci = abstract.CCI(data,window)

    return cci

def cmo_14(data):
    chande = abstract.CMO(data)
    signal = talib.SMA(chande,10)
    oscillator = pd.concat([chande, signal], axis=1)
    oscillator.rename(columns={0: 'chande', 1: 'signal'}, inplace=True)

    return oscillator

def cmo_20(data, window=20):
    chande = abstract.CMO(data, window)
    signal = talib.SMA(chande,9)
    oscillator = pd.concat([chande, signal], axis=1)
    oscillator.rename(columns={0: 'chande', 1: 'signal'}, inplace=True)

    return oscillator

# Calculate the Mayer Multiple (MM)
def mayermultiple(data):
    '''
    Introduced by Trace Mayer to guage cryptocoin price
    against its long range historical price movements
    :param data: df with ohlcv data
    :return: df with the mm values
    '''
    mmdata = data.copy()

    mmdata['200ma'] = talib.SMA(mmdata['close'], timeperiod=200)
    mmdata['mm'] = mmdata['close'] / mmdata['200ma']

    return mmdata['mm']


# Calculate the Elder Force Index Fast(EFI)
def efi_2(data, window=2):
    '''
    Created by Alexander Elder, measures the power behind a price movement
    using price and volume. The indicator can also be used to identify
    potential reversals and price corrections.
    :param ohlcv: dataframe with ohlcv data
    :param window: time periods for the indicator
    :return:
    '''
    efidata = data.copy()
    efidata['shift_close'] = efidata['close'].shift(1)
    efidata['raw_efi'] = efidata['close'] - efidata['shift_close']
    efidata['efi'] = efidata['raw_efi'] * efidata['volume']
    efidata['efi'] = talib.EMA(efidata['efi'], window)

    return efidata['efi']


def efi_13(data, window=13):
    '''
    Created by Alexander Elder, measures the power behind a price movement
    using price and volume. The indicator can also be used to identify
    potential reversals and price corrections.
    :param ohlcv: dataframe with ohlcv data
    :param window: time periods for the indicator
    :return:
    '''
    efidata = data.copy()
    efidata['shift_close'] = efidata['close'].shift(1)
    efidata['raw_efi'] = efidata['close'] - efidata['shift_close']
    efidata['efi'] = efidata['raw_efi'] * efidata['volume']
    efidata['efi'] = talib.EMA(efidata['efi'], window)

    return efidata['efi']

def efi_30(data, window=30):
    '''
    Created by Alexander Elder, measures the power behind a price movement
    using price and volume. The indicator can also be used to identify
    potential reversals and price corrections.
    :param ohlcv: dataframe with ohlcv data
    :param window: time periods for the indicator
    :return:
    '''

    efidata = data.copy()
    efidata['shift_close'] = efidata['close'].shift(1)
    efidata['raw_efi'] = efidata['close'] - efidata['shift_close']
    efidata['efi'] = efidata['raw_efi'] * efidata['volume']
    efidata['efi'] = talib.EMA(efidata['efi'], window)

    return efidata['efi']

# Calculate the Elder Force Index Slow (EFI)
def efi_100(data, window=100):
    '''
    Created by Alexander Elder, measures the power behind a price movement
    using price and volume. The indicator can also be used to identify
    potential reversals and price corrections.
    :param ohlcv: dataframe with ohlcv data
    :param window: time periods for the indicator
    :return:
    '''

    efidata = data.copy()
    efidata['shift_close'] = efidata['close'].shift(1)
    efidata['raw_efi'] = efidata['close'] - efidata['shift_close']
    efidata['efi'] = efidata['raw_efi'] * efidata['volume']
    efidata['efi'] = talib.EMA(efidata['efi'], window)

    return efidata['efi']

def adx_system(data):
    '''
    Plots the ADX with the +/- Directional Indicators(+/- DI)
    :param data: a df with ohlcv data
    :return: a df with +/- DI and ADX values
    '''

    adxdata = data.copy()
    dip = abstract.PLUS_DI(adxdata)
    dim = abstract.MINUS_DI(adxdata)
    adx = abstract.ADX(adxdata)

    system = [adx, dip, dim]

    for df in system:
        df.index = pd.to_datetime(df.index)

    result = pd.concat(system, axis=1).reset_index()

    result.rename(columns={'index': 'dates', 0: 'adx', 1: 'plus_di', 2:'minus_di'}, inplace=True)
    result = result.set_index('dates')
    result.index = pd.to_datetime(result.index)

    return result

def adxr_system(data):
    '''
    Plots the ADX with the +/- Directional Indicators(+/- DI)
    :param data: a df with ohlcv data
    :return: a df with +/- DI and ADX values
    '''

    adxrdata = data.copy()
    dip = abstract.PLUS_DI(adxrdata)
    dim = abstract.MINUS_DI(adxrdata)
    adx = abstract.ADXR(adxrdata)

    system = [adx, dip, dim]

    for df in system:
        df.index = pd.to_datetime(df.index)

    result = pd.concat(system, axis=1).reset_index()

    result.rename(columns={'index': 'dates', 0: 'adxr', 1: 'plus_di', 2:'minus_di'}, inplace=True)
    result = result.set_index('dates')
    result.index = pd.to_datetime(result.index)

    return result

def stoch_rsi_twenty(data):

    df = data.copy()
    stochrsi = abstract.STOCHRSI(df, timeperiod=20)

    return stochrsi

def ppo_signal(data):

    df = data.copy()
    df['ppo'] = abstract.PPO(df)
    df['ppo_signal'] = talib.EMA(df['ppo'], timeperiod=9)
    df = df.drop(columns=['close', 'open', 'high', 'low', 'volume'])

    return df

def ppo_signal_long(data):

    df = data.copy()
    ppo = abstract.PPO(df,25,50)
    sline = talib.EMA(ppo, 9)
    osc = pd.concat([ppo, sline], axis=1)
    osc.rename(columns={0: 'ppo', 1: 'signal(9)'}, inplace=True)

    return osc


#-----------------------------------------
# For custom plots
#--------------------------------------
def ichimoku_clouds(data):
    '''
    Calculate the Ichimoku Indicator Lines
    :param data: Base ohlcv data
    :return: Five lines that can be plotted to form the Ichimoku Clouds
    '''
    clouds_df = data.copy()
    clouds_df = clouds_df.iloc[:, :4]

    # TenkanSen
    clouds_df['TnkSn'] = (clouds_df['high'].rolling(9).max() + clouds_df['low'].rolling(9).min()) / 2

    # KijubSen
    clouds_df['KjnSn'] = (clouds_df['high'].rolling(26).max() + clouds_df['low'].rolling(26).min()) / 2

    # Senkou A
    clouds_df['Snk_A'] = ((clouds_df['TnkSn'] + clouds_df['KjnSn']) / 2).shift(26)

    # Senkou B
    clouds_df['Snk_B'] = ((clouds_df['high'].rolling(52).max() + clouds_df['low'].rolling(52).min()) / 2).shift(26)

    # ChikuSpan
    clouds_df['ChkSpn'] = clouds_df['close'].shift(-26)

    clouds_df.drop(columns=['open', 'high', 'low', 'close'], inplace=True)

    return clouds_df


def pivotpoints(data):
    '''
    Calculate Pivot Point Resistance and Support Lines
    :param data: Base data df
    :return: data for plotting pivot points as axlines
    '''
    pp_df = data.copy()

    # Calculate the PP and R/S levels
    ppoint = pp_df.iloc[-1, [1, 2, 3]].sum() / 3  # Pivot point level
    r1 = (ppoint * 2) - pp_df['low'].iloc[-1]  # resistance level 1
    r2 = ppoint + (pp_df['high'].iloc[-1] - pp_df['low'].iloc[-1])  # resistance level 2
    r3 = pp_df['high'].iloc[-1] + (2 * (ppoint - pp_df['low'].iloc[-1]))  # resistance level 3
    s1 = (2 * ppoint) - pp_df['high'].iloc[-1]  # support level 1
    s2 = ppoint - (pp_df['high'].iloc[-1] - pp_df['low'].iloc[-1])  # support level 2
    s3 = pp_df['low'].iloc[-1] - (2 * (pp_df['high'].iloc[-1] - ppoint))  # support level 3

    pp_levels = [ppoint,r1,r2,r3,s1,s2,s3]

    return pp_levels


def fibonacci_extensions(data, fib_start, fib_end):
    '''
    Plots Fibonacci Levels based on a Prevailing trend
    :param data: Base data df
    :param fib_start: Date string to use as a mask and fed to .loc
    :param fib_end: Date string to use as a mask and fed to .loc
    :return: A list of fib levels to plot axlines on
    '''
    fib_df = data.copy()

    # Instantiate .loc (feed them to .loc) with the masks
    trend_start = fib_df.loc[fib_start]
    trend_end = fib_df.loc[fib_end]

    # Calculate the Fib levels
    diff = trend_end['close'] - trend_start['close']
    level1 = trend_end['close'] - 0.236 * diff
    level2 = trend_end['close'] - 0.382 * diff
    level3 = trend_end['close'] - 0.618 * diff
    level4 = trend_end['close'] + 0.236 * diff
    level5 = trend_end['close'] + 0.382 * diff
    level6 = trend_end['close'] + 0.618 * diff

    fib_levels = {
        'line1':[level1, trend_start['close']],
                  'line2':[level2, level1],
                  'line3':[level3, level2],
                  'line4':[trend_end['close'], level3],
                  'line5':[level4, trend_end['close']],
                  'line6':[level5, level4],
                  'line7':[level6, level5]
                  }

    result = [i for i in fib_levels.values()]

    return result


def fibonacci_reversal(data, fib_start, fib_end, ret_end):
    '''
    Fibonacci levels based on a trend reversal
    :param data: Base data df
    :param fib_start: Date string to use as a mask and fed to .loc
    :param fib_end: Date string to use as a mask and fed to .loc
    :param ret_end: Date string to use as a mask and fed to .loc
    :return: A list of fib levels to plot axlines on
    '''
    fib_df = data.copy()

    # Instantiate .loc (feed them to .loc) with the masks
    end_retrace = fib_df.loc[ret_end]
    trend_start = fib_df.loc[fib_start]
    trend_end = fib_df.loc[fib_end]

    # Fib levels
    diff = trend_end['close'] - trend_start['close']
    level1 = end_retrace['close'] - 0.236 * diff
    level2 = end_retrace['close'] - 0.382 * diff
    level3 = end_retrace['close'] - 0.618 * diff
    level4 = end_retrace['close'] + 0.236 * diff
    level5 = end_retrace['close'] + 0.382 * diff
    level6 = end_retrace['close'] + 0.618 * diff

    fib_levels = [level1, level2, level3, level4, level5, level6, end_retrace['close']]

    return fib_levels


# Calculate the Network Value to Transactions (NVT)
def networkvalue2transactions(data, coin, ST, SP):
    '''
    Developed by Willy Woo as a PE Ratio for cryptocoins
    Source: https://charts.woobull.com/bitcoin-nvt-ratio/
    :param data: df containing daily market capitalization and daily blockchain tx volume
    :return: a df with the nvt ratio values
    '''
    data = data.copy()

    sp_start = SP
    sp_start = sp_start.strftime('%Y-%m-%d')
    sp_end = ST
    sp_end = sp_end.strftime('%Y-%m-%d')

    response = requests.get(
        f"https://data.messari.io/api/v1/assets/{coin}/metrics/nvt.adj/time-series?start={sp_start}&end={sp_end}&interval=1d&timestamp-format=rfc3339"
    )
    # If the API lacks data for this indicator, it will either return None value or 404 response. 404 causes a crash.
    if response.status_code != 404:
        data = response.json()

    else:
        data = {
            'data':{'values': None},
            'status': response.status_code
        }

    df = pd.DataFrame(data['data']['values'], columns=['dates', 'nvt'])
    df['dates'] = pd.to_datetime(df['dates'], format='%Y-%m-%d')
    df['dates'] = pd.to_datetime(df['dates']).dt.date
    df.index = df['dates']
    df.drop(columns=['dates'], inplace=True)
    df.index = pd.to_datetime(df.index)

    return df['nvt']

# Calculate the Network Value to Transactions Signal (NVTS)
def networkvalue2transactionsignal(data, coin, ST, SP):
    '''
    Developed by Dimitry Kalichkin deriving from the NVT ratio
    Provides more emphasis on predictive signaling ahead of price peaks.
    Source: https://charts.woobull.com/bitcoin-nvt-signal/
    :param data: df containing daily market capitalization and daily blockchain tx volume
    :return: df containing nvts values
    '''
    data = data.copy()

    sp_start = SP
    sp_start = sp_start.strftime('%Y-%m-%d')
    sp_end = ST
    sp_end = sp_end.strftime('%Y-%m-%d')

    response = requests.get(
        f"https://data.messari.io/api/v1/assets/{coin}/metrics/nvt.adj.90d.ma/time-series?start={sp_start}&end={sp_end}&interval=1d&timestamp-format=rfc3339"
    )
    # If the API lacks data for this indicator, it will either return None value or 404 response. 404 causes a crash.
    if response.status_code != 404:
        data = response.json()
    else:
        data = {
            'data':{'values': None},
            'status': response.status_code
        }

    df = pd.DataFrame(data['data']['values'], columns=['dates', 'nvts'])
    df['dates'] = pd.to_datetime(df['dates'], format='%Y-%m-%d')
    df['dates'] = pd.to_datetime(df['dates']).dt.date
    df.index = df['dates']
    df.drop(columns=['dates'], inplace=True)
    df.index = pd.to_datetime(df.index)

    return df['nvts']


# Zero Lag Exponential Moving Average (ZLEMA)
def zerolagexponentialmovingaverage(data, window):
    '''
    An MA that eliminates lag from an EMA
    source:
    https://technicalindicators.net/indicators-technical-analysis/182-zlema-zero-lag-exponential-moving-average
    window: desired time period
    data: ohlcv pandas df
    returns: a df with the zlema and datetime index
    '''

    zdata = data.copy()
    lag = (window - 1) // 2  # ZLEMA lag

    zdata['lag_close'] = zdata['close'].shift(lag)
    zdata['raw_zlema'] = zdata['close'] + (zdata['close'] - zdata['lag_close'])
    zdata['zlema'] = zdata['raw_zlema'].ewm(span=window, adjust=False).mean()
    zdata['zlema'] = talib.EMA(zdata['raw_zlema'], timeperiod=window)

    return zdata['zlema']

# Hull Moving Average (HMA)
def hullma(data, window):
    '''
    Calculate the HMA using talib abstract api WMA calls
    :param window: timeperiods for the MA
    :param data: ohlcv df
    :return: df with the HMA values
    '''
    hdata = data.copy()

    second_window = window // 2  # // instead of / to get whole number
    windowsqrt = math.sqrt(window)
    windowsqrt = int(windowsqrt)  # int to get a whole number

    # Calculate the base WMAs
    wma1 = abstract.WMA(hdata, timeperiod=window)
    wma2 = abstract.WMA(hdata, timeperiod=second_window)  # second WMA is half window of first

    hdata = {"wma1": wma1, "wma2": wma2}
    hma = pd.concat(hdata, axis=1)
    hma['raw-hama'] = (hma['wma2'] * 2) - hma['wma1']
    hma['hama'] = talib.WMA(hma['raw-hama'], timeperiod=windowsqrt)  # smooth eaw hama with new wma using sqrt

    hma.drop(columns=['wma1', 'wma2', 'raw-hama'], inplace=True)

    return hma


def bollinger_band_bands(data):
    '''
    NOTE:Bollinger Bands were created by John Bollinger
    and are a registered trademark to him.
    :param data: ohlcv df
    :return: df with 2 upper 2 lower and one middle band
    '''
    bbbdata = data.copy()

    # 2 and 1 std for the bands
    boll_x2std = abstract.BBANDS(bbbdata, timeperiod=20)
    boll_x1std = abstract.BBANDS(bbbdata, timeperiod=20, nbdevup=1.0, nbdevdn=1.0)

    # keep only 1 middleband and rename the others
    boll_x1std.drop(columns=['middleband'], inplace=True)
    boll_x1std.rename(columns={'upperband': 'upperband_1', 'lowerband': 'lowerband_1'}, inplace=True)
    boll_x2std.rename(columns={'upperband': 'upperband_2', 'lowerband': 'lowerband_2'}, inplace=True)

    bbb = pd.concat([boll_x1std, boll_x2std], axis=1)
    bbb.drop(columns=['middleband'],inplace=True)

    return bbb

# Calculate SMA,EMA,DEMA,TREMA,WMA,KAMA,TRIMA,T3 Moving Averages
def moving_averages(ohlcv, mav_type, mav_window):
    '''
    Uses the talib abstract API as well as custom functions
    to return moving averages for the supplied dataset

    :param ohlcv: a df with lowercase column names and datetime index
    :param mav_type: int, selects the MA type
    :param mav_window: The number of periods for the MA
    :return: Another df with datetime index and transformed data
    '''
    data = ohlcv.copy()
    #data.sort_index(ascending=True, inplace=True)

    # MAs included with talib
    # 10 = ZLEMA, 9 = HMA, 8 = T3, 7 = ??, 6 = KAMA, 5 = TRIMA, 4 = TEMA, 3 = DEMA, 2 = WMA, 1 = EMA, 0 = SMA
    if mav_type in range(0,9):
        mov_av = abstract.MA(data, timeperiod=mav_window, matype=mav_type)

    # Custom MAs abscent from talib
    # 9 = HMA, 10 = ZLEMA
    elif mav_type == 9:
        mov_av = hullma(mav_window, data)

    elif mav_type == 10:
        mov_av = zerolagexponentialmovingaverage(mav_window, data)

    else:
        print("ERROR: Please chose a number from '0-10'")

    return mov_av


def donchianchannel(data, timeframe=20):
    '''
    Creates Donchian Channels
    :param data: df with ohlc data
    :param timeframe: number of periods, default is 20
    :return: a df with Donchian Channel bands
    '''
    dchand = data.copy()

    dchand['high_chan'] = dchand['close'].rolling(timeframe).max()
    dchand['low_chan'] = dchand['close'].rolling(timeframe).min()
    dchand['mid_chan'] = (dchand['high_chan'] + dchand['low_chan']) / 2

    return dchand[['high_chan','low_chan','mid_chan']]


# Calculate the Elder Force Index (EFI)
def efi(data, window=13):
    '''
    Created by Alexander Elder, measures the power behind a price movement
    using price and volume. The indicator can also be used to identify
    potential reversals and price corrections.
    :param ohlcv: dataframe with ohlcv data
    :param window: time periods for the indicator
    :return:
    '''
    efidata = data.copy()

    efidata = efidata.drop(columns=['open', 'high', 'low'])
    efidata['shift_close'] = efidata['close'].shift(window)
    efidata['raw_efi'] = efidata['close'] - efidata['shift_close']
    efidata['efi'] = efidata['raw_efi'] * efidata['volume']

    efidata = efidata.drop(columns=['close', 'shift_close', 'raw_efi', 'shift_close', 'volume'])

    return efidata['efi']



def williamsalligatorpyti(data):
    '''
    Calculate the williams alligator indicator
    according to these formulas:
    https://www.investopedia.com/articles/trading/072115/exploring-williams-alligator-indicator.asp
    https://www.daytradetheworld.com/trading-blog/william-alligator-indicator/
    https://towardsdatascience.com/how-to-code-different-types-of-moving-averages-in-python-4f8ed6d2416f?gi=fa671ef671ff
    :param data:
    :return:
    '''

    df = data.copy()

    df['smma_13'] = smma(df['close'], 13)
    df['smma_8'] = smma(df['close'], 8)
    df['smma_5'] = smma(df['close'], 5)

    df['jaws (13/8)'] = df['smma_13'].shift(8)
    df['teeth (8/5)'] = df['smma_8'].shift(5)
    df['lips (5/3'] = df['smma_5'].shift(3)

    df.drop(columns=['open', 'high', 'low', 'close', 'volume', 'smma_13', 'smma_8', 'smma_5'], inplace=True)

    return df


