import numpy as np

def buy_sell_signal(indicator,last,cross):
    '''
    :param indicator:
    :param values:
    :return:
    '''
    stochs = ['STOCH', 'STOCHF', 'STOCH_MID', 'STOCH_LONG', 'STOCHF_MID', 'STOCHF_LONG']
    stochrsis = ['STOCHRSI', 'STOCHRSI20', 'STOCHRSI_MID', 'STOCHRSI_LONG', 'STOCHRSI20_MID', 'STOCHRSI20_LONG']

    if indicator == 'RSI' or indicator == 'RSI20':
        if last >= 70:
            signal = 'Overbought'
        elif last <= 30:
            signal = 'Oversold'
        elif last > 50:
            signal = 'Bullish'
        elif last < 50:
            signal = 'Bearish'
        else:
            signal = None

    elif indicator == 'MACD':
        if last[0] > last[1] and cross[0] < cross[1] and last[0] > 0:
            signal = 'Very Bullish'
        elif last[0] < last[1] and cross[0] > cross[1] and last[0] < 0:
            signal = 'Very Bearish'
        elif last[0] > last[1] and cross[0] < cross[1]:
            signal = 'Bullish'
        elif last[0] < last[1] and cross[0] > cross[1]:
            signal = 'Bearish'
        elif last[0] > 0 and cross[0] < 0:
            signal = 'Bullish'
        elif last[0] < 0 and cross[0] > 0:
            signal = 'Bearish'

        else:
            signal = None

    elif indicator == 'MACDFIX':
        if last[0] > last[1] and cross[0] < cross[1] and last[0] > 0:
            signal = 'Very Bullish'
        elif last[0] < last[1] and cross[0] > cross[1] and last[0] < 0:
            signal = 'Very Bearish'
        elif last[0] > last[1] and cross[0] < cross[1]:
            signal = 'Bullish'
        elif last[0] < last[1] and cross[0] > cross[1]:
            signal = 'Bearish'
        elif last[0] > 0 and cross[0] < 0:
            signal = 'Bullish'
        elif last[0] < 0 and cross[0] > 0:
            signal = 'Bearish'

        else:
            signal = None


    elif indicator in stochs:
        # Line Crosses and potential trend confirmation
        if cross[0] < 20 and last[0] > last[1] and last[0] > 20:
            signal = 'Buy'
        elif cross[0] > 80 and last[0] < last[1] and last[0] < 80:
            signal = 'Sell'

        # Crossovers
        elif last[0] > last[1] and cross[0] < cross[1]:
            signal = 'Bullish'
        elif last[0] < last[1] and cross[0] > cross[1]:
            signal = 'Bearish'

        # Overbought Oversold
        elif last[0] > 80:
            signal = 'Overbought'
        elif last[0] < 20:
            signal = 'Oversold'

        else:
            signal = None

    elif indicator == 'CCI' or indicator == 'CCI20' or indicator == 'CCI40':
        if cross <= 200 and last > 200:
            signal = 'Sell'
        elif cross >= -200 and last < -200:
            signal = 'Buy'
        elif last >= 200:
            signal = 'Very Overbought'
        elif last <= -200:
            signal = 'Very Oversold'
        elif cross <= 100 and last > 100:
            signal = 'Sell'
        elif cross >= -100 and last < -100:
            signal = 'Buy'
        elif last >= 100:
            signal = 'Overbought'
        elif last <= -100:
            signal = 'Oversold'
        else:
            signal = None



    elif indicator == 'ADXS':
        if last[0] > 50:
            if last[1] > last[2]:
                signal = 'Very Bullish'
            elif last[2] > last[1]:
                signal = 'Very Bearish'
            else:
                signal = None

        elif last[0] > 25:
            if last[1] > last[2]:
                signal = 'Bullish'
            elif last[2] > last[1]:
                signal = 'Bearish'
            else:
                signal = None

        else:
            signal = None

    elif indicator == 'APO':
        if last > 0:
            signal = 'Bullish'
        elif last < 0:
            signal = 'Bearish'

        else:
            signal = None

    elif indicator == 'AROONI25' or indicator == 'AROONI75':

        # Detect a crossover of the up/down lines
        if last[1] > last[0] and cross[1] < cross[0]:
            signal = 'Sell'

        elif last[0] < last[1] and cross[0] > cross[1]:
            signal = 'Buy'

       # Detect prevailing trend
        elif last[0] > 90:
            signal = 'Very Bearish'

        elif last[1] > 90:
            signal = 'Very Bullish'

        elif last[0] > 50:
            signal = 'Bearish'

        elif last[1] > 50:
            signal = 'Bullish'

        else:
            signal = None

    elif indicator == 'AROONO25' or indicator == 'AROONO75':
        if last > 0 and cross < 0:
            signal = 'Buy'
        elif last < 0 and cross > 0:
            signal = 'Sell'
        elif last > 50:
            signal = 'Bullish'
        elif last < -50:
            signal ='Bearish'
        elif last > 90:
            signal = 'Very Bullish'
        elif last < -90:
            signal = 'Very Bearish'
        else:
            signal = None

    elif indicator == 'BOP':
        if last > 0 and cross <= 0:
            signal = 'Buy'
        elif last < 0 and cross >= 0:
            signal = 'Sell'
        elif last > 0:
            signal = 'Bullish'
        elif last < 0:
            signal = 'Bearish'

        else:
            signal = None

    elif indicator == 'BOP14':
        if last > 0 and cross <= 0:
            signal = 'Buy'
        elif last < 0 and cross >= 0:
            signal = 'Sell'
        elif last > 0:
            signal = 'Bullish'
        elif last < 0:
            signal = 'Bearish'

        else:
            signal = None

    elif indicator == 'CMO14' or indicator == 'CMO20':
        # Overbought or oversold
        if last[0] > 50:
            signal = 'Overbought'
        elif last[0] < -50:
            signal = 'Oversold'
        # Detect Crossovers
        elif last[0] > last[1] and cross[0] <= cross[1]:
            signal = 'Bullish'
        elif last[0] < last[1] and cross[0] >= cross[1]:
            signal = 'Bearish'
        elif last[0] > 0 and cross[0] < 0:
            signal = 'Bullish'
        elif last[0] < 0 and cross[0] > 0:
            signal = 'Bearish'



        else:
            signal = None

    elif indicator == 'EFI13' or indicator == 'EFI30' or indicator == 'EFI100':
        if last > 0:
            signal = 'Bullish'
        elif last < 0:
            signal = 'Bearish'
        else:
            signal = None

    elif indicator == 'EFI2':
        if last > 0:
            signal = 'Bullish'
        elif last < 0:
            signal = 'Bearish'
        else:
            signal = None

    elif indicator == 'MM':
        if last < 1:
            signal = 'Buy'
        elif last == np.nan:
            signal = 'Not enough data'
        elif last > 2.4:
            signal = 'Bubble'
        else:
            signal = 'HODL'

    elif indicator == 'MFI':
        # Detect Failure Swing
        if cross >= 80 and last < 80:
            signal = 'Bearish'
        elif cross <= 20 and last > 20:
            signal = 'Bullish'
        elif cross >= 70 and last < 70:
            signal = 'Bearish'
        elif cross <= 30 and last > 30:
            signal = 'Bullish'

        # Buy/Sell
        elif cross < 80 and last > 80:
            signal = 'Sell'
        elif cross > 20 and last < 20:
            signal = 'Buy'
        elif cross < 70 and last > 70:
            signal = 'Sell'
        elif cross > 30 and last < 30:
            signal = 'Buy'

        # Overbought/Oversold
        elif last > 90:
            signal = 'Very Overbought'
        elif last < 10:
            signal = 'Very Oversold'
        elif last > 80:
            signal = 'Overbought'
        elif last < 20:
            signal = 'Oversold'
        else:
            signal = None


    elif indicator == 'MOM':
        if last > 0 and cross < 0:
            signal = 'Buy'
        elif last < 0 and cross > 0:
            signal = 'Sell'
        # Bullish/Bearish
        elif last > 0:
            signal = 'Bullish'
        elif last < 0:
            signal = 'Bearish'
        else:
            signal = None

    elif indicator == 'MOM9':
        if last[1] > 0 and cross[1] < 0:
            signal = 'Buy'
        elif last[1] < 0 and cross[1] > 0:
            signal = 'Sell'
        # Bullish/Bearish
        elif last[1] > 0:
            signal = 'Bullish'
        elif last[1] < 0:
            signal = 'Bearish'
        else:
            signal = None

    elif indicator == 'MOM14':
        if last[1] > 0 and cross[1] < 0:
            signal = 'Buy'
        elif last[1] < 0 and cross[1] > 0:
            signal = 'Sell'
        # Bullish/Bearish
        elif last[1] > 0:
            signal = 'Bullish'
        elif last[1] < 0:
            signal = 'Bearish'
        else:
            signal = None

    elif indicator == 'MOM21':
        if last[1] > 0 and cross[1] < 0:
            signal = 'Buy'
        elif last[1] < 0 and cross[1] > 0:
            signal = 'Sell'
        # Bullish/Bearish
        elif last[1] > 0:
            signal = 'Bullish'
        elif last[1] < 0:
            signal = 'Bearish'
        else:
            signal = None

    elif indicator == 'PPOS':
        if last[0] > last[1] and cross[0] < cross[1]:
            signal = 'Buy'
        elif last[0] < last[1] and cross[0] > cross[1]:
            signal = 'Sell'
        elif last[0] > 0:
            signal = 'Bullish'
        elif last[0] < 0:
            signal = 'Bearish'
        else:
            signal = None

    elif indicator == 'PPOSL':
        if last[0] > last[1] and cross[0] < cross[1]:
            signal = 'Buy'
        elif last[0] < last[1] and cross[0] > cross[1]:
            signal = 'Sell'
        elif last[0] > 0:
            signal = 'Bullish'
        elif last[0] < 0:
            signal = 'Bearish'
        else:
            signal = None

    elif indicator == 'PPO':
        if last > 0 and cross < 0:
            signal = 'Buy'
        elif last < 0 and cross > 0:
            signal = 'Sell'
        elif last > 0:
            signal = 'Bullish'
        elif last < 0:
            signal = 'Bearish'
        else:
            signal = None


    elif indicator in stochrsis:

        # Confirmation line cross
        if last[0] < 80 and cross[0] > 80:
            signal = 'Sell'
        elif last[0] > 20 and cross[0] < 20:
            signal = 'Buy'

        # Overbought/Oversold
        elif last[0] > 80:
            signal = 'Overbought'

        elif last[0] < 20:
            signal = 'Oversold'

        # Center line Cross
        elif last[0] > 50 and cross[0] < 50:
            signal = 'Bullish'

        elif last[0] < 50 and cross[0] > 50:
            signal = 'Bearish'

        else:
            signal = None


    elif indicator == 'WILLR':

        # Crossover triggers
        if cross > -20 and last < -20:
            signal = "Sell"

        elif cross < -80 and last > -80:
            signal = "Buy"

        elif cross < -50 and last > -50:
            signal = 'Buy'

        elif cross > -50 and last < -50:
            signal = 'Sell'

        # overbought/oversold triggers
        elif last > -20:
            signal = 'Overbought'
        elif last < -80:
            signal = 'Oversold'


        else:
            signal = None



    else:
        signal = 'A Signal is returned'
        print(indicator)
        # print(result)
        print(last)

    return signal

