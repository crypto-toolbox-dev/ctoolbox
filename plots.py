import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import mplfinance as mpf
import base64

from io import BytesIO
from menu_items import pattern_filter


# Plotter for the patter signals template
def plot_pattern_signals(df, result, pattern, cname, csymbol, SP):
    # This is drawing the y at 100 cause thats whats in the series, you need it to draw it at the price level
    deg = 80
    cncs = "angle3,angleA={}".format(deg)

    # The specific data that will be used to plot the annotations below
    index = result.index
    values = result.values
    price = df['close']
    price = price[price.index.isin(result.index)]

    # If the pattern has generated a signal today, plot that coin and its recent history
    print(f"{pattern} Detected in {cname}")

    # Make in-memory buffer
    buf = BytesIO()

    # Initialize the Figure
    #fig = mpf.figure(style='mike')
    fig = mpf.figure(style='binance')


    # Initialize the subplots
    ax1 = plt.subplot2grid((6, 4), (0, 0), rowspan=5, colspan=4)
    ax1v = ax1.twinx()

    # Colors for the candles
    kwargs = dict(type='candle', ax=ax1, volume=False, show_nontrading=True)

    mc = mpf.make_marketcolors(
        up='tab:green', down='tab:red',
        wick={'up': 'green', 'down': 'red'},
        ohlc='i'
    )

    # mplfinance style and method call
    s = mpf.make_mpf_style(marketcolors=mc)
    kwargs.update(update_width_config=dict(candle_linewidth=0.7, candle_width=0.5))

    ohlc = df.iloc[:, :4]
    ohlc = ohlc[-SP:]
    #print(ohlc)


    # Plot the candles on ax1
    mpf.plot(ohlc, **kwargs, style=s)

    # Volume as an overlay (on ax1 as ax1v)
    ax1v.fill_between(
        df.index[-SP:],
        df['volume'][-SP:],
        facecolor='lightskyblue', alpha=.5
    )

    # Ax1 styling parameters
    ax1.grid(True, color='lightblue')
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(20))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.yaxis.label.set_color("w")
    ax1.spines['bottom'].set_color("#5998ff")
    ax1.spines['top'].set_color("#5998ff")
    ax1.spines['left'].set_color("#5998ff")
    ax1.spines['right'].set_color("#5998ff")
    ax1.tick_params(axis='y', colors='grey')
    plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
    ax1.tick_params(axis='x', colors='grey')

    # ax1v styling parameters
    ax1v.axes.yaxis.set_ticklabels([])
    ax1v.grid(False)
    ax1v.set_ylim(0, 3 * max(df['volume'][df.index[-SP:]]))
    ax1v.spines['bottom'].set_color("#5998ff")
    ax1v.spines['top'].set_color("#5998ff")
    ax1v.spines['left'].set_color("#5998ff")
    ax1v.spines['right'].set_color("#5998ff")
    ax1v.tick_params(axis='x', colors='grey')
    ax1v.tick_params(axis='y', colors='grey')

    # Rotate xaxis labels
    for label in ax1.xaxis.get_ticklabels():
        label.set_rotation(45)
        label.set_horizontalalignment('right')

    # Thicker ax lines for all axes set here
    plt.setp(ax1.lines, linewidth=2.0)

    # Annotate the plots to show where the patterm has recently occured
    if pattern in pattern_filter:
        for (i, v, p) in zip(index, values, price):

            if v > 0:
                ax1.annotate(" ", xy=(i, p),
                             # xytext=(i + 0.2, v + 0.2),
                             arrowprops=dict(facecolor='yellow',
                                             shrink=0.05, connectionstyle=cncs), )
            elif v < 0:
                ax1.annotate(" ", xy=(i, p),
                             # xytext=(i + 0.2, v + 0.2),
                             arrowprops=dict(facecolor='red',
                                             shrink=0.05, connectionstyle=cncs), )
            else:
                pass
    else:
        for (i, v, p) in zip(index, values, price):

            if v > 0:
                ax1.annotate(" ", xy=(i, p),
                             # xytext=(i + 0.2, v + 0.2),
                             arrowprops=dict(facecolor='green',
                                             shrink=0.05, connectionstyle=cncs), )
            elif v < 0:
                ax1.annotate(" ", xy=(i, p),
                             # xytext=(i + 0.2, v + 0.2),
                             arrowprops=dict(facecolor='red',
                                             shrink=0.05, connectionstyle=cncs), )
            else:
                pass

    # Plot title
    id1 = cname.index("(")
    ax1.set_title(f"{cname.capitalize()[:id1]}({csymbol.upper()}) - USD", c='grey', fontsize='medium')

    fig.savefig(buf, dpi=150, format='png', facecolor=fig.get_facecolor())

    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")

    # Prevent Excessive memory use by clearing the plots from memory after they are passed to the buffer
    # Clear the current axes.
    plt.cla()
    # Clear the current figure.
    plt.clf()

    # Closes all the figure windows.
    plt.close('all')
    fig.clear()
    plt.close(fig)

    return data


