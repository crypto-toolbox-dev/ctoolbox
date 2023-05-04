import os
import json
import pytz
import datetime

import custom_functions
import pandas as pd

from talib import abstract
from flask import Flask, render_template, request
from indicator_signals import buy_sell_signal
from plots import plot_pattern_signals, plot_momentum_signals, plotter
from parse_descriptions import get_indicator_descriptions, get_pattern_descriptions

from menu_items import top_bottom_functions, main_plot_functions, moving_Averages, timeframes, pattern_functions, \
    pattern_filter, pattern_signals, abstract_functions

from menu_items import fibonaccis as fibs

from hompage_functions import top_ten, fearandgreed, returns, cumulative_returns, plot_multiline,\
    hbars, multi_bars, fng_line, mcap_pie_data, pie_chart, pie_chart_broken, spread


from pprint import pprint

# Check necessary directories for the app, usually only needs to be run once.
check_dirs = False

if check_dirs == True:
    # Create necessary directories for the app
    if not os.path.isdir('datasets'):
        os.mkdir("datasets")

    if not os.path.isdir('txn_vol'):
        os.mkdir("txn_vol")

    if not os.path.isdir('descriptions'):
        os.mkdir("descriptions")

    if not os.path.isdir('notcurrentlyupdated'):
        os.mkdir("notcurrentlyupdated")

    if not os.path.isdir('coinnames'):
        os.mkdir("coinnames")

    if not os.path.isdir('fiat_exch_rates'):
        os.mkdir("fiat_exch_rates")


# Update the datasets for the app
updates_active = False  # Set to false during some debugging operations

if updates_active == True:

    from background_updater import timed_job as update_datasets
    from background_updater import timed_job_two as update_coinlists_and_fiatdata

    print("Background updates active")
    what_to_update_for = update_coinlists_and_fiatdata
    coin_datasets = update_datasets


app = Flask(__name__)

