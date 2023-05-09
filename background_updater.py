import datetime
import time
import os
import json

import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler

from dataset_maker import revise_datasets, fiat_exchange_rates, get_fiat_names, top_hundred_coins, coingecko_minute_data, \
    messari_historic, coingecko_historic, on_chain_txnvol


# Declare the scheduler
sched = BackgroundScheduler()

# Number of coins to get
cl = 50

now = datetime.datetime.utcnow()  # current UTC date and time
today = datetime.datetime.combine(now, datetime.datetime.min.time())  # Midnight this morning UTC

# Date range corresponding to Messari free API limitations
# NOTE: Only daily & weekly data are available for free. Most recent possible date is "yesterday"
to_date = today  # This is effectively "yesterday" UTC
from_date = today - datetime.timedelta(hours=48384)  # max allowed by Messari

# Epoch timestamps for CoinGecko
to_minute = now.strftime('%s')
from_minute = today.strftime('%s')

# Location of datasets for the app
existing_ohlcv_datasets = os.listdir('datasets')

ohlcv_data_dir = 'datasets/'
ohlcv_data_path = os.path.join(ohlcv_data_dir)

# File paths, directory checks, timestamps
txn_data_dir = 'txn_vol/'
txn_data_path = os.path.join(txn_data_dir)



# Schedule and run updates for top 50 cryptocoins, dictionary of currently tracked coins, and fiat exchange rates
@sched.scheduled_job('interval', hours=8, next_run_time=datetime.datetime.now())

def timed_job_two():

    # Function calls
    # Update the current list of the top coins and revise the existing one from coingecko
    try:
        # Get the filtered list of cryptocoins from coin gecko API, based on filters seen within the function above
        cryptocoins = top_hundred_coins(cl)

        # Check and combine to new and old dictionaries into a final dictionary of current coins
        cryptocoins = revise_datasets(cryptocoins, existing_ohlcv_datasets, cl)

        # Save the new dictionary of cryptocoins
        with open("coinnames/cryptocoins.json", "w") as outfile:
            json.dump(cryptocoins, outfile)

    # If the API call fails use the existing old dictionary
    except Exception as e:
        print("Failed to update coin list from coin gecko")
        print(f"The reason was {e}")
        print("Using old existing list of Top Coins")

        existing_topcoins = open("coinnames/cryptocoins.json", "r")
        cryptocoins = json.loads(existing_topcoins.read())

    # Update the current list of Fiat currency exchange rates
    # Get fiat currency exchange rates

    try:
        exchange_rates = fiat_exchange_rates()

        # Save the exchange rates
        with open("fiat_exch_rates/exchrates.json", "w") as outfile:
            json.dump(exchange_rates, outfile)

    # If API call fails use old existing data
    except Exception as e:
        print("There was a problem getting fiat exchange rates")
        print(f"The reason was {e}")
        print("Using old exchange rates...")

        existing_exchange = open("fiat_exch_rates/exchrates.json", "r")
        exchange_rates = json.loads(existing_exchange.read())

    #  Get the names of the fiat currencies for the drop-down menu in the "custom plots drop-down menu"
    try:
        fiat_names = get_fiat_names()

        # Save the names of fiat currencies as a dictionary in json format
        fiat_names.to_json('fiat_exch_rates/fiat.json', orient='index')

    # Use existing list of names
    except Exception as e:
        print("There was a problem getting the names of fiat currencies...")
        print(f"The reason was {e}")
        print("Using existing names list...")

        existing_fiat_names = open("fiat_exch_rates/fiat.json", "r")
        fiat_names = json.loads(existing_fiat_names.read())

    print('Finished updating coin lists and fiat. Update will run again in 8 Hours.')


# Schedule and run updates for OHLCV and TXN Volume data
@sched.scheduled_job('interval', hours=1, next_run_time=datetime.datetime.now())
def timed_job():

    # Read cryptocoins for which to get OHLCV and TXN VOL data
    with open("coinnames/cryptocoins.json", "r") as read_file:
        cryptocoins = json.load(read_file)


    # FUNCTION CALLS FOR OHLCV DATA

    # Get data for each coin in the dictionary created above
    for symbol, coin in cryptocoins.items():

        # Messari is used first because it provides data with only one API call per coin
        # If the data is missing or incomplete, CoinGecko is called instead.
        # The Coingecko API requires multiple API calls per coin in order to get the same level of data.
        # For running ohlc data for the current UTC day, CoinGecko is always used

        print(f"Getting data for {coin}({symbol})")

        # RUN PARTIAL UPDATE

        # Check if there is existing data and how old it is
        if os.path.exists(f"{os.path.join(ohlcv_data_dir)}{coin}({symbol}).csv"):
            current_update = pd.read_csv(f"{ohlcv_data_path}{coin}({symbol}).csv", index_col=0)
            last_update = current_update.index[-1]

            # If the last update was today, only update today. Eliminates unnecessary API calls and adds much more speed
            current_period = pd.date_range(
                start=today, end=now)

            if last_update in current_period:

                print(f"Only updating data for today from coinGecko for {coin} {symbol}")
                # Minute data
                try:
                    minute_data = coingecko_minute_data(coin, from_minute, to_minute, symbol)

                except Exception as e:
                    print("Something went wrong")
                    print(f"The reason is: {e}")

                # If this dataframe is empty then the API is giving us empty data.
                # In this case break the loop and try again later
                if minute_data.empty:
                    print('DataFrame is empty!')

                    break

                # combine with existing
                ohlcv_data = pd.concat([current_update, minute_data], axis=0, sort=True)

                ohlcv_data.index = pd.to_datetime(ohlcv_data.index)
                ohlcv_data['dates'] = ohlcv_data.index
                ohlcv_data['dates'] = pd.to_datetime(ohlcv_data['dates'])
                ohlcv_data.drop_duplicates(subset='dates', keep='last', inplace=True)

                ohlcv_data = ohlcv_data.set_index('dates')
                ohlcv_data = ohlcv_data[['open', 'high', 'low', 'close', 'volume']]

            # RUN FULL UPDATE IF IT IS NOT WITHIN TODAY
            else:

                # Minute data
                try:
                    minute_data = coingecko_minute_data(coin, from_minute, to_minute, symbol)

                except Exception as e:
                    print("Something went wrong")
                    print(f"The reason is: {e}")

                # If this dataframe is empty then the API is giving us empty data.
                # In this case break the loop and try again later
                if minute_data.empty:
                    print('DataFrame is empty!')

                    break

                # Daily data from Messari
                try:
                    daily_data = messari_historic(coin, symbol, from_date, to_date)

                except Exception as e:
                    print("Something went wrong")
                    print(f"The reason is: {e}")

                # Check to see the structure of the dataset is what is expected
                try:
                    consistency_check = pd.date_range(
                        start=daily_data.index[-1] - datetime.timedelta(days=60), end=daily_data.index[-1]).difference(
                        daily_data.index).shape[0]

                    # If Messari has incomplete or fragmented data (e.g. for Leo) then try to get the data from coingecko
                    if daily_data.shape[0] <= 60 or consistency_check > 0:
                        print(f"Not saving {coin} {symbol}. Incomplete data")
                        print(daily_data.shape)
                        print("Trying from CoinGecko...")

                        # Daily data from CoinGecko
                        daily_data = coingecko_historic(minute_data, 8, coin, symbol)

                        ohlcv_data = pd.concat([daily_data, minute_data], axis=0, sort=True)

                        ohlcv_data.index = pd.to_datetime(ohlcv_data.index)
                        ohlcv_data['dates'] = ohlcv_data.index
                        ohlcv_data['dates'] = pd.to_datetime(ohlcv_data['dates'])
                        ohlcv_data.drop_duplicates(subset='dates', keep='last', inplace=True)

                        ohlcv_data = ohlcv_data.set_index('dates')
                        ohlcv_data = ohlcv_data[['open', 'high', 'low', 'close', 'volume']]


                    else:
                        ohlcv_data = pd.concat([daily_data, minute_data], axis=0, sort=True)

                        ohlcv_data.index = pd.to_datetime(ohlcv_data.index)
                        ohlcv_data['dates'] = ohlcv_data.index
                        ohlcv_data['dates'] = pd.to_datetime(ohlcv_data['dates'])
                        ohlcv_data.drop_duplicates(subset='dates', keep='last', inplace=True)

                        ohlcv_data = ohlcv_data.set_index('dates')
                        ohlcv_data = ohlcv_data[['open', 'high', 'low', 'close', 'volume']]


                # If consistency check fails or anything else goes wrong, try from CoinGeckoAPI
                except Exception as e:
                    print(f"Consistency Check Failed for Messari data for {coin} {symbol}")
                    print(f"Reason is {e}")
                    print(f"Trying from CoinGecko for {coin} {symbol}")

                    # Daily data from CoinGEcko
                    daily_data = coingecko_historic(minute_data, 8, coin, symbol)

                    ohlcv_data = pd.concat([daily_data, minute_data], axis=0, sort=True)

                    ohlcv_data.index = pd.to_datetime(ohlcv_data.index)
                    ohlcv_data['dates'] = ohlcv_data.index
                    ohlcv_data['dates'] = pd.to_datetime(ohlcv_data['dates'])
                    ohlcv_data.drop_duplicates(subset='dates', keep='last', inplace=True)

                    ohlcv_data = ohlcv_data.set_index('dates')
                    ohlcv_data = ohlcv_data[['open', 'high', 'low', 'close', 'volume']]

                # Daily data if there is a current dataset
                if os.path.exists(f"{os.path.join(ohlcv_data_dir)}{coin}({symbol}).csv"):

                    extant_ohlcv = pd.read_csv(f"{ohlcv_data_path}{coin}({symbol}).csv", index_col=0)

                    ohlcv_data = pd.concat([extant_ohlcv, ohlcv_data], axis=0, sort=True)
                    ohlcv_data.index = pd.to_datetime(ohlcv_data.index)
                    ohlcv_data['dates'] = ohlcv_data.index
                    ohlcv_data['dates'] = pd.to_datetime(ohlcv_data['dates'])
                    ohlcv_data.drop_duplicates(subset='dates', keep='last', inplace=True)
                    ohlcv_data = ohlcv_data.set_index('dates')
                    ohlcv_data = ohlcv_data[['open', 'high', 'low', 'close', 'volume']]
                    print(f"THERE WAS EXISTING DATA FOR {coin} {symbol}")

                else:
                    print(f"THERE WAS NOT EXISTING DATA FOR {coin}{symbol}")

                ohlcv_data = ohlcv_data.drop_duplicates(keep='last')
                ohlcv_data = ohlcv_data.sort_index(axis=0)

                # CALL FOR TXN VOL
                print(f"Checking Messari for TXN data for {coin} {symbol}")

                try:
                    chain_txn_data = on_chain_txnvol(coin, symbol, from_date, to_date)

                    # Save the data
                    try:
                        chain_txn_data.to_csv(f'{txn_data_dir}/{coin}({symbol}).csv')

                    except Exception as e:
                        print(f"No TXN to save for {coin} {symbol}")
                        print(f"The reason is {e}")


                except Exception as e:
                    print(f"No TXN to save for {coin} {symbol}")
                    print(f"The reason is {e}")

        # RUN FULL UPDATE IF THERE IS NO EXISTING DATA
        else:

            # Minute data
            try:
                minute_data = coingecko_minute_data(coin, from_minute, to_minute, symbol)

            except Exception as e:
                print("Something went wrong")
                print(f"The reason is: {e}")

            # If this dataframe is empty then the API is giving us empty data.
            # In this case break the loop and try again later
            if minute_data.empty:
                print('DataFrame is empty!')

                break

            # Daily data from Messari
            try:
                daily_data = messari_historic(coin, symbol, from_date, to_date)

            except Exception as e:
                print("Something went wrong")
                print(f"The reason is: {e}")

            # Check to see the structure of the dataset is what is expected
            try:
                consistency_check = pd.date_range(
                    start=daily_data.index[-1] - datetime.timedelta(days=60), end=daily_data.index[-1]).difference(
                    daily_data.index).shape[0]

                # If Messari has incomplete or fragmented data (e.g. for Leo) then try to get the data from coingecko
                if daily_data.shape[0] <= 60 or consistency_check > 0:
                    print(f"Not saving {coin} {symbol}. Incomplete data")
                    print(daily_data.shape)
                    print("Trying from CoinGecko...")

                    # Daily data from CoinGecko
                    daily_data = coingecko_historic(minute_data, 8, coin, symbol)

                    ohlcv_data = pd.concat([daily_data, minute_data], axis=0, sort=True)

                    ohlcv_data.index = pd.to_datetime(ohlcv_data.index)
                    ohlcv_data['dates'] = ohlcv_data.index
                    ohlcv_data['dates'] = pd.to_datetime(ohlcv_data['dates'])
                    ohlcv_data.drop_duplicates(subset='dates', keep='last', inplace=True)

                    ohlcv_data = ohlcv_data.set_index('dates')
                    ohlcv_data = ohlcv_data[['open', 'high', 'low', 'close', 'volume']]


                else:
                    ohlcv_data = pd.concat([daily_data, minute_data], axis=0, sort=True)

                    ohlcv_data.index = pd.to_datetime(ohlcv_data.index)
                    ohlcv_data['dates'] = ohlcv_data.index
                    ohlcv_data['dates'] = pd.to_datetime(ohlcv_data['dates'])
                    ohlcv_data.drop_duplicates(subset='dates', keep='last', inplace=True)

                    ohlcv_data = ohlcv_data.set_index('dates')
                    ohlcv_data = ohlcv_data[['open', 'high', 'low', 'close', 'volume']]


            # If consistency check fails or anything else goes wrong, try from CoinGeckoAPI
            except Exception as e:
                print(f"Consistency Check Failed for Messari data for {coin} {symbol}")
                print(f"Reason is {e}")
                print(f"Trying from CoinGecko for {coin} {symbol}")

                # Daily data from CoinGEcko
                daily_data = coingecko_historic(minute_data, 8, coin, symbol)

                ohlcv_data = pd.concat([daily_data, minute_data], axis=0, sort=True)

                ohlcv_data.index = pd.to_datetime(ohlcv_data.index)
                ohlcv_data['dates'] = ohlcv_data.index
                ohlcv_data['dates'] = pd.to_datetime(ohlcv_data['dates'])
                ohlcv_data.drop_duplicates(subset='dates', keep='last', inplace=True)

                ohlcv_data = ohlcv_data.set_index('dates')
                ohlcv_data = ohlcv_data[['open', 'high', 'low', 'close', 'volume']]

            # Daily data if there is a current dataset
            if os.path.exists(f"{os.path.join(ohlcv_data_dir)}{coin}({symbol}).csv"):

                extant_ohlcv = pd.read_csv(f"{ohlcv_data_path}{coin}({symbol}).csv", index_col=0)

                ohlcv_data = pd.concat([extant_ohlcv, ohlcv_data], axis=0, sort=True)
                ohlcv_data.index = pd.to_datetime(ohlcv_data.index)
                ohlcv_data['dates'] = ohlcv_data.index
                ohlcv_data['dates'] = pd.to_datetime(ohlcv_data['dates'])
                ohlcv_data.drop_duplicates(subset='dates', keep='last', inplace=True)
                ohlcv_data = ohlcv_data.set_index('dates')
                ohlcv_data = ohlcv_data[['open', 'high', 'low', 'close', 'volume']]

                print(f"THERE WAS EXISTING DATA FOR {coin} {symbol}")

            else:
                print(f"THERE WAS NOT EXISTING DATA FOR {coin}{symbol}")

            ohlcv_data = ohlcv_data.drop_duplicates(keep='last')
            ohlcv_data = ohlcv_data.sort_index(axis=0)

            # CALL FOR TXN VOL
            print(f"Checking Messari for TXN data for {coin} {symbol}")

            try:
                chain_txn_data = on_chain_txnvol(coin, symbol, from_date, to_date)

                # Save the data
                try:
                    chain_txn_data.to_csv(f'{txn_data_dir}/{coin}({symbol}).csv')

                except Exception as e:
                    print(f"No TXN to save for {coin} {symbol}")
                    print(f"The reason is {e}")


            except Exception as e:
                print(f"No TXN to save for {coin} {symbol}")
                print(f"The reason is {e}")

        # Sometimes you get one date and then nothing for months.
        # Consistency is improved dramatically by dropping that one date
        ohlcv_data = ohlcv_data.drop(ohlcv_data.index[0])

        # This code is in try except because sometimes the APIs return empty dataframes late at night
        # While the application is in mid-update.
        try:

            # Perform one last check of the dataset for any gaps
            last_test = pd.date_range(start=ohlcv_data.index[0], end=ohlcv_data.index[-1]).difference(ohlcv_data.index)

            # if less than 10 dates are missing, fill them with the mean values for that dataset
            if len(last_test) >= 1 and len(last_test) <= 14:

                for col in ohlcv_data.columns:
                    ohlcv_data[col].fillna(ohlcv_data[col].mean(), inplace=True)

                # Save OHLCV
                ohlcv_data.to_csv(f'datasets/{coin}({symbol}).csv')

            # If more than 10 you can't use the dataset because it will have too many mean values
            elif len(last_test) > 14:
                print(f"Dataset for {coin}({symbol}) failed final check. Not saving....")


            else:
                # Save OHLCV
                ohlcv_data.to_csv(f'datasets/{coin}({symbol}).csv')

        except Exception as e:
            print("An except occurred when trying to test the data.")
            print(f"The reason was {e}")
            print("Probably the time changed and one of the API started returning empty dataframes")
            print("While the application was mid-update....")


        # Pause the for loop iterations to not spam the APIs
        time.sleep(3)

    print('Finished updating datasets. Update will run again in 15 Minutes.')


# Invoke the schedulers
sched.start()