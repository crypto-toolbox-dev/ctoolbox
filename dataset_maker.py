import pandas as pd
from bs4 import BeautifulSoup
import os
import shutil
import json
import time
import datetime
import requests



def revise_datasets(new, datafiles, cl):
    '''
    This function compares the current top X coins to those in the existing cryptocoins.json
    This makes sure that data for coins that used to be in the top X but aren't any longer
    still get dataset updates.

    :param new: The current top X coins
    :param datafiles: Existing datasets
    :return:
    '''

    symbols = []
    names = []

    for dataset in datafiles:
        id1 = dataset.index("(")
        id2 = dataset.index(")")
        csymbol = dataset[id1 + len("") + 1: id2].upper()
        cname = dataset[:id1]

        symbols.append(csymbol)
        names.append(cname)

    symbols = [x.lower() for x in symbols]
    names = [x.lower() for x in names]

    res = {symbols[i]: names[i] for i in range(len(symbols))}

    # Move old coins that have moved from the top positions by market cap out of the dataset dir to save
    # on update time and API calls. But keep the data anyway
    for k, v in res.items():
        if k not in new.keys():
            print(f"{v} ({k.upper()}) no longer in the top {cl} by Market Cap.")
            print("Moving into storage...")

            try:
                shutil.move(
                    f"datasets/{v.lower()}({k.lower()}).csv",
                    f"notcurrentlyupdated/{v.lower()}({k.lower()}).csv"
                )

            except FileNotFoundError:
                print(f"data not present for {v} ({k.upper()}). Nothing to move.")

    return new

def fiat_exchange_rates():
    '''
    Get fiat currency exchange rates from moneyconvert.net api which sources from
    currencyrate.today which sources from all of those here https://currencyrate.today/page/sources
    :return: Dictionary with a list of currency tickers and the current rate of exchange against USD
    '''

    url = "https://cdn.moneyconvert.net/api/latest.json"

    try:
        response = requests.get(url)
        print("Print Fiat Exchange Rates from Moneyconvert.et")
        print(f"Response Code:{response.status_code}")
        #print(f"Response Headers:{response.headers}")
        data = response.json()

    except Exception:
        print("Fiat exchange rate call failed.")
        print("Trying again in 30 seconds...")
        time.sleep(30)
        response = requests.get(url)
        print("Print Fiat Exchange Rates from Moneyconvert.et")
        print(f"Response Code:{response.status_code}")
        #print(f"Response Headers:{response.headers}")
        data = response.json()

    return data['rates']


def get_fiat_names():
    '''
    Scrape the names of fiat and precious metals from wikipedia
    Combine them with the exchange rates
    Purpose is to make it easier to know
    Which fiat currency or precious metal
    you are selecting in the app dropdown menus
    :return:  pandas dataframe with tickers, names, and exchange rates
    '''

    # Scrape
    url = "https://en.wikipedia.org/wiki/ISO_4217#National_currencies"

    try:
        req = requests.get(url)
        print("Scraping Fiat names from Wikipedia.")
        print(f"REST Response Code: {req.status_code}")
        soup = BeautifulSoup(req.text, "html.parser")

        # Search tags
        results = soup.findAll("table", {"class": "wikitable sortable mw-collapsible"})
        lines = results[0].findAll("td")

        # Collect names and tickers
        fiat_names = {k.get_text(): v.get_text() for (k, v) in zip(lines[::5], lines[3::5])}

        # Collect names and exchange rates
        if not os.path.isfile("fiat_exch_rates/exchrates.json"):
            with open("fiat_exch_rates/exchrates.json", 'w') as outfile:
                json.dump(fiat_names, outfile)


        f = open("fiat_exch_rates/exchrates.json", "r")
        ex = json.loads(f.read())

        # Combine
        names = pd.DataFrame(fiat_names.values(), index=fiat_names.keys(), columns=['name'])
        exvals = pd.DataFrame(ex.values(), index=ex.keys(), columns=['rate'])

        # Cleanup
        rates_and_names = exvals.merge(names, left_on=exvals.index, right_on=names.index)
        rates_and_names.rename(columns={'key_0': 'tickers'}, inplace=True)
        rates_and_names = rates_and_names.set_index('tickers')


    except ConnectionError:
        print("There was a problem getting the Fiat names")
        print("Using the existing local list instead")

        f = open("fiat_exch_rates/fiat.json", "r")
        rates_and_names = json.loads(f.read())

    return rates_and_names