# Plotter for the indicator signals template
def plot_momentum_signals(df, indicator, result, cname, iname, SP=30):

    result = result[-SP:]

    # Make in-memory buffer
    buf = BytesIO()

    # Initialize the Figure
    #fig = mpf.figure(style='mike')
    fig = mpf.figure(style='binance')


    # Initialize the subplots
    ax1 = plt.subplot2grid((6, 4), (1, 0), rowspan=4, colspan=4)
    ax0 = plt.subplot2grid((6, 4), (0, 0), sharex=ax1, rowspan=1, colspan=4)
    ax1v = ax1.twinx()

    # Colors for the candles
    kwargs = dict(type='candle', ax=ax1, volume=False, show_nontrading=True)

    mc = mpf.make_marketcolors(
        up='tab:green', down='tab:red',
        wick={'up': 'green', 'down': 'red'},
        ohlc='i'
    )

    # mplfinance style and method call
    s = mpf.make_mpf_style(marketcolors=mc)
    kwargs.update(update_width_config=dict(candle_linewidth=0.7, candle_width=0.5))

    ohlc = df.iloc[:, :4]
    ohlc = ohlc[-SP:]
    # print(ohlc)

    #Plot the candles on ax1
    mpf.plot(ohlc, **kwargs, style=s)

    # Volume as an overlay (on ax1 as ax1v)
    ax1v.fill_between(
        df.index[-SP:],
        df['volume'][-SP:],
        facecolor='lightskyblue', alpha=.5
    )

    # Plot the selected indicator on ax0
    try:
        ax0.plot(result, label=result.columns)

    except AttributeError:
        ax0.plot(result, label=iname)

    # ax0 legend
    ax0.legend(ncol=3, fontsize="xx-small")

    # Ax1 styling parameters
    ax1.grid(True, color='lightblue')
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(20))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.yaxis.label.set_color("w")
    ax1.spines['bottom'].set_color("#5998ff")
    ax1.spines['top'].set_color("#5998ff")
    ax1.spines['left'].set_color("#5998ff")
    ax1.spines['right'].set_color("#5998ff")
    ax1.tick_params(axis='y', colors='grey')
    plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
    ax1.tick_params(axis='x', colors='grey')

    # ax1v styling parameters
    ax1v.axes.yaxis.set_ticklabels([])
    ax1v.grid(False)
    ax1v.set_ylim(0, 3 * max(df['volume'][-SP:]))
    ax1v.spines['bottom'].set_color("#5998ff")
    ax1v.spines['top'].set_color("#5998ff")
    ax1v.spines['left'].set_color("#5998ff")
    ax1v.spines['right'].set_color("#5998ff")
    ax1v.tick_params(axis='x', colors='grey')
    ax1v.tick_params(axis='y', colors='grey')


    # ax0 styling params
    # axline colors
    posCol = 'green'
    negCol = 'red'
    lineCol = 'gold'
    negFillCol = 'lightcoral'
    posFillCol = 'chartreuse'

    stochs = ['STOCH', 'STOCHF', 'STOCH_MID', 'STOCH_LONG', 'STOCHF_MID', 'STOCHF_LONG']
    stochrsis = ['STOCHRSI', 'STOCHRSI20', 'STOCHRSI_MID', 'STOCHRSI_LONG', 'STOCHRSI20_MID', 'STOCHRSI20_LONG']

    if indicator == 'RSI' or indicator == 'RSI20':
        ax0.axhline(70, color=negCol)
        ax0.axhline(50, color=lineCol, linestyle='--')
        ax0.axhline(30, color=posCol)
        ax0.fill_between(result.index, result, 70,
                         where=(result >= 70), facecolor=negCol, edgecolor=negCol,
                         alpha=0.5)
        ax0.fill_between(result.index,result, 30,
                         where=(result <= 30), facecolor=posCol, edgecolor=posCol,
                         alpha=0.5)
        ax0.set_ylim(0, 100)
        ax0.set_yticks([30, 70])

    elif indicator == 'MACD' or indicator == 'MACDEXT' or indicator == 'MACDFIX':
        ax0.axhline(0, color=negCol)
        #ax0.set_color(['blue', 'gold', 'red'])
        ax0.fill_between(result.index[-SP:],
                         result['macd'] - result['macdsignal'], 0,
                         facecolor=negFillCol, edgecolor=negCol, alpha=0.5)

        ax0.locator_params(axis='y', nbins=4)

    elif indicator in stochs:
        ax0.axhline(80, color=negCol)
        ax0.axhline(50, color=lineCol, linestyle='--')
        ax0.axhline(20, color=posCol)
        ax0.set_ylim(0, 100)
        ax0.set_yticks([20, 80])

    elif indicator in stochrsis:
        ax0.axhline(80, color=negCol)
        ax0.axhline(50, color=lineCol, linestyle='--')
        ax0.axhline(20, color=posCol)
        ax0.set_ylim(0, 100)
        ax0.set_yticks([20, 50, 80])

    elif indicator == 'ADX' or indicator == 'ADXS':
        ax0.set_yticks([25, 50])
        ax0.axhline(25, color=lineCol)
        ax0.axhline(50, color=lineCol)

    elif indicator == 'APO':
        ax0.axhline(0, color=lineCol)

    elif indicator == 'BOP' or indicator == 'BOP14':
        ax0.axhline(0, color=lineCol)
        ax0.fill_between(result.index, result, 0,
                         where=(result > 0), facecolor=posCol, edgecolor=posCol,
                         alpha=0.5)
        ax0.fill_between(result.index, result, 0,
                         where=(result < 0), facecolor=negCol, edgecolor=negCol,
                         alpha=0.5)
        ax0.set_yticks([-1, 0, 1])

    elif indicator == 'CCI' or indicator == 'CCI20' or indicator == 'CCI40':
        ax0.axhline(100, color=negCol)
        ax0.axhline(-100, color=posCol)
        ax0.axhline(200, color=negCol)
        ax0.axhline(-200, color=posCol)

        ax0.fill_between(result.index, result, 100,
                         where=(result >= 100), facecolor=negCol, edgecolor=negCol,
                         alpha=0.5)
        ax0.fill_between(result.index, result, -100,
                         where=(result <= -100), facecolor=posCol, edgecolor=posCol,
                         alpha=0.5)

        ax0.fill_between(result.index, result, 200,
                         where=(result >= 100), facecolor='y', edgecolor=negCol,
                         alpha=0.5)
        ax0.fill_between(result.index, result, -200,
                         where=(result <= -200), facecolor='y', edgecolor=posCol,
                         alpha=0.5)

        ax0.set_yticks([-200, -100, 100, 200])

    elif indicator == 'CMO14' or indicator == 'CMO20':
        ax0.axhline(0, color=lineCol)
        ax0.axhline(50, color=negCol)
        ax0.axhline(-50, color=posCol)
        ax0.fill_between(result.index, result['chande'], 50,
                         where=(result['chande'] >= 50), facecolor='y', edgecolor=negCol,
                         alpha=0.5)
        ax0.fill_between(result.index, result['chande'], -50,
                         where=(result['chande'] <= -50), facecolor='y', edgecolor=posCol,
                         alpha=0.5)
        ax0.set_yticks([-50, 0, 50])


    elif indicator == 'EFI2' or indicator =='EFI13' or indicator =='EFI30' or indicator =='EFI100':
        ax0.axhline(0, color=lineCol)
        ax0.fill_between(result.index, result, 0,
                         where=(result >= 0), facecolor=posCol, edgecolor=posCol,
                         alpha=0.5)
        ax0.fill_between(result.index, result, 0,
                         where=(result <= 0), facecolor=negCol, edgecolor=negCol,
                         alpha=0.5)


    elif indicator == 'AROONI25' or indicator == 'AROONI75':
        ax0.axhline(90, color=lineCol,linewidth=0.7)
        ax0.axhline(50, color=lineCol,linewidth=0.7)
        ax0.axhline(10, color=lineCol,linewidth=0.7)
        ax0.set_yticks([0,10, 50, 90,100])


    elif  indicator == 'AROONO25' or indicator == 'AROONO75':
        ax0.axhline(0, color=lineCol, linewidth=0.7)
        ax0.axhline(-50, color=lineCol, linewidth=0.7)
        ax0.axhline(50, color=lineCol, linewidth=0.7)
        ax0.axhline(-90, color=lineCol, linewidth=0.7)
        ax0.axhline(90, color=lineCol, linewidth=0.7)
        ax0.set_yticks([0, -50, -90, 50, 90])

    elif indicator == 'MFI':
        ax0.axhline(80, color=negCol)
        ax0.axhline(20, color=posCol)
        ax0.axhline(70, color=negCol)
        ax0.axhline(30, color=posCol)
        ax0.set_yticks([ 10,20, 30, 80, 70, 90], fontsize="xx-small")

    elif indicator == 'MM':
        ax0.axhline(2.4, color=negCol)
        ax0.axhline(1.5, color=lineCol)
        ax0.axhline(1, color=posCol)
        ax0.set_yticks([ 1, 1.5, 2.4])

    elif indicator == 'MOM':
        ax0.axhline(0, color=lineCol)

        ax0.fill_between(result.index, result, 0,
                         where=(result >= 0), facecolor=posCol, edgecolor=posCol,
                         alpha=0.5)
        ax0.fill_between(result.index, result, 0,
                         where=(result <= 0), facecolor=negCol, edgecolor=negCol,
                         alpha=0.5)

    elif indicator == 'MOM9' or indicator == 'MOM14' or indicator == 'MOM21':
        ax0.axhline(0, color=lineCol)

        ax0.fill_between(result.index, result['ema'], 0,
                         where=(result['ema'] >= 0), facecolor=posCol, edgecolor=posCol,
                         alpha=0.5)
        ax0.fill_between(result.index, result['ema'], 0,
                         where=(result['ema'] <= 0), facecolor=negCol, edgecolor=negCol,
                         alpha=0.5)


    elif indicator == 'WILLR':
        ax0.axhline(-20, color=negCol)
        ax0.axhline(-50, color=lineCol, linestyle='--')
        ax0.axhline(-80, color=posCol)
        ax0.fill_between(result.index, result, -20,
                         where=(result >= -20), facecolor=negCol, edgecolor=negCol,
                         alpha=0.5)
        ax0.fill_between(result.index, result, -80,
                         where=(result <= -80), facecolor=posCol, edgecolor=posCol,
                         alpha=0.5)
        ax0.set_ylim(0, -100)
        ax0.set_yticks([-20, -50, -80])


    elif indicator == 'PPO' or indicator == 'PPOS' or indicator == 'PPOSL':
        ax0.axhline(0, color=lineCol)

    # Rotate xaxis labels
    for label in ax1.xaxis.get_ticklabels():
        label.set_rotation(45)
        label.set_horizontalalignment('right')

    # Hide top plot x axis ticks
    plt.setp(ax0.get_xticklabels(), visible=False)

    # Thicker ax lines for all axes set here
    plt.setp(ax1.lines, linewidth=1.3)
    plt.setp(ax0.lines, linewidth=1.3)


    # Plot title
    id1 = cname.index("(")
    id2 = cname.index(")")
    csymbol = cname[id1 + len("") + 1: id2].upper()
    plt.suptitle(f"{cname.capitalize()[:id1]}({csymbol.upper()}) - USD", color='grey', fontsize='medium')
    fig.savefig(buf, dpi=150, format='png', facecolor=fig.get_facecolor())

    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")

    # Prevent Excessive memory use by clearing the plots from memory after they are passed to the buffer
    # Clear the current axes.
    plt.cla()
    # Clear the current figure.
    plt.clf()

    # Closes all the figure windows.
    plt.close('all')
    fig.clear()
    plt.close(fig)

    return data