# Homepage
@app.route('/', methods=["GET", "POST"])
def hello():

    # Pull the current top 10 from CoinGecko
    homecoins = top_ten()

    # Copy the data to cleanup for display purposes on the homepage, without breaking or distorting anything else
    home_data = homecoins

    # MARQUEE
    # If the value is less than .1 to the 10 -3 power, suppress scientific notation on the template
    for data in home_data:
        if data['current_price'] < .1 * 10 ** -3:
            data['high_24h'] = "{:f}".format(data['high_24h'])
            data['low_24h'] = "{:f}".format(data['low_24h'])
            data['current_price'] = "{:f}".format(data['current_price'])

    spread_data = spread(homecoins)

    # FEAR AND GREED INDEX
    cryptofng = fearandgreed()

    # Prepare Fear and Greed
    cryptofng = cryptofng[::-1]
    cryptofng = cryptofng[-720:]
    cryptofng.fng_v = cryptofng.fng_v.astype('int64')
    labels = cryptofng.index
    values = cryptofng.fng_v

    # Plot Fear and Greed Index
    fng_plot = fng_line(labels, values, " ", (20, 5))


    # CUMULATIVE RETURNS

    # cumulative returns for all coins
    cumprod_daily_pct = cumulative_returns(homecoins)

    # cumulative returns without shiba-inu
    cumprod_daily_pct_no_shib = [c for c in cumprod_daily_pct if 'shib' not in c.columns]

    # cumulative returns without dogecoin
    cumprod_daily_pct_no_shib_no_doge = [c for c in cumprod_daily_pct_no_shib if 'doge' not in c.columns]


    # Cumulative returns for dogecoin and shiba-inu
    doge_cumprod_daily_pct = [c for c in cumprod_daily_pct if 'doge' in c.columns]
    shiba_cumprod_daily_pct = [c for c in cumprod_daily_pct if 'shib' in c.columns]

    # Plot cumulative returns

    # All coins
    cumprod_plot = plot_multiline(cumprod_daily_pct, 'Historic All coins', (7.4, 5.8))
    cumulative_bars = hbars(cumprod_daily_pct, 'Current Year All Coins')

    # Without doge and Shiba
    cumprod_plot_no_shib_doge = plot_multiline(cumprod_daily_pct_no_shib_no_doge, 'Historic without Shiba-Inu or Dogecoin', (7.4, 5.8))
    cumprod_plot_no_shib_line = plot_multiline(cumprod_daily_pct_no_shib, 'Historic without Shiba-Inu', (7.4, 5.8))
    cumulative_bars_no_shib_doge = hbars(cumprod_daily_pct_no_shib_no_doge, 'Current Year without Shiba-Inu or Dogecoin')
    cumulative_bars_no_shib = hbars(cumprod_daily_pct_no_shib, 'Current Year without Shiba_Inu)')

    # plot multibar plot of cumulative returns by year
    # Divided into 2 plots because of the vast differences in the data
    multiba = multi_bars(cumprod_daily_pct_no_shib, 'By Year without Shiba-Inu', 0, -3)
    multibb = multi_bars(cumprod_daily_pct_no_shib_no_doge, 'By Year without Shiba-Inu or Dogecoin', -3, None)

    # Doge and Shiba-Inu saw explosive returns 2020-2023.
    # Plotting them along the rest makes it impossible to effectively visualize the data for the others
    multib_shiba = multi_bars(shiba_cumprod_daily_pct, 'Shiba-Inu Cumulative Returns', -3, None)
    multib_doge = multi_bars(doge_cumprod_daily_pct, 'Dogecoin Cumulative Returns', -3, None)


    # NORMAL RETURNS
    # Dynamically change the type of Returns plotted depending on if button on template is clicked
    if request.method == 'POST':
        if request.form['submit_button'] == 'Daily':
            print("Daily Pressed")

            # Daily
            return_pct = returns(homecoins, 1)
            return_pct_shib = [c for c in return_pct if 'shib' not in c.columns]  # All except Shiba-Inu

            returns_plot = plot_multiline(return_pct, f'Historical {request.form["submit_button"]} Returns - All Coins')
            daily_bars = hbars(return_pct, f'Current Year {request.form["submit_button"]} Returns - All Coins')
            multibc = multi_bars(return_pct, f'{request.form["submit_button"]} Returns by Year - All Coins', 0, -2)
            multibd = multi_bars(return_pct, f'{request.form["submit_button"]} Returns by Year - All Coins', -2, None)

            # Only Shiba-Inu
            returns_plot_shib = plot_multiline(return_pct_shib,
                                               f'Historical {request.form["submit_button"]} Returns - Except Shiba-Inu')
            daily_bars_shib = hbars(return_pct_shib,
                                    f'Current Year {request.form["submit_button"]} Returns - Except Shiba-Inu')
            multibc_shib = multi_bars(return_pct_shib,
                                      f'{request.form["submit_button"]} Returns by Year - Except Shiba-Inu', 0, -2)
            multibd_shib = multi_bars(return_pct_shib,
                                      f'{request.form["submit_button"]} Returns by Year - Except Shiba-Inu', -2, None)


        elif request.form['submit_button'] == 'Weekly':
            print("Weekly Pressed")

            # Weekly
            return_pct = returns(homecoins, 7)
            return_pct_shib = [c for c in return_pct if 'shib' not in c.columns]  # All except Shiba-Inu

            returns_plot = plot_multiline(return_pct, f'Historical {request.form["submit_button"]} Returns - All Coins')
            daily_bars = hbars(return_pct, f'Current Year {request.form["submit_button"]} Returns - All Coins')
            multibc = multi_bars(return_pct, f'{request.form["submit_button"]} Returns by Year - All Coins', 0, -2)
            multibd = multi_bars(return_pct, f'{request.form["submit_button"]} Returns by Year - All Coins', -2, None)

            # Only Shiba-Inu
            returns_plot_shib = plot_multiline(return_pct_shib,
                                               f'Historical {request.form["submit_button"]} Returns - Except Shiba-Inu')
            daily_bars_shib = hbars(return_pct_shib,
                                    f'Current Year {request.form["submit_button"]} Returns - Except Shiba-Inu')
            multibc_shib = multi_bars(return_pct_shib,
                                      f'{request.form["submit_button"]} Returns by Year - Except Shiba-Inu', 0, -2)
            multibd_shib = multi_bars(return_pct_shib,
                                      f'{request.form["submit_button"]} Returns by Year - Except Shiba-Inu', -2, None)

        elif request.form['submit_button'] == 'Bi-Weekly':
            print("Bi-Weekly Pressed")

            # Bi-Weekly
            return_pct = returns(homecoins, 14)
            return_pct_shib = [c for c in return_pct if 'shib' not in c.columns]  # All except Shiba-Inu

            returns_plot = plot_multiline(return_pct, f'Historical {request.form["submit_button"]} Returns - All Coins')
            daily_bars = hbars(return_pct, f'Current Year {request.form["submit_button"]} Returns - All Coins')
            multibc = multi_bars(return_pct, f'{request.form["submit_button"]} Returns by Year - All Coins', 0, -2)
            multibd = multi_bars(return_pct, f'{request.form["submit_button"]} Returns by Year - All Coins', -2, None)

            # Only Shiba-Inu
            returns_plot_shib = plot_multiline(return_pct_shib,
                                               f'Historical {request.form["submit_button"]} Returns - Except Shiba-Inu')
            daily_bars_shib = hbars(return_pct_shib,
                                    f'Current Year {request.form["submit_button"]} Returns - Except Shiba-Inu')
            multibc_shib = multi_bars(return_pct_shib,
                                      f'{request.form["submit_button"]} Returns by Year - Except Shiba-Inu', 0, -2)
            multibd_shib = multi_bars(return_pct_shib,
                                      f'{request.form["submit_button"]} Returns by Year - Except Shiba-Inu', -2, None)

        elif request.form['submit_button'] == 'Monthly':
            print("Monthly Pressed")

            # Monthly
            return_pct = returns(homecoins, 30)
            return_pct_shib = [c for c in return_pct if 'shib' not in c.columns]  # All except Shiba-Inu

            returns_plot = plot_multiline(return_pct, f'Historical {request.form["submit_button"]} Returns - All Coins')
            daily_bars = hbars(return_pct, f'Current Year {request.form["submit_button"]} Returns - All Coins')
            multibc = multi_bars(return_pct, f'{request.form["submit_button"]} Returns by Year - All Coins', 0, -2)
            multibd = multi_bars(return_pct, f'{request.form["submit_button"]} Returns by Year - All Coins', -2, None)

            # Only Shiba-Inu
            returns_plot_shib = plot_multiline(return_pct_shib,
                                               f'Historical {request.form["submit_button"]} Returns - Except Shiba-Inu')
            daily_bars_shib = hbars(return_pct_shib,
                                    f'Current Year {request.form["submit_button"]} Returns - Except Shiba-Inu')
            multibc_shib = multi_bars(return_pct_shib,
                                      f'{request.form["submit_button"]} Returns by Year - Except Shiba-Inu', 0, -2)
            multibd_shib = multi_bars(return_pct_shib,
                                      f'{request.form["submit_button"]} Returns by Year - Except Shiba-Inu', -2, None)

        elif request.form['submit_button'] == 'Quarterly':
            print("Quarterly Pressed")

            # Quarterly
            return_pct = returns(homecoins, 90)
            return_pct_shib = [c for c in return_pct if 'shib' not in c.columns]  # All except Shiba-Inu

            returns_plot = plot_multiline(return_pct, f'Historical {request.form["submit_button"]} Returns - All Coins')
            daily_bars = hbars(return_pct, f'Current Year {request.form["submit_button"]} Returns - All Coins')
            multibc = multi_bars(return_pct, f'{request.form["submit_button"]} Returns by Year - All Coins', 0, -2)
            multibd = multi_bars(return_pct, f'{request.form["submit_button"]} Returns by Year - All Coins', -2, None)

            # Only Shiba-Inu
            returns_plot_shib = plot_multiline(return_pct_shib,
                                               f'Historical {request.form["submit_button"]} Returns - Except Shiba-Inu')
            daily_bars_shib = hbars(return_pct_shib,
                                    f'Current Year {request.form["submit_button"]} Returns - Except Shiba-Inu')
            multibc_shib = multi_bars(return_pct_shib,
                                      f'{request.form["submit_button"]} Returns by Year - Except Shiba-Inu', 0, -2)
            multibd_shib = multi_bars(return_pct_shib,
                                      f'{request.form["submit_button"]} Returns by Year - Except Shiba-Inu', -2, None)

        elif request.form['submit_button'] == 'Bi-Annual':
            print("Bi-Annual Pressed")

            # Bi-annually
            return_pct = returns(homecoins, 180)
            return_pct_shib = [c for c in return_pct if 'shib' not in c.columns]  # All except Shiba-Inu

            returns_plot = plot_multiline(return_pct, f'Historical {request.form["submit_button"]} Returns - All Coins')
            daily_bars = hbars(return_pct, f'Current Year {request.form["submit_button"]} Returns - All Coins')
            multibc = multi_bars(return_pct, f'{request.form["submit_button"]} Returns by Year - All Coins', 0, -2)
            multibd = multi_bars(return_pct, f'{request.form["submit_button"]} Returns by Year - All Coins', -2, None)

            # Only Shiba-Inu
            returns_plot_shib = plot_multiline(return_pct_shib,
                                               f'Historical {request.form["submit_button"]} Returns - Except Shiba-Inu')
            daily_bars_shib = hbars(return_pct_shib,
                                    f'Current Year {request.form["submit_button"]} Returns - Except Shiba-Inu')
            multibc_shib = multi_bars(return_pct_shib,
                                      f'{request.form["submit_button"]} Returns by Year - Except Shiba-Inu', 0, -2)
            multibd_shib = multi_bars(return_pct_shib,
                                      f'{request.form["submit_button"]} Returns by Year - Except Shiba-Inu', -2, None)

        elif request.form['submit_button'] == 'Annual':
            print("Annual Pressed")

            # Yearly
            return_pct = returns(homecoins, 360)
            return_pct_shib = [c for c in return_pct if 'shib' not in c.columns]  # All except Shiba-Inu

            returns_plot = plot_multiline(return_pct, f'Historical {request.form["submit_button"]} Returns - All Coins')
            daily_bars = hbars(return_pct, f'Current Year {request.form["submit_button"]} Returns - All Coins')
            multibc = multi_bars(return_pct, f'{request.form["submit_button"]} Returns by Year - All Coins', 0, -2)
            multibd = multi_bars(return_pct, f'{request.form["submit_button"]} Returns by Year - All Coins', -2, None)

            # Only Shiba-Inu
            returns_plot_shib = plot_multiline(return_pct_shib,
                                               f'Historical {request.form["submit_button"]} Returns - Except Shiba-Inu')
            daily_bars_shib = hbars(return_pct_shib,
                                    f'Current Year {request.form["submit_button"]} Returns - Except Shiba-Inu')
            multibc_shib = multi_bars(return_pct_shib,
                                      f'{request.form["submit_button"]} Returns by Year - Except Shiba-Inu', 0, -2)
            multibd_shib = multi_bars(return_pct_shib,
                                      f'{request.form["submit_button"]} Returns by Year - Except Shiba-Inu', -2, None)

        else:
            print("Nothing Happens")
            pass  # unknown

    # Else if its a GET request just plot Daily Returns
    else:
        print("Was a GET request plotting daily returns")
        # Plot Returns Line and bars
        return_pct = returns(homecoins, 1)
        returns_plot = plot_multiline(return_pct, 'Historical Daily Returns', (7.4, 5.8))
        daily_bars = hbars(return_pct, 'Current Year Daily Returns')

        # Plot multi-bar plot of returns by year
        # Divided into 2 plots because of the vast differences in the data
        multibc = multi_bars(return_pct, 'Daily Returns by Year', 0, -2)
        multibd = multi_bars(return_pct, 'Daily Returns by Year', -2, None)

        # All except Shiba-Inu
        return_pct_shib = [c for c in return_pct if 'shib' not in c.columns]

        # Only Shiba-Inu
        returns_plot_shib = plot_multiline(return_pct_shib, 'Historical Daily Returns - Except Shiba-Inu')
        daily_bars_shib = hbars(return_pct_shib, 'Current Year Daily Returns - Except Shiba-Inu')
        multibc_shib = multi_bars(return_pct_shib, 'Daily Returns by Year - Except Shiba-Inu', 0, -2)
        multibd_shib = multi_bars(return_pct_shib, 'Daily Returns by Year - Except Shiba-Inu', -2, None)

    # Pie Charts for Market Cap
    market_capital = mcap_pie_data()
    pie = pie_chart(market_capital, (12, 9))
    broken_pie = pie_chart_broken(market_capital, (12, 9))

    return render_template('home.html', fng=fng_plot, cumprod=cumprod_plot, returns=returns_plot,
                           cumprod_bar=cumulative_bars, daily_b=daily_bars, cumprod_no=cumprod_plot_no_shib_doge,
                           cumprod_no_sl=cumprod_plot_no_shib_line,
                           cumprod_bar_no_shib=cumulative_bars_no_shib, mb=multiba, mb2=multibb,
                           cumprod_bar_no_shib_doge=cumulative_bars_no_shib_doge,
                           doge_cret=multib_doge, shiba_cret=multib_shiba,
                           mb3=multibc, mb4=multibd, p=pie, p2=broken_pie, marquee_data=home_data, spreads=spread_data,
                           returns_shib=returns_plot_shib, returns_bars_shib=daily_bars_shib,
                           returns_multi_bars_shib=multibc_shib, returns_multi_bars_shib2=multibd_shib)