def top_hundred_coins(limit):
    '''
    Get the top X coins according to CoinGecko.com
    :param limit: Integer, number of coins from top to bottom to pull from API
    :return: A json dictionary of the top X coins which the greater webapp will reference
    '''

    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false"

    try:
        response = requests.get(url)

        print(f"CoinGecko API call for Top {limit} CryptoCoins by Market Capitalization")
        print(f"CoinGecko Response Code: {response.status_code}")
        #print(f"CoinGecko Headers:{response.headers}")

        data = response.json()
        data = data[:limit]

    except Exception as e:
        print(f"CoinGecko API refused connection for top {limit} coins. Retrying in 30 seconds...")
        print(f"The reason is: {e}")
        time.sleep(30)
        response = requests.get(url)

        data = response.json()
        data = data[:limit]

    # Drop stablecoins and wrappers
    stablecoins = ['usdt', 'busd', "ust", 'mim', 'frax', 'tusd', 'usdc', 'dai', 'usdp', 'usdc', 'usdd', 'usdn']
    wrappercoins = ['wbtc', 'hbtc', 'steth', 'cdai']
    data = [d for d in data if d['symbol'] not in stablecoins]
    data = [d for d in data if d['symbol'] not in wrappercoins]

    # Get a dictionary of coins and their symbols for the webapp and lists for the datagrabber
    coins = [coin['id'] for coin in data]
    symbols = [coin['symbol'] for coin in data]
    cryptocoins = dict(zip(symbols, coins))

    return cryptocoins


def coingecko_minute_data(coin, start_epoch, end_epoch, symbol):
    '''
    Get today's data by the minute so that the
    candlesticks update everytime the script is
    run in pseudo real time
    :return:
    '''

    print(f"Calling CoinGecko for Minute data on {coin}({symbol}).....")
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart/range?vs_currency=usd&from={start_epoch}&to={end_epoch}"

    count = 3

    # Keep trying the API unless the count is 0 or one of the other conditions is met
    while count > 0:
        response = requests.get(url)

        # Response is good, break loop and proceed
        if int(response.status_code) == 200:
            data = response.json()

            # Prepare prices as we did before but this time its minutes of the present day, not the hours of the prior 90 days
            new_df = pd.DataFrame(data['prices'], columns=['dates', 'prices'])

            break

        # Server busy, try again after the number of seconds told by the API
        elif int(response.status_code) == 429:
            print(f"CoinGecko Response: {response.status_code}")
            print(f"Waiting {response.headers['Retry-After']} Seconds....")
            time.sleep(int(response.headers['Retry-After']))

        # If the API can't find the coin or can't service the request, break the loop and return nothing
        elif int(response.status_code) == 404 or int(response.status_code) == 508:
            print(f"CoinGecko Response: {response.status_code}")
            print("Coin Not found or API is unavailable/ having problems...")

            break

        # If anything else happened try again after 30 seconds just in case
        else:
            count -= 1
            print(f"CoinGecko Response: {response.status_code}")
            print(f"Trying Again in 30 Seconds....")
            print(f"Will try {count} more times...")

            time.sleep(30)

    # Catches any other unforseen problems in getting the data, and the function returns nothing if so
    try:

        new_df['dates'] = pd.to_datetime(new_df['dates'], unit='ms')
        new_df = new_df.set_index('dates')

        # Prepare volume as we did before but this time its minutes of the present day, not the hours of the prior 90 days
        volumes_df = pd.DataFrame(data['total_volumes'], columns=['dates', 'volumes'])
        volumes_df['dates'] = pd.to_datetime(volumes_df['dates'], unit='ms')
        volumes_df = volumes_df.set_index('dates')

        # Calculate todays Open High Low Close Volume(OHLCV) values
        min_df = new_df.groupby([new_df.index.date]).min()  # Get the lows for each day
        max_df = new_df.groupby([new_df.index.date]).max()  # Get the highs for each day
        open_df = new_df.groupby([new_df.index.date]).first()  # Get the first value of each day for Open
        close_df = new_df.groupby([new_df.index.date]).last()  # Get the last value of each day for Close
        volume_df = volumes_df.groupby([volumes_df.index.date]).last()  # Get the latest volume for the day

        todays_ohlc_df = pd.concat(
            [open_df['prices'], max_df['prices'], min_df['prices'], close_df['prices'], volume_df['volumes']],
            axis=1, keys=['Open', 'High', 'Low', 'Close', 'Volume'])

        todays_ohlc_df.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close',
                                       'Volume': 'volume'}, inplace=True)

        return todays_ohlc_df

    # Print the error to the console to debug later or just to know what happened
    except Exception as e:
        print(f"Couldn't get CoinGecko minute data for  {coin} {symbol}")
        print(f"Problem was: {e} ")

        # So we know if it kept trying and found nothing or if there was another reason
        if count == 0:
            print(f"The Retry attempts were exhausted...")


        return None


def messari_historic(coin, symbol, from_date, at_date):
    '''
    :param coin: String, The selected cryptocoin
    :param start_date: String, the most recent date
    :param end_date: String, The furthest back date
    :return: DataFrame with [open,high,low,close,volume] columns
    '''

    print(f"Calling Messari API for daily data on {coin}({symbol}).....")

    url = f"https://data.messari.io/api/v1/assets/{coin}/metrics/ohlcv/time-series?start={from_date}&end={at_date}&interval=1d&timestamp-format=rfc3339"
    alt_url = f"https://data.messari.io/api/v1/assets/{symbol}/metrics/ohlcv/time-series?start={from_date}&end={at_date}&interval=1d&timestamp-format=rfc3339"

    count = 3

    while count > 0:
        response = requests.get(url)

        if int(response.status_code) == 200:
            print(f"Messari Response Code: {response.status_code}")
            print(f"Messari found {coin} by name Match!")
            data = response.json()
            df = pd.DataFrame(data['data']['values'], columns=data['data']['parameters']['columns'])

            break

        # Unlike with CoinGecko, a 404 from Messari is not necessarily the end. Try the ticker of the coin instead
        elif int(response.status_code) == 404:
            print(f"Messari Response Code: {response.status_code}")
            print("Trying for a ticker symbol match....")

            response = requests.get(alt_url)
            data = response.json()

            try:
                df = pd.DataFrame(data['data']['values'], columns=data['data']['parameters']['columns'])
                print(f"Messari found {coin} by Ticker Symbol match!")

                break

            except Exception as e:
                print(f"Couldn't FIND data for {coin} {symbol} from Messari API")
                print(f"Reason: {e}")

                break

        elif int(response.status_code) == 429:
            print(f"Messari API Response: {response.status_code}")
            print(f"Waiting {response.headers['retry-after']} Seconds")

            # Sometimes Messari will return a retry after of seconds in the tens of thousands
            # If this is the case there is no point in trying again. Break the loop
            if int(response.headers['retry-after']) > 400:
                print("Messari API no longer accepting requests for OHLCV data today...")
                break
            else:
                time.sleep(int(response.headers['retry-after']))


        else:
            count -= 1
            print(f"Messari API Response: {response.status_code}")
            print(f"Trying Again in 30 Seconds....")
            print(f"Will try {count} more times...")
            time.sleep(30)

    # Catch any other problems, return nothing in that case
    try:
        df.rename(columns={'timestamp': 'dates'}, inplace=True)
        df['dates'] = pd.to_datetime(df['dates'], format='%Y-%m-%d')
        df['dates'] = pd.to_datetime(df['dates']).dt.date
        df.index = df['dates']
        df.drop(columns=['dates'], inplace=True)

        return df


    # Print the error to the console to debug later or just to know what happened
    except Exception as e:
        print(f"Couldn't get Messari daily data for {coin} {symbol}")
        print(f"Problem was: {e} ")

        # So we know if it kept trying and found nothing or if there was another reason
        if count == 0:
            print(f"The Retry attempts were exhausted...")

        return None



def coingecko_historic(source_df, ninetyDayPeriods, coin, symbol):
    '''
    Gets ohlc data in 90 day tranches. Default is 6 tranches.
    90 days is the maximum period for which hourly data is returned, which is ncessary
    to calculate the open,high,low,close, and close volume for each 24 hour period in each 90 days

    :param source_df: Existing data, csv file into DataFrame
    :param ninetyDayPeriods: The number of 90 day chunks to request, starting from the present date
    :param coin: The coin for which to request data
    :param fiat: The fiat currency desired
    :return: A single dataframe to update the existing data from
    '''

    print("CoinGecko API backup historic data")
    print(f"{coin}({symbol})")

    count = ninetyDayPeriods
    df_list = [source_df]

    while count > 0:
        print('Count is' + str(count))

        start = df_list[0].index[0]
        end = start - datetime.timedelta(90)

        start = start.strftime('%s')
        start = int(start) - 3600  # Temporary solution to a timezone issue likely realted to EDT/EST change
        start = str(start)
        end = end.strftime('%s')

        url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart/range?vs_currency=usd&from={end}&to={start}"

        try:
            # API call, max 90 days for hourly prices. More than that its daily. API limitation
            response = requests.get(url)
            data = response.json()

            # Prepare the hourly price data
            new_df = pd.DataFrame(data['prices'], columns=['dates', 'prices'])
            new_df['dates'] = pd.to_datetime(new_df['dates'], unit='ms')
            new_df = new_df.set_index('dates')

        except Exception as e:

            print("There was a problem during the CoinGEcko Historic API call.")
            print(f" The cause was : {e}")

            if int(response.status_code) == 429:
                print(f"CoinGecko Response: {response.status_code}")
                #print(f"{response.headers}")
                print(f"Waiting {response.headers['Retry-After']} Seconds")

                time.sleep(int(response.headers['Retry-After']))

            else:
                print(f"CoinGecko Response: {response.status_code}")
                print(f"Trying Again in 30 Seconds....")

                time.sleep(30)

            response = requests.get(url)
            data = response.json()

            # Prepare the hourly price data
            new_df = pd.DataFrame(data['prices'], columns=['dates', 'prices'])
            new_df['dates'] = pd.to_datetime(new_df['dates'], unit='ms')
            new_df = new_df.set_index('dates')

        # Prepare hourly volume data
        volumes_df = pd.DataFrame(data['total_volumes'], columns=['dates', 'volumes'])
        volumes_df['dates'] = pd.to_datetime(volumes_df['dates'], unit='ms')
        volumes_df = volumes_df.set_index('dates')

        # Prepare hourly market cap data
        cap_df = pd.DataFrame(data['market_caps'], columns=['dates', 'mcaps'])
        cap_df['dates'] = pd.to_datetime(cap_df['dates'], unit='ms')
        cap_df = cap_df.set_index('dates')

        # Calculate the Open High Low Close Volume(OHLCV) values
        min_df = new_df.groupby([new_df.index.date]).min()  # Get the lows for each day
        max_df = new_df.groupby([new_df.index.date]).max()  # Get the highs for each day
        open_df = new_df.groupby([new_df.index.date]).first()  # Get the first value of each day for Open
        close_df = new_df.groupby([new_df.index.date]).last()  # Get the last value of each day for Close
        volume_df = volumes_df.groupby([volumes_df.index.date]).mean()  # Get the mean volume for each day
        mcaps_df = cap_df.groupby([cap_df.index.date]).mean()  # Get the mean mcaps for each day

        # Concatenate it all into a single dataframe for 90 days worth of OHLCV
        try:
            next_ohlc_df = pd.concat(
                [open_df['prices'], max_df['prices'], min_df['prices'], close_df['prices'], volume_df['volumes'],
                 mcaps_df['mcaps']], axis=1, keys=['open', 'high', 'low', 'close', 'volume', 'Market Cap'])

            next_ohlc_df = next_ohlc_df.shift(-1, axis=0)
            next_ohlc_df = next_ohlc_df.dropna()

            df_list.insert(0, next_ohlc_df)

        except Exception as e:
            print("Something went wrong during coingecko historic data gathering for:")
            print(f"{coin} ({symbol})")
            print(f"The reason is {e}")
            print(f"It occurred during tranch {count} of the gathering process...")

        count -= 1
        print('Pausing for 5 seconds, not to exceed API call limit')

        # Wait to not overload the API
        time.sleep(5)

    test_joiner = pd.concat(df_list)
    test_joiner = test_joiner.drop(['Market Cap'], axis=1)

    return test_joiner


def on_chain_txnvol(coin, symbol, from_date, at_date):
    '''
    :param coin: String, The selected cryptocoin
    :param start_date: String, the most recent date
    :param end_date: String, The furthest back date
    :return: DataFrame with [open,high,low,close,volume] columns
    '''

    print(f"Calling Messari API for daily on-chain txn volume for {coin}({symbol}).....")

    url = f"https://data.messari.io/api/v1/assets/{coin}/metrics/txn.vol/time-series?start={from_date}&end={at_date}&interval=1d&timestamp-format=rfc3339"
    alt_url = f"https://data.messari.io/api/v1/assets/{symbol}/metrics/txn.vol/time-series?start={from_date}&end={at_date}&interval=1d&timestamp-format=rfc3339"

    count = 3

    while count > 0:
        response = requests.get(url)

        if int(response.status_code) == 200:
            print(f"Messari Response Code: {response.status_code}")
            print(f"Messari found {coin} by name Match!")
            data = response.json()
            df = pd.DataFrame(data['data']['values'], columns=['dates', 'txn_vol'])

            break

        # Unlike with CoinGecko, a 404 from Messari is not necessarily the end. Try the ticker of the coin instead
        elif int(response.status_code) == 404:
            print(f"Messari Response Code: {response.status_code}")
            print("Trying for a ticker symbol match....")
            response = requests.get(alt_url)

            data = response.json()

            try:
                df = pd.DataFrame(data['data']['values'], columns=['dates', 'txn_vol'])
                print(f"Messari found {coin} by Ticker Symbol match!")

                break

            except Exception as e:
                print(f"Couldn't FIND on-chain txn volume data for {coin} {symbol} from Messari API")
                print(f"Reason: {e}")

                break

        elif int(response.status_code) == 429:
            print(f"Messari API Response: {response.status_code}")
            print(f"Waiting {response.headers['retry-after']} Seconds")

            # Sometimes Messari will return a retry after of seconds in the tens of thousands
            # If this is the case there is no point in trying again. Break the loop
            if int(response.headers['retry-after']) > 400:
                print("Messari API no longer accepting requests for TXN Volume data today...")
                break
            else:
                time.sleep(int(response.headers['retry-after']))

        else:
            count -= 1
            print(f"Messari API Response: {response.status_code}")
            #print(f"Messari API Response: {response.headers}")
            print(f"Trying Again in 30 Seconds....")
            print(f"Will try {count} more times...")
            time.sleep(30)


    # Catch any other problems
    try:
        # In rare cases this code throws a key error but it doesn't crash the app. Monitor in case it gets worse
        df['dates'] = pd.to_datetime(df['dates'], format='%Y-%m-%d')
        df['dates'] = pd.to_datetime(df['dates']).dt.date
        df.index = df['dates']
        df.drop(columns=['dates'], inplace=True)
        df.index = pd.to_datetime(df.index)

        return df['txn_vol']


    # Print the error to the console to debug later or just to know what happened
    except Exception as e:
        print(f"Couldn't get Messari on-chain txn volume data for {coin} {symbol}")
        print(f"Problem was: {e} ")

        # So we know if it kept trying and found nothing or if there was another reason
        if count == 0:
            print(f"The Retry attempts were exhausted...")

        return None


def fill_missing_dates_with_average(df, window=30):
    # Reindex the DataFrame with the full date range
    date_range = pd.date_range(start=df.index.min(), end=df.index.max())
    df = df.reindex(date_range)

    # Fill missing values in each column with the rolling mean of the past 'window' days
    for column in df.columns:
        df[column] = df[column].fillna(df[column].rolling(window=window, min_periods=1).mean())

    return df