# Plotter for the custom plots template
def plotter(cname, ohlcv, txn_vol=None, top_result=None, bottom_result=None, main_result=None, first_mav=None, second_mav=None,
            patresult=None, first_mav_p=None, second_mav_p=None, top_iname=None, bottom_iname=None, main_iname=None,
            fibonacci=None, fibonacci_levels=None, fibonacci_labels=None, fibonacci_colors=None,
            fib_ts=None, fib_te=None, fib_trev=None,
            first_mav_name=None, second_mav_name=None, patname=None, bottom_color=None, top_color=None, main_color=None,
            fiat=None, timezone=None, **kwargs):

    '''
   :param ohlcv: open, high, low, close, volume for the candles and volume overlay
   :param top_result: top indicator values (ax0)
   :param bottom_result:  bottom indicator values (ax2)
   :param first_mav: moving average values (ax1)
   :param second_mav: moving average values (ax1)
   :param top_iname:
   :param bottom_iname:
   :param main_iname:
   :param first_mav_name:
   :param second_mav_name:
   :return: A matplotlib figure which is saved to the data directory and displayed in the template 'custom_plots.html'
   '''

    # Make in-memory buffer
    buf = BytesIO()

    #Initialize the Figure
    #fig = mpf.figure(style='mike')
    fig = mpf.figure(style='binance')


    # Initialize the subplots
    ax1 = plt.subplot2grid((6, 4), (1, 0), rowspan=4, colspan=4)
    ax1v = ax1.twinx()     # for the volume which will be plotted as a shaded overlay
    ax1txnv = ax1.twinx()  # for the on chain volume which will be plotted as a shaded overlay
    ax1obv = ax1.twinx()  # for the obv so it doesn't skew the plot away from the candles
    ax0 = plt.subplot2grid((6, 4), (0, 0), sharex=ax1, rowspan=1, colspan=4)
    ax2 = plt.subplot2grid((6, 4), (5, 0), sharex=ax1, rowspan=1, colspan=4)

    # Colors for the candles and ohlc sticks
    kwargs = dict(type='candle', ax=ax1, volume=False, show_nontrading=True)

    mc = mpf.make_marketcolors(
        up='tab:green', down='tab:red',
        wick={'up': 'green', 'down': 'red'},
        ohlc='i'
    )

    # mplfinance style and method call
    s = mpf.make_mpf_style(marketcolors=mc)
    kwargs.update(update_width_config=dict(candle_linewidth=0.4, candle_width=0.5))

    print("Data length")
    print(len(ohlcv))

    # Change candle style depending on amount of data
    if len(ohlcv) >= 720:
        kwargs.update(type='ohlc')

    elif len(ohlcv) >= 180:
        kwargs.update(type='ohlc')

    elif len(ohlcv) >= 90:
        kwargs.update(update_width_config=dict(candle_linewidth=0.4, candle_width=1.0))


    # Prepare the candles for ax1
    ohlc = ohlcv.iloc[:, :4]
    ohlc = ohlc

    # Volume as an overlay (on ax1 as ax1v)
    ax1v.fill_between(
        ohlcv.index,
        ohlcv['volume'],
        facecolor='lightskyblue', alpha=.5
    )

    # On-chain Transaction Volume as an overlay (on ax1 as ax1txnv)
    try:
        ax1txnv.fill_between(
            txn_vol.index,
            txn_vol['txn_vol'],
            facecolor='pink', alpha=.5
        )
        ax1txnv.set_ylim(0, 3 * max(txn_vol['txn_vol']))


    except:
        print("No on-chain Transaction data to plot")

    # Line colors for the subplots
    posCol = 'green'
    negCol = 'red'
    indiCol = 'blue'
    lineCol = 'gold'
    negFillCol = 'lightcoral'
    posFillCol = 'chartreuse'

    if top_iname:
        # Plot the selected indicator on top at ax0
        try:
            for column, color, label in zip(top_result, top_color, top_result.columns):
                ax0.plot(top_result[column], color=color, label=label.upper(), lw=0.8)

        except AttributeError:
            ax0.plot(top_result, color=indiCol, label=top_iname.upper(), lw=0.8)


    # OBV is here because it needs its own axes like volume (ax1obv)
    if main_iname:
        if main_iname == 'OBV':
            ax1obv.plot(main_result, color='orange', label='OBV', lw=0.8)
            ax1obv.legend(fontsize="xx-small", loc='upper left')


        elif main_iname == 'PIV':
            plot_main_indi = main_result
            plot_main_indi_color = main_color

            labels = ['Ppoint', 'Resistance', None, None, 'Support', None, None]

            for (plev, colors, labe) in zip(plot_main_indi, plot_main_indi_color, labels):
                ax1.axhline(y=plev, color=colors, linestyle='-', label=labe, linewidth=0.7)

        else:
            try:
                for column, color, label in zip(main_result, main_color, main_result.columns):
                    ax1.plot(main_result[column], color=color, label=label.upper(), lw=0.8)

            except AttributeError:
                ax1.plot(main_result, color=indiCol, label=main_iname.upper(), lw=0.8)


    # Mark where patterns were selected pattern was detected on the candles
    if patname:
        index = patresult.index
        values = patresult.values
        hprice = ohlc['high']
        lprice = ohlc['low']

        # If the pattern detected is marked by 0 or 100
        if patname in pattern_filter:
            label_added = False             # to get label for only one of the iterations

            for (i, v, hp, lp) in zip(index, values, hprice, lprice):

                if v > 0:
                    if not label_added:     # to get label for only one of the iterations
                        ax1.scatter(i, hp, marker="*", color='y', s=48, alpha=0.8, label=f"{patname[3:].upper()}")
                        label_added=True
                    else:
                        ax1.scatter(i, hp, marker="*", color='y', s=48, alpha=0.8)

        # If the pattern is marked by -100 or 100
        else:
            label_added = False      # to get label for only one of the iterations

            for (i, v, hp, lp) in zip(index, values, hprice, lprice):

                    if v > 0:
                        if not label_added:         # to get label for only one of the iterations
                            ax1.scatter(
                                i, hp,
                                marker="v",
                                color='yellowgreen',
                                s=48,
                                alpha=0.8,
                                label=f"Bull {patname[3:].upper()}"
                            )
                            label_added = True
                        else:
                            ax1.scatter(i, hp, marker="v", color='yellowgreen', s=48, alpha=0.8)

            label_added = False

            for (i, v, hp, lp) in zip(index, values, hprice, lprice):

                    if v < 0:
                        if not label_added:         # to get label for only one of the iterations
                            ax1.scatter(
                                i, lp, marker="^",
                                color='orangered',
                                s=48, alpha=0.8,
                                label=f"Bear {patname[3:].upper()}"
                            )
                            label_added = True

                        else:
                            ax1.scatter(i, lp, marker="^", color='orangered', s=48, alpha=0.8)


    # Plot the first selected moving on the main plot at ax1
    if first_mav_name:
        try:
            ax1.plot(first_mav, label=f"{first_mav.columns} {first_mav_p}", color='purple', lw=0.8)

        except AttributeError:
            ax1.plot(first_mav, label=f"{first_mav_name} {first_mav_p}", color='purple', lw=0.8)


    if second_mav_name:
        # Plot the first selected moving on the main plot at ax1
        try:
            ax1.plot(second_mav, label=f"{second_mav.columns} {second_mav_p}", color='blue', lw=0.8)

        except AttributeError:
            ax1.plot(second_mav, label=f"{second_mav_name} {second_mav_p}", color='blue', lw=0.8)


    if fibonacci:
        if fibonacci == 'FIBEXT':

            ohlc['dates'] = ohlc.index

            for (fiblev, colors, labe) in zip(fibonacci_levels, fibonacci_colors, fibonacci_labels):
                ax1.axhspan(fiblev[0], fiblev[1], alpha=0.5, color=colors, label=labe)

            # Annotations to mark the user specified start and end of the trend used from Fib Extension lines
            try:
                ax1.annotate(
                    'Trend Start',
                    xy=(ohlc.loc[fib_ts]['dates'], ohlc.loc[fib_ts]['low']),
                    xycoords='data',
                    xytext=(0.5 * 32, -32),
                    textcoords='offset points',
                    horizontalalignment='right',
                    family='sans-serif',
                    fontsize=6,
                    rotation=-45,
                    arrowprops=dict(
                    facecolor='yellow', arrowstyle="->", connectionstyle="angle, angleA = 0, angleB = 90,\
                        rad = 10")
                )

            except KeyError:
                print("Trend start date out of the visible range being plotted")

            try:
                ax1.annotate(
                    'Trend End',
                    xy=(ohlc.loc[fib_te]['dates'], ohlc.loc[fib_te]['low']),
                    xycoords='data',
                    xytext=(0.5 * 32, -32),
                    textcoords='offset points',
                    horizontalalignment='right',
                    family='sans-serif',
                    fontsize=6,
                    rotation=-45,
                    arrowprops=dict(
                    facecolor='yellow', arrowstyle="->",connectionstyle = "angle, angleA = 0, angleB = 90,\
                    rad = 10")
                            )
            except KeyError:
                print("Trend end date out of the visible range being plotted")

        else:
            ohlc['dates'] = ohlc.index

            for (fiblev, colors, labe) in zip(fibonacci_levels, fibonacci_colors, fibonacci_labels):
                ax1.axhline(fiblev, color=colors, label=labe)

            #TODO: Add error handling as above to this annotation logic

            ax1.annotate(
                'Trend Start',
                xy=(ohlc.loc[fib_ts]['dates'], ohlc.loc[fib_ts]['low']),
                xycoords='data',
                xytext=(0.5 * 32, -32),
                textcoords='offset points',
                horizontalalignment='right',
                family='sans-serif',
                fontsize=6,
                rotation=-45,
                arrowprops=dict(facecolor='yellow', arrowstyle="->", connectionstyle="angle, angleA = 0, angleB = 90,\
                                rad = 10")
            )

            ax1.annotate(
                'Trend End',
                xy=(ohlc.loc[fib_te]['dates'], ohlc.loc[fib_te]['low']),
                xycoords='data',
                xytext=(0.5 * 32, -32),
                textcoords='offset points',
                horizontalalignment='right',
                family='sans-serif',
                fontsize=6,
                rotation=-45,
                arrowprops=dict(facecolor='yellow', arrowstyle="->", connectionstyle="angle, angleA = 0, angleB = 90,\
                            rad = 10")
            )

            ax1.annotate(
                'Reversal End',
                xy=(ohlc.loc[fib_trev]['dates'], ohlc.loc[fib_trev]['low']),
                xycoords='data',
                xytext=(0.5 * 32, -32),
                textcoords='offset points',
                horizontalalignment='right',
                family='sans-serif',
                fontsize=6,
                rotation=-45,
                arrowprops=dict(facecolor='yellow', arrowstyle="->", connectionstyle="angle, angleA = 0, angleB = 90,\
                                        rad = 10")
            )


    # Plot the candlesticks using mpl finance plot function
    # Plotted here so the candles remain the center of plot
    mpf.plot(ohlc, **kwargs, style=s)

    if bottom_iname:
        # Plot the selected indicator on bottom at ax2
        try:
            for column, color, label in zip(bottom_result, bottom_color, bottom_result.columns):
                ax2.plot(bottom_result[column], color=color, label=label.upper(), lw=0.8)

        except AttributeError:
            ax2.plot(bottom_result, color=indiCol, label=bottom_iname.upper(), lw=0.8)


    # Indicator Groupings
    stochs = ['STOCH', 'STOCHF', 'STOCH_MID', 'STOCH_LONG', 'STOCHF_MID', 'STOCHF_LONG']
    stochrsis = ['STOCHRSI', 'STOCHRSI20', 'STOCHRSI_MID', 'STOCHRSI_LONG', 'STOCHRSI20_MID', 'STOCHRSI20_LONG']
    macds = ['MACD', 'MACDEXT', 'MACDFIX']
    rsis = ['RSI', 'RSI20']
    ccis = ['CCI', 'CCI20', 'CCI40']
    efis = ['EFI2', 'EFI13', 'EFI30', 'EFI100']
    cmos = ['CMO14', 'CMO20']
    bops = ['BOP', 'BOP14']
    adxes = ['ADX', 'ADXS', 'ADXR']
    aroonis = ['AROONI25', 'AROONI75']
    aroonos = ['AROONO25', 'AROONO75']
    moms = ['MOM9', 'MOM14', 'MOM21']
    pposes = ['PPO', 'PPOS', 'PPOSL']


    # Styling Parameters
    # Indicator Specific axline colors

    # Top Plot ax0
    if top_iname:
        if top_iname in rsis:
            ax0.axhline(70, color=negCol, linewidth=0.7)
            ax0.axhline(50, color=lineCol, linestyle='--', linewidth=0.7)
            ax0.axhline(30, color=posCol, linewidth=0.7)
            ax0.fill_between(top_result.index, top_result, 70,
                             where=(top_result >= 70), facecolor=negCol, edgecolor=negCol,
                             alpha=0.5)
            ax0.fill_between(top_result.index, top_result, 30,
                             where=(top_result <= 30), facecolor=posCol, edgecolor=posCol,
                             alpha=0.5)
            ax0.set_ylim(0, 100)
            ax0.set_yticks([30, 70])

        elif top_iname in macds:
            ax0.axhline(0, color=negCol, linewidth=0.7)
            ax0.fill_between(top_result.index,
                             top_result['macd'] - top_result['macdsignal'], 0,
                             facecolor=negFillCol, edgecolor=negCol, alpha=0.5)

            ax0.locator_params(axis='y', nbins=4)

        elif top_iname in stochs:
            ax0.axhline(80, color=negCol, linewidth=0.7)
            ax0.axhline(50, color=lineCol, linestyle='--', linewidth=0.7)
            ax0.axhline(20, color=posCol, linewidth=0.7)
            ax0.set_ylim(0, 100)
            ax0.set_yticks([20, 80])

        elif top_iname in stochrsis:
            ax0.axhline(80, color=negCol, linewidth=0.7)
            ax0.axhline(50, color=lineCol, linestyle='--', linewidth=0.7)
            ax0.axhline(20, color=posCol, linewidth=0.7)
            ax0.set_ylim(0, 100)
            ax0.set_yticks([20, 50, 80])

        elif top_iname in adxes:
            ax0.set_yticks([25, 50])
            ax0.axhline(25, color=lineCol, linewidth=0.7)
            ax0.axhline(50, color=lineCol, linewidth=0.7)


        elif top_iname == 'APO':
            ax0.axhline(0, color=lineCol, linewidth=0.7)


        elif top_iname in bops:
            ax0.axhline(0, color=lineCol, linewidth=0.7)
            ax0.fill_between(top_result.index, top_result, 0,
                             where=(top_result > 0), facecolor=posCol, edgecolor=posCol,
                             alpha=0.5)
            ax0.fill_between(top_result.index, top_result, 0,
                             where=(top_result < 0), facecolor=negCol, edgecolor=negCol,
                             alpha=0.5)
            ax0.set_yticks([-1, 0, 1])


        elif top_iname in ccis:
            ax0.axhline(100, color=negCol, linewidth=0.7)
            ax0.axhline(-100, color=posCol, linewidth=0.7)
            ax0.axhline(200, color=negCol, linewidth=0.7)
            ax0.axhline(-200, color=posCol, linewidth=0.7)

            ax0.fill_between(top_result.index, top_result, 100,
                             where=(top_result >= 100), facecolor=negCol, edgecolor=negCol,
                             alpha=0.5)
            ax0.fill_between(top_result.index, top_result, -100,
                             where=(top_result <= -100), facecolor=posCol, edgecolor=posCol,
                             alpha=0.5)

            ax0.fill_between(top_result.index, top_result, 200,
                             where=(top_result >= 100), facecolor='y', edgecolor=negCol,
                             alpha=0.5)
            ax0.fill_between(top_result.index, top_result, -200,
                             where=(top_result <= -200), facecolor='y', edgecolor=posCol,
                             alpha=0.5)

            ax0.set_yticks([-200, -100, 100, 200])


        elif top_iname in cmos:
            ax0.axhline(0, color=lineCol, linewidth=0.7)
            ax0.axhline(50, color=negCol, linewidth=0.7)
            ax0.axhline(-50, color=posCol, linewidth=0.7)
            ax0.fill_between(top_result.index, top_result['chande'], 50,
                             where=(top_result['chande'] >= 50), facecolor='y', edgecolor=negCol,
                             alpha=0.5)
            ax0.fill_between(top_result.index, top_result['chande'], -50,
                             where=(top_result['chande'] <= -50), facecolor='y', edgecolor=posCol,
                             alpha=0.5)
            ax0.set_yticks([-50, 0, 50])


        elif top_iname in efis:
            ax0.axhline(0, color=lineCol, linewidth=0.7)
            ax0.fill_between(top_result.index, top_result, 0,
                             where=(top_result >= 0), facecolor=posCol, edgecolor=posCol,
                             alpha=0.5)
            ax0.fill_between(top_result.index, top_result, 0,
                             where=(top_result <= 0), facecolor=negCol, edgecolor=negCol,
                             alpha=0.5)


        elif top_iname in aroonis:
            ax0.axhline(90, color=lineCol, linewidth=0.7)
            ax0.axhline(50, color=lineCol, linewidth=0.7)
            ax0.axhline(10, color=lineCol, linewidth=0.7)
            ax0.set_yticks([0, 10, 50, 90, 100])


        elif top_iname in aroonos:
            ax0.axhline(0, color=lineCol, linewidth=0.7)
            ax0.axhline(-50, color=lineCol, linewidth=0.7)
            ax0.axhline(50, color=lineCol, linewidth=0.7)
            ax0.axhline(-90, color=lineCol, linewidth=0.7)
            ax0.axhline(90, color=lineCol, linewidth=0.7)
            ax0.set_yticks([0, -50, -90, 50, 90])

        elif top_iname == 'MFI':
            ax0.axhline(80, color=negCol, linewidth=0.7)
            ax0.axhline(20, color=posCol, linewidth=0.7)
            ax0.axhline(70, color=negCol, linewidth=0.7)
            ax0.axhline(30, color=posCol, linewidth=0.7)
            ax0.set_yticks([10, 20, 30, 80, 70, 90], fontsize="xx-small")

        elif top_iname == 'MM':
            ax0.axhline(2.4, color=negCol, linewidth=0.7)
            ax0.axhline(1.5, color=lineCol, linewidth=0.7)
            ax0.axhline(1, color=posCol, linewidth=0.7)
            ax0.set_yticks([1, 1.5, 2.4])

        elif top_iname == 'MOM':
            ax0.axhline(0, color=lineCol, linewidth=0.7)

            ax0.fill_between(top_result.index, top_result, 0,
                             where=(top_result >= 0), facecolor=posCol, edgecolor=posCol,
                             alpha=0.5)
            ax0.fill_between(top_result.index, top_result, 0,
                             where=(top_result <= 0), facecolor=negCol, edgecolor=negCol,
                             alpha=0.5)

        elif top_iname in moms:
            ax0.axhline(0, color=lineCol)

            ax0.fill_between(top_result.index, top_result['ema'], 0,
                             where=(top_result['ema'] >= 0), facecolor=posCol, edgecolor=posCol,
                             alpha=0.5)
            ax0.fill_between(top_result.index, top_result['ema'], 0,
                             where=(top_result['ema'] <= 0), facecolor=negCol, edgecolor=negCol,
                             alpha=0.5)


        elif top_iname == 'WILLR':
            ax0.axhline(-20, color=negCol, linewidth=0.7)
            ax0.axhline(-50, color=lineCol, linestyle='--', linewidth=0.7)
            ax0.axhline(-80, color=posCol, linewidth=0.7)
            ax0.fill_between(top_result.index, top_result, -20,
                             where=(top_result >= -20), facecolor=negCol, edgecolor=negCol,
                             alpha=0.5)
            ax0.fill_between(top_result.index, top_result, -80,
                             where=(top_result <= -80), facecolor=posCol, edgecolor=posCol,
                             alpha=0.5)
            ax0.set_ylim(0, -100)
            ax0.set_yticks([-20, -50, -80])


        elif top_iname in pposes:
            ax0.axhline(0, color=lineCol, linewidth=0.7)


    # Main Plot ax1
    if main_iname:

        if main_iname == 'ICH':
            ax1.fill_between(main_result.index,
                             main_result['Snk_A'][main_result.index],
                             main_result['Snk_B'][main_result.index],
                             where=(main_result['Snk_A'][main_result.index] < main_result['Snk_B'][main_result.index]),
                             color=negCol, alpha=0.5)

            ax1.fill_between(main_result.index,
                             main_result['Snk_A'][main_result.index],
                             main_result['Snk_B'][main_result.index],
                             where=(main_result['Snk_A'][main_result.index] > main_result['Snk_B'][main_result.index]),
                             color=posCol, alpha=0.5)

        elif main_iname == 'BBB':
            ax1.fill_between(main_result.index,
                             main_result['upperband_2'][main_result.index],
                             main_result['upperband_1'][main_result.index],
                             where=(main_result['upperband_2'][main_result.index] >= main_result['upperband_1'][
                                 main_result.index]),
                             color=posCol, alpha=0.5)

            ax1.fill_between(main_result.index,
                             main_result['lowerband_2'][main_result.index],
                             main_result['lowerband_1'][main_result.index],
                             where=(main_result['lowerband_1'][main_result.index] >= main_result['lowerband_2'][
                                 main_result.index]),
                             color=negCol, alpha=0.5)

        elif main_iname == 'DCHAN':
            ax1.fill_between(main_result.index,
                             main_result['high_chan'][main_result.index],
                             main_result['mid_chan'][main_result.index],
                             where=(main_result['high_chan'][main_result.index] > main_result['mid_chan'][
                                 main_result.index]),
                             color=posCol, alpha=0.5)

            ax1.fill_between(main_result.index,
                             main_result['low_chan'][main_result.index],
                             main_result['mid_chan'][main_result.index],
                             where=(main_result['low_chan'][main_result.index] < main_result['mid_chan'][
                                 main_result.index]),
                             color=negCol, alpha=0.5)


    # Bottom Plot ax2
    if bottom_iname:
        if bottom_iname in rsis:
            ax2.axhline(70, color=negCol, linewidth=0.7)
            ax2.axhline(50, color=lineCol, linestyle='--', linewidth=0.7)
            ax2.axhline(30, color=posCol, linewidth=0.7)
            ax2.fill_between(bottom_result.index, bottom_result, 70,
                             where=(bottom_result >= 70), facecolor=negCol, edgecolor=negCol,
                             alpha=0.5)
            ax2.fill_between(bottom_result.index, bottom_result, 30,
                             where=(bottom_result <= 30), facecolor=posCol, edgecolor=posCol,
                             alpha=0.5)
            ax2.set_ylim(0, 100)
            ax2.set_yticks([30, 70])

        elif bottom_iname in macds:
            ax2.axhline(0, color=negCol, linewidth=0.7)
            ax2.fill_between(bottom_result.index,
                             bottom_result['macd'] - bottom_result['macdsignal'], 0,
                             facecolor=negFillCol, edgecolor=negCol, alpha=0.5)

            ax2.locator_params(axis='y', nbins=4)

        elif bottom_iname in stochs:
            ax2.axhline(80, color=negCol, linewidth=0.7)
            ax2.axhline(50, color=lineCol, linestyle='--', linewidth=0.7)
            ax2.axhline(20, color=posCol, linewidth=0.7)
            ax2.set_ylim(0, 100)
            ax2.set_yticks([20, 80])

        elif bottom_iname in stochrsis:
            ax2.axhline(80, color=negCol, linewidth=0.7)
            ax2.axhline(50, color=lineCol, linestyle='--', linewidth=0.7)
            ax2.axhline(20, color=posCol, linewidth=0.7)
            ax2.set_ylim(0, 100)
            ax2.set_yticks([20, 50, 80])

        elif bottom_iname in adxes:
            ax2.set_yticks([25, 50])
            ax2.axhline(25, color=lineCol, linewidth=0.7)
            ax2.axhline(50, color=lineCol, linewidth=0.7)

        elif bottom_iname == 'APO':
            ax2.axhline(0, color=lineCol)

        elif bottom_iname in bops:
            ax2.axhline(0, color=lineCol, linewidth=0.7)
            ax2.fill_between(bottom_result.index, bottom_result, 0,
                             where=(bottom_result > 0), facecolor=posCol, edgecolor=posCol,
                             alpha=0.5)
            ax2.fill_between(bottom_result.index, bottom_result, 0,
                             where=(bottom_result < 0), facecolor=negCol, edgecolor=negCol,
                             alpha=0.5)
            ax2.set_yticks([-1, 0, 1])

        elif bottom_iname in ccis:
            ax2.axhline(100, color=negCol, linewidth=0.7)
            ax2.axhline(-100, color=posCol, linewidth=0.7)
            ax2.axhline(200, color=negCol, linewidth=0.7)
            ax2.axhline(-200, color=posCol, linewidth=0.7)

            ax2.fill_between(bottom_result.index, bottom_result, 100,
                             where=(bottom_result >= 100), facecolor=negCol, edgecolor=negCol,
                             alpha=0.5)
            ax2.fill_between(bottom_result.index, bottom_result, -100,
                             where=(bottom_result <= -100), facecolor=posCol, edgecolor=posCol,
                             alpha=0.5)

            ax2.fill_between(bottom_result.index, bottom_result, 200,
                             where=(bottom_result >= 100), facecolor='y', edgecolor=negCol,
                             alpha=0.5)
            ax2.fill_between(bottom_result.index, bottom_result, -200,
                             where=(bottom_result <= -200), facecolor='y', edgecolor=posCol,
                             alpha=0.5)

            ax2.set_yticks([-200, -100, 100, 200])

        elif bottom_iname in cmos:
            ax2.axhline(0, color=lineCol, linewidth=0.7)
            ax2.axhline(50, color=negCol, linewidth=0.7)
            ax2.axhline(-50, color=posCol, linewidth=0.7)
            ax2.fill_between(bottom_result.index, bottom_result['chande'], 50,
                             where=(bottom_result['chande'] >= 50), facecolor='y', edgecolor=negCol,
                             alpha=0.5)
            ax2.fill_between(bottom_result.index, bottom_result['chande'], -50,
                             where=(bottom_result['chande'] <= -50), facecolor='y', edgecolor=posCol,
                             alpha=0.5)
            ax2.set_yticks([-50, 0, 50])


        elif bottom_iname in efis:
            ax2.axhline(0, color=lineCol, linewidth=0.7)
            ax2.fill_between(bottom_result.index, bottom_result, 0,
                             where=(bottom_result >= 0), facecolor=posCol, edgecolor=posCol,
                             alpha=0.5)
            ax2.fill_between(bottom_result.index, bottom_result, 0,
                             where=(bottom_result <= 0), facecolor=negCol, edgecolor=negCol,
                             alpha=0.5)


        elif bottom_iname in aroonis:
            ax2.axhline(90, color=lineCol, linewidth=0.7)
            ax2.axhline(50, color=lineCol, linewidth=0.7)
            ax2.axhline(10, color=lineCol, linewidth=0.7)
            ax2.set_yticks([0, 10, 50, 90, 100])


        elif bottom_iname in aroonos:
            ax2.axhline(0, color=lineCol, linewidth=0.7)
            ax2.axhline(-50, color=lineCol, linewidth=0.7)
            ax2.axhline(50, color=lineCol, linewidth=0.7)
            ax2.axhline(-90, color=lineCol, linewidth=0.7)
            ax2.axhline(90, color=lineCol, linewidth=0.7)
            ax2.set_yticks([0, -50, -90, 50, 90])

        elif bottom_iname == 'MFI':
            ax2.axhline(80, color=negCol, linewidth=0.7)
            ax2.axhline(20, color=posCol, linewidth=0.7)
            ax2.axhline(70, color=negCol, linewidth=0.7)
            ax2.axhline(30, color=posCol, linewidth=0.7)
            ax2.set_yticks([10, 20, 30, 80, 70, 90], fontsize="xx-small")

        elif bottom_iname == 'MM':
            ax2.axhline(2.4, color=negCol, linewidth=0.7)
            ax2.axhline(1.5, color=lineCol, linewidth=0.7)
            ax2.axhline(1, color=posCol, linewidth=0.7)
            ax2.set_yticks([1, 1.5, 2.4])

        elif bottom_iname == 'MOM':
            ax2.axhline(0, color=lineCol, linewidth=0.7)

            ax2.fill_between(bottom_result.index, bottom_result, 0,
                             where=(bottom_result >= 0), facecolor=posCol, edgecolor=posCol,
                             alpha=0.5)
            ax2.fill_between(bottom_result.index, bottom_result, 0,
                             where=(bottom_result <= 0), facecolor=negCol, edgecolor=negCol,
                             alpha=0.5)

        elif bottom_iname in moms:
            ax2.axhline(0, color=lineCol, linewidth=0.7)

            ax2.fill_between(bottom_result.index, bottom_result['ema'], 0,
                             where=(bottom_result['ema'] >= 0), facecolor=posCol, edgecolor=posCol,
                             alpha=0.5)
            ax2.fill_between(bottom_result.index, bottom_result['ema'], 0,
                             where=(bottom_result['ema'] <= 0), facecolor=negCol, edgecolor=negCol,
                             alpha=0.5)


        elif bottom_iname == 'WILLR':
            ax2.axhline(-20, color=negCol, linewidth=0.7)
            ax2.axhline(-50, color=lineCol, linestyle='--', linewidth=0.7)
            ax2.axhline(-80, color=posCol, linewidth=0.7)
            ax2.fill_between(bottom_result.index, bottom_result, -20,
                             where=(bottom_result >= -20), facecolor=negCol, edgecolor=negCol,
                             alpha=0.5)
            ax2.fill_between(bottom_result.index, bottom_result, -80,
                             where=(bottom_result <= -80), facecolor=posCol, edgecolor=posCol,
                             alpha=0.5)
            ax2.set_ylim(0, -100)
            ax2.set_yticks([-20, -50, -80])


        elif bottom_iname in pposes:
            ax2.axhline(0, color=lineCol, linewidth=0.7)



    # Parameters for the overall Plot

    # Ax1 styling parameters
    ax1.grid(True, color='lightblue', alpha=0.5)
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(20))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.yaxis.label.set_color("grey")
    ax1.spines['bottom'].set_color("#5998ff")
    ax1.spines['top'].set_color("#5998ff")
    ax1.spines['left'].set_color("#5998ff")
    ax1.spines['right'].set_color("#5998ff")
    ax1.tick_params(axis='y', colors='grey')
    ax1.ticklabel_format(axis="y", style='plain')

    plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
    ax1.tick_params(axis='x', colors='grey')

    # ax1v styling parameters
    ax1v.axes.yaxis.set_ticklabels([])
    ax1v.grid(False)
    ax1v.set_ylim(0, 3 * max(ohlcv['volume']))
    ax1v.spines['bottom'].set_color("#5998ff")
    ax1v.spines['top'].set_color("#5998ff")
    ax1v.spines['left'].set_color("#5998ff")
    ax1v.spines['right'].set_color("#5998ff")
    ax1v.tick_params(axis='x', colors='grey')
    ax1v.tick_params(axis='y', colors='grey')

    # ax1txnv styling parameters
    ax1txnv.axes.yaxis.set_ticklabels([])
    ax1txnv.grid(False)
    #ax1txnv.set_ylim(0, 3 * max(txn_vol['txn_vol']))
    ax1txnv.spines['bottom'].set_color("#5998ff")
    ax1txnv.spines['top'].set_color("#5998ff")
    ax1txnv.spines['left'].set_color("#5998ff")
    ax1txnv.spines['right'].set_color("#5998ff")
    ax1txnv.tick_params(axis='x', colors='grey')
    ax1txnv.tick_params(axis='y', colors='grey')

    # ax1obv parameters
    ax1obv.axes.yaxis.set_ticklabels([])
    ax1obv.grid(False)
    plt.setp(ax1obv.get_xticklabels(), visible=False)

    # ax0
    ax0.ticklabel_format(axis="y", style='plain')
    ax0.grid(False)
    ax0.tick_params(axis='y', colors='grey')


    # ax2
    ax2.ticklabel_format(axis="y", style='plain')
    ax2.grid(False)
    ax2.tick_params(axis='y', colors='grey')



    # Bottom ticks for whole figure plotted on the bottom axe (ax2)
    ax2.yaxis.set_major_locator(mticker.MaxNLocator(nbins=3, prune='upper'))
    for label in ax2.xaxis.get_ticklabels():
        label.set_rotation(45)
        label.set_horizontalalignment('right')

    # Axes legends
    ax0.legend(ncol=3, fontsize=4, loc="upper left")
    ax1.legend(ncol=6, fontsize=4, loc="upper left")
    ax2.legend(ncol=3, fontsize=4, loc="upper left")

    # Hide the other ax labels, position adjustments
    plt.setp(ax0.get_yticklabels(), fontsize=8)
    plt.setp(ax1.get_yticklabels(), fontsize=8)
    plt.setp(ax2.get_yticklabels(), fontsize=8)
    plt.setp(ax2.get_xticklabels(), fontsize=8)



    plt.setp(ax0.get_xticklabels(), visible=False)
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax1v.get_xticklabels(), visible=False)
    plt.setp(ax1txnv.get_xticklabels(), visible=False)
    plt.setp(ax1obv.get_xticklabels(), visible=False)
    plt.subplots_adjust(bottom=.16)


    # Plot title
    plt.suptitle(f"{cname.upper()}/{fiat} {timezone}", color='grey', fontsize='small')

    fig.savefig(buf, dpi=600, format='png', facecolor=fig.get_facecolor())

    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")

    # Save the data
    #plot_save = fig.savefig('static/custom_plot.png', dpi=600, format='png',
    #                        facecolor=fig.get_facecolor())


    # Clear the current axes.
    plt.cla()
    # Clear the current figure.
    plt.clf()
    # Closes all the figure windows.
    plt.close('all')
    plt.close(fig)

    return data