# About the app page
@app.route('/about')
def about():
    return render_template('about.html')

# Custom Plots
@app.route('/custom')
def custom():
    fiat = request.args.get('fiat', None)
    ccoin = request.args.get('ccoin', None)
    top_plot = request.args.get('top_plot', None)
    main_plot = request.args.get('main_plot', None)
    bottom_plot = request.args.get('bottom_plot', None)
    pattern = request.args.get('pattern', None)
    movavg = request.args.get('frstma', None)
    movavg2 = request.args.get('scndma', None)
    SP = request.args.get('timeframe', None)
    tz = request.args.get('timezone', None)
    fibonacci = request.args.get('fibonacci', None)
    ST = request.args.get("plot_start", None)

    # Timezones
    tzones = pytz.all_timezones

    # read coin names and symbols
    f = open("coinnames/cryptocoins.json", "r")
    coins = json.loads(f.read())
    symbols = [i.upper() for i in coins.keys()]
    names = [i.capitalize() for i in coins.values()]

    # Put them in their own dictionary of dictionaries
    coin_names = {}
    for i in range(len(symbols)):
        coin_names[symbols[i]] = {'Cryptocoin': names[i]}

    # Read the current exchange rates
    f = open("fiat_exch_rates/fiat.json", "r")
    ex = json.loads(f.read())

    # Getting the data for the specified coin for the custom plot
    plot_kwargs = {}

    # Lookback period for the custom plot, user specified, defaults to 30 so things don't break
    if SP:
        print(timeframes[SP])
        id1 = timeframes[SP].index("(")
        id2 = timeframes[SP].index(")")
        days = timeframes[SP][id1 + len("") + 1: id2]
        days = days.split(" ")
        SP = int(days[0])
        print(SP)

    else:
        SP = 90
        print(SP)

    # User select timezone for the plot
    if tz:
        timezone = tz
        plot_kwargs['timezone'] = timezone
        print(timezone)

    else:
        timezone = 'US/Eastern'
        plot_kwargs['timezone'] = timezone
        print(timezone)

    # Desired cryptocoin. No point in running the rest of the block if this is empty
    if ccoin:
        print(ccoin)

        # OHLCV data for the coin
        df = pd.read_csv(f'datasets/{coin_names[ccoin]["Cryptocoin"].lower()}({ccoin.lower()}).csv', index_col=0)
        df.index = pd.to_datetime(df.index)

        # On chain-transaction volume if available for the coin
        try:
            tx_vol = pd.read_csv(f'txn_vol/{coin_names[ccoin]["Cryptocoin"].lower()}({ccoin.lower()}).csv', index_col=0)
            tx_vol.index = pd.to_datetime(tx_vol.index)

        except FileNotFoundError:
            print(f"TXN Volume data not available for {ccoin}")

        # Sometimes due to daylight savings switches (and vice versa) some timezones cease to exist for a time
        # In case that revert to UTC to prevent a crash
        try:
            df = df.tz_localize(timezone)
        except pytz.exceptions.NonExistentTimeError:
            print("Timezone Error. Reverted to UTC.")
            df = df.tz_localize('UTC')

        # Plot subsection of the data in the past, starting from a user specified "today" and going back SP days
        # Check the value of ST is a date in the correct format and within the dataset
        if ST in df.index:
            ST = datetime.datetime.strptime(ST, "%Y-%m-%d")
            SP = ST - datetime.timedelta(SP)
            print(ST)
            print(SP)
        # else just take the most recent date available
        else:
            ST = df.index[-1]
            SP = ST - datetime.timedelta(SP)
            print(ST)
            print(SP)

        # Currency localization
        if fiat:
            rate = ex[fiat]['rate']
            df = df.loc[:,:] * rate

            plot_kwargs['cname'] = ccoin
            plot_kwargs['ohlcv'] = df[SP:ST]
            plot_kwargs['fiat'] = fiat
            plot_kwargs['plot_name'] = coin_names[ccoin]["Cryptocoin"].capitalize()
            print(fiat)

        else:
            plot_kwargs['cname'] = ccoin
            plot_kwargs['ohlcv'] = df[SP:ST]
            plot_kwargs['fiat'] = 'USD'
            print(fiat)

        try:
            plot_kwargs['txn_vol'] = tx_vol[SP:ST]
        except UnboundLocalError:
            print(f"No on-chain transaction data available for {ccoin}")


        # Patterns for the custom plot
        if pattern:
            print(pattern)
            pat_func = pattern_functions[pattern][1]
            print(pat_func)
            patresult = pat_func(df)
            print(patresult)
            patresult = patresult[SP:ST]
            print(patresult)


            plot_kwargs['patname'] = pattern
            plot_kwargs['patresult'] = patresult

        # Top plot
        if top_plot:
            print(top_plot)

            if top_plot == 'NVTS' or top_plot == 'NVTR':
                # Necessary because these indicators pull data directly from API, not transformed by the app
                top_func = top_bottom_functions[top_plot][1]
                s = df.index[-1]
                tpresult = top_func(df, ccoin, ST, SP)
                tpresult = tpresult[SP:ST]
                top_color = top_bottom_functions[top_plot][2]

                plot_kwargs['top_iname'] = top_plot
                plot_kwargs['top_result'] = tpresult
                plot_kwargs['top_color'] = top_color

            else:
                top_func = top_bottom_functions[top_plot][1]
                tpresult = top_func(df)
                tpresult = tpresult[SP:ST]
                top_color = top_bottom_functions[top_plot][2]

                plot_kwargs['top_iname'] = top_plot
                plot_kwargs['top_result'] = tpresult
                plot_kwargs['top_color'] = top_color


        # Main plot
        if main_plot:
            print(main_plot)
            main_func = main_plot_functions[main_plot][1]
            mpresult = main_func(df)
            mpresult = mpresult[SP:ST]
            main_color = main_plot_functions[main_plot][2]

            plot_kwargs['main_iname'] = main_plot
            plot_kwargs['main_result'] = mpresult
            plot_kwargs['main_color'] = main_color

        # First moving average
        if movavg:
            print(movavg)
            # getting input with name = fname in HTML form
            periods = request.args.get("fmap", None)

            if periods:
                try:
                    periods = int(periods)
                    print(periods)
                    mafunc = moving_Averages[movavg][1]
                    maresult = mafunc(df, periods)
                    maresult = maresult[SP:ST]

                    plot_kwargs['first_mav_name'] = movavg
                    plot_kwargs['first_mav'] = maresult
                    plot_kwargs['first_mav_p'] = periods

                except ValueError:
                    print("Number not entered or invalid for MA periods.")

        # Second moving average
        if movavg2:
            print(movavg2)
            periods = request.args.get("smap", None)

            if periods:
                try:
                    periods = int(periods)
                    print(periods)
                    mafunc = moving_Averages[movavg2][1]
                    ma2result = mafunc(df, periods)
                    ma2result = ma2result[SP:ST]

                    plot_kwargs['second_mav_name'] = movavg2
                    plot_kwargs['second_mav'] = ma2result
                    plot_kwargs['second_mav_p'] = periods

                except ValueError:
                    print("Number not entered or invalid for MA2 periods.")


        # Fibonacci Extension or Reversal Levels based on an observable, user specified trend
        if fibonacci:
            print(fibonacci)
            fib_func = fibs[fibonacci][1]

            # If retrace levels are selected
            if fibonacci == 'FIBRET':
                start = request.args.get("fexs")
                end = request.args.get("fexe")
                reverse = request.args.get("frev")

                # If one of the trend inputs is missing
                if not start or not end or not reverse:
                    print("Missing one of the trend inputs. Can't plot Fib Retracement")

                elif start not in df.index or end not in df.index or reverse not in df.index:
                    print("This is not a date in the data. Cannot proceed with Retracement.")

                else:
                    fibresult = fib_func(df, start, end, reverse)
                    fibcolor = fibs[fibonacci][2]
                    fiblabel = fibs[fibonacci][3]

                    plot_kwargs['fib_trev'] = reverse
                    plot_kwargs['fibonacci'] = fibonacci
                    plot_kwargs['fibonacci_levels'] = fibresult
                    plot_kwargs['fibonacci_colors'] = fibcolor
                    plot_kwargs['fibonacci_labels'] = fiblabel
                    plot_kwargs['fib_ts'] = start
                    plot_kwargs['fib_te'] = end

            # Else if extension levels are selected
            else:
                start = request.args.get("fexs")
                end = request.args.get("fexe")

                # If one of the trend inputs is missing
                if not start or not end:
                    print("Missing one of the trend inputs. Can't plot Fib Extension")

                elif start not in df.index or end not in df.index:
                    print("This is not a date in the data. Cannot proceed with Retracement.")

                else:
                    fibresult = fib_func(df, start, end)
                    fibcolor = fibs[fibonacci][2]
                    fiblabel = fibs[fibonacci][3]

                    plot_kwargs['fibonacci'] = fibonacci
                    plot_kwargs['fibonacci_levels'] = fibresult
                    plot_kwargs['fibonacci_colors'] = fibcolor
                    plot_kwargs['fibonacci_labels'] = fiblabel
                    plot_kwargs['fib_ts'] = start
                    plot_kwargs['fib_te'] = end

        # Bottom plot
        if bottom_plot:
            print(bottom_plot)

            if bottom_plot == 'NVTS' or bottom_plot == 'NVTR':
                bot_func = top_bottom_functions[bottom_plot][1]
                s = df.index[-1]
                bpresult = bot_func(df, ccoin, ST, SP)
                bpresult = bpresult[SP:ST]
                bottom_color = top_bottom_functions[bottom_plot][2]

                plot_kwargs['bottom_iname'] = bottom_plot
                plot_kwargs['bottom_result'] = bpresult
                plot_kwargs['bottom_color'] = bottom_color


            else:
                bot_func = top_bottom_functions[bottom_plot][1]
                bpresult = bot_func(df)
                bpresult = bpresult[SP:ST]
                bottom_color = top_bottom_functions[bottom_plot][2]

                plot_kwargs['bottom_iname'] = bottom_plot
                plot_kwargs['bottom_result'] = bpresult
                plot_kwargs['bottom_color'] = bottom_color

        # Call the plotting function for the custom plot
        custom_plot = plotter(**plot_kwargs)

    try:
        return render_template('custom_plots.html', top=top_bottom_functions, main=main_plot_functions,
                           frstma=moving_Averages, scndma=moving_Averages, fibonaccis=fibs,
                           bottom=top_bottom_functions, patterns=pattern_functions,
                           crycoin=coin_names, range=timeframes, fiatcurr=ex, zones=tzones, plot=custom_plot)

    except UnboundLocalError:

        custom_plot = None

        return render_template('custom_plots.html', top=top_bottom_functions, main=main_plot_functions,
                               frstma=moving_Averages, scndma=moving_Averages, fibonaccis=fibs,
                               bottom=top_bottom_functions, patterns=pattern_functions,
                               crycoin=coin_names, range=timeframes, fiatcurr=ex, zones=tzones, plot=custom_plot)



# Candlestick Pattern Signals
@app.route('/patterns')
def show_patterns():
    pattern = request.args.get('pattern', None)

    # read coin names and symbols
    f = open("coinnames/cryptocoins.json", "r")
    coins = json.loads(f.read())
    symbols = [i.upper() for i in coins.keys()]
    names = [i.capitalize() for i in coins.values()]

    # Put them in their own dictionary of dictionaries
    coin_names = {}
    pattern_plots = {}

    for i in range(len(symbols)):
        coin_names[symbols[i]] = {'Cryptocoin': names[i]}

    # Get icons for the view
    try:
        icon = top_ten(limit=100)
        coin_image = {k: {'Images': v} for (k, v) in
                      zip([x['symbol'].upper() for x in icon], [x['image'] for x in icon])}

    except Exception as e:
        print("Couldnt get icons")
        print(f"The reason is {e}")


    # When pattern was selected
    if pattern:
        datafiles = os.listdir('datasets')
        timezone = 'UTC'
        pattern_name = pattern_signals[pattern].split("(")[0]

        # Get descriptions of the indicators from text files
        descript = get_pattern_descriptions(pattern)

        # Iterate over files in the dataset directory
        for dataset in datafiles:
            df = pd.read_csv(f'datasets/{dataset}', index_col=0)
            df.index = pd.to_datetime(df.index)
            df = df.tz_localize(timezone)

            pat_func = getattr(abstract, pattern)
            id1 = dataset.index("(")
            id2 = dataset.index(")")
            csymbol = dataset[id1 + len("") + 1: id2].upper()

            # Apply user selected function to the dataset and check if a pattern was detected "today"
            result = pat_func(df)
            last = result.tail(1).values[0]

            # Signal detection and plotting logic
            # Differentiate between patterns that can return negative values and those that do not.
            # Yellow arrows will be used for the latter, it is not necessarily a bullish or bearish signal
            if pattern in pattern_filter:
                try:
                    if last > 0:
                        coin_names[csymbol][pat_func] = 'Detected'

                        # Generate the Plot
                        pattern_plots[csymbol] = plot_pattern_signals(df, result, pattern, dataset, csymbol, SP=30)

                    else:
                        coin_names[csymbol][pat_func] = None

                except KeyError:
                    print(f"{dataset}{csymbol} not in current coin list anymore")

            else:

                try:
                    if last > 0:
                        coin_names[csymbol][pat_func] = 'Bullish'

                        # Generate the plot
                        pattern_plots[csymbol] = plot_pattern_signals(df, result, pattern, dataset, csymbol, SP=30)

                    elif last < 0:
                        coin_names[csymbol][pat_func] = 'Bearish'

                        # Generate the plot
                        pattern_plots[csymbol] = plot_pattern_signals(df, result, pattern, dataset, csymbol, SP=30)

                    else:
                        coin_names[csymbol][pat_func] = None

                except KeyError:
                    print(f"{dataset}{csymbol} not in current coin list anymore")


    try:
        return render_template('pattern_signals.html', patterns=pattern_signals, cryptocoins=coin_names, pattern=pat_func,
                               pname=pattern, desc=descript, pcode=pattern_name, plot=pattern_plots, icons=coin_image)

    except UnboundLocalError:
        descript = get_indicator_descriptions(pattern)
        pat_func = getattr(abstract, 'CDLDOJI')
        pattern_name = 'None'

        return render_template('pattern_signals.html', patterns=pattern_signals, cryptocoins=coin_names, pattern=pat_func,
                               pname=pattern, desc=descript, pcode=pattern_name, plot=pattern_plots, icons=coin_image)


# Technical Indicator Signals
@app.route('/indicators')
def show_indicators():
    indicator = request.args.get('indicator', None)

    # read coin names ansd symbols
    f = open("coinnames/cryptocoins.json", "r")
    coins = json.loads(f.read())
    symbols = [i.upper() for i in coins.keys()]
    names = [i.capitalize() for i in coins.values()]

    # Store the in-memory plots for the desired indicator
    coin_names = {}
    indicator_plots = {}

    # Put them in their own dictionary of dictionaries
    for i in range(len(symbols)):
        coin_names[symbols[i]] = {'Cryptocoin': names[i]}

    # Get icons for the view
    try:
        icon = top_ten(limit=100)
        coin_image = {k: {'Images': v} for (k, v) in
                      zip([x['symbol'].upper() for x in icon], [x['image'] for x in icon])}

    except Exception as e:
        print("Couldnt get icons")
        print(f"The reason is {e}")

    # When an indicator is selected
    if indicator:
        datafiles = os.listdir('datasets')   # The data for the cryptocoins
        timezone = 'UTC'
        indicator_name = abstract_functions[indicator].split("(")[0] + " " + f"({indicator})"

        # Get descriptions of the indicators from text files
        descript = get_indicator_descriptions(indicator)

        # For all coins we acquired data for
        for dataset in datafiles:
            df = pd.read_csv(f'datasets/{dataset}', index_col=0)
            df.index = pd.to_datetime(df.index)
            df = df.tz_localize(timezone)

            # Try if the desired indicator is included in talib
            try:
                indi_func = getattr(abstract, indicator)
                id1 = dataset.index("(")
                id2 = dataset.index(")")
                csymbol = dataset[id1 + len("") + 1: id2].upper()
                result = indi_func(df)
                cross_check = result.tail(2).values[0]  # The day before today, check for pos/neg or zero line crossover
                last = result.tail(1).values[0]

            # If function not included in talib or different default parameters are needed
            except Exception:
                indi_func = custom_functions.function_choser(indicator)
                id1 = dataset.index("(")
                id2 = dataset.index(")")
                csymbol = dataset[id1 + len("") + 1: id2].upper()
                result = indi_func(df)
                cross_check = result.tail(2).values[0]  # The day before today, check for pos/neg or zero line crossover
                last = result.tail(1).values[0]

            # Evaluate the indicator data and see if the data has generated a signal today
            signal_value = buy_sell_signal(indicator, last, cross_check)

            if signal_value != None:
                print(f"{indicator} is {signal_value} for {csymbol}")

                try:
                    coin_names[csymbol][indi_func] = signal_value

                    # Generate the Plot
                    indicator_plots[csymbol] = plot_momentum_signals(df, indicator, result, dataset, indicator_name,
                                                                     SP=30)

                except KeyError:
                    print(f"{dataset}{csymbol} not in current coin list anymore")

    try:
        return render_template('indicator_signals.html', indicators=abstract_functions, cryptocoins=coin_names,
                               indicator=indi_func, iname=indicator, desc=descript, icode=indicator_name,
                               plot=indicator_plots, icons=coin_image)

    # This was done to address the fact that when no indicator is selected the app crashes, such as when first
    # loading the template for the indicators upon app startup
    except UnboundLocalError:

        # Set the RSI as the default indicator and description
        descript = get_indicator_descriptions(indicator)
        indi_func = getattr(abstract, 'RSI')
        indicator_name = 'None'

        return render_template('indicator_signals.html', indicators=abstract_functions, cryptocoins=coin_names,
                               indicator=indi_func, iname=indicator, desc=descript, icode=indicator_name,
                               plot=indicator_plots, icons=coin_image)


# Run the application
if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)