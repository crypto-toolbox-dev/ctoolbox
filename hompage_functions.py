import base64
from functools import reduce
from datetime import timedelta, datetime
from io import BytesIO
from matplotlib.figure import Figure
import matplotlib.ticker as mticker
import pandas as pd
import numpy as np
import time
import requests
import random


def top_ten(limit=15):
    try:
        response = requests.get(
            f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false")

        print(f"CoinGecko API call for Top {limit} CryptoCoins by Market Capitalization")
        print(f"CoinGecko Response Code: {response.status_code}")

        data = response.json()

    except ConnectionError:
        print("CoinGecko API refused connection. Retrying in 30 seconds...")
        time.sleep(30)
        response = requests.get(
            f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false")

        print(f"CoinGecko API call for Top {limit} CryptoCoins by Market Capitalization")
        print(f"CoinGecko Response Code: {response.status_code}")

        data = response.json()

    stablecoins = ['usdt', 'busd', "ust", 'mim', 'frax', 'tusd', 'usdc', 'dai', 'usdp', 'usdc', 'usdd', 'usdn']
    wrappercoins = ['wbtc', 'hbtc', 'steth', 'cdai']
    data = [d for d in data if d['symbol'] not in stablecoins]
    data = [d for d in data if d['symbol'] not in wrappercoins]
    data = data[:limit]

    return data


def mcap_pie_data():

    # Request Global Market Cap data
    try:
        response = requests.get(
            f"https://api.coingecko.com/api/v3/global")

        print(f"CoinGecko Response Code: {response.status_code}")

        data = response.json()

    except ConnectionError:
        print("CoinGecko API refused connection. Retrying in 30 seconds...")
        time.sleep(30)
        response = requests.get(
            f"https://api.coingecko.com/api/v3/global")

        print(f"CoinGecko Response Code: {response.status_code}")

        data = response.json()

    # Wrangle Market Cap data
    tcap = data["data"]["total_market_cap"]["usd"]
    fifteen_cap = top_ten(limit=15)
    fifteen_cap_name = [cap['id'] for cap in fifteen_cap]

    fifteen_cap = [cap['market_cap'] for cap in fifteen_cap]  # Market cap per coin in the top 15
    fifteen_sum = sum(fifteen_cap)  # Total Mcap of top 15
    other_cap = tcap - fifteen_sum  # Total Mcap of all other coins listed
    fifteen_cap_name.append("All others")
    fifteen_cap.append(other_cap)

    # Data for the Pie Chart
    mcap_pie = {fifteen_cap_name[i]: fifteen_cap[i] for i in range(len(fifteen_cap_name))}

    return mcap_pie

# From alternative.me for the Fear and Greed Index
def fearandgreed():
    '''
    Grab the Crypto Fear and Greed Index data
    Source: https://alternative.me/crypto/fear-and-greed-index/
    :return: Fear and Greed Index values
    '''

    # API call to alternative.me
    try:
        fngresponse = requests.get("https://api.alternative.me/fng/?limit=0")
        data = fngresponse.json()

    except Exception:
        print("Error getting Fear and Greed Index")
        print("Trying again in 10 seconds")
        time.sleep(30)
        fngresponse = requests.get("https://api.alternative.me/fng/?limit=0")
        data = fngresponse.json()

    # Isolate the time till next update for plotting later
    del data['data'][0]['time_until_update']

    # Wrangle the data a bit to combine it with the rest later
    fngdata = pd.DataFrame(data['data'])
    fngdata['dates'] = pd.to_datetime(fngdata['timestamp'], unit='s')
    fngdata = fngdata.set_index('dates')
    fngdata.drop(columns=['timestamp'], inplace=True)
    fngdata.rename(columns={ 'value':'fng_v','value_classification':'fng_c'}, inplace=True)

    return fngdata

# Long dimensions are figsize=(20,5)
# default dimensions are figsize=(6.4, 4.8)
def fng_line(x,y, title, dims=(6.4, 4.8)):
    # Generate the figure **without using pyplot**.
    fig = Figure(figsize=dims)
    ax = fig.subplots()
    ax.plot(x, y,color='darkblue')
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_locator(mticker.MaxNLocator(10))
    ax.grid(False)
    ax.set_yticks([0,25,45,55,75,100],['Extreme Fear','Fear','Neutral', 'Neutral','Greed','Extreme Greed'])

    ax.fill_between(x, y, 0,
                     where=(y >= 75), facecolor='lime', edgecolor='lime',
                     alpha=1)

    ax.fill_between(x, y, 0,
                    where=(y >= 55), facecolor='green', edgecolor='green',
                    alpha=0.5)

    ax.fill_between(x, y, 0,
                    where=(y <= 45), facecolor='orange', edgecolor='orange',
                    alpha=0.8)

    ax.fill_between(x, y, 0,
                    where=(y <= 25), facecolor='red', edgecolor='red',
                    alpha=1)

    ax.fill_between(x, y, 0,
                    where=(y >= 45), facecolor='yellow', edgecolor='yellow',
                    alpha=0.5)

    # Rotate xaxis labels
    for label in ax.xaxis.get_ticklabels():
        label.set_rotation(45)
        label.set_horizontalalignment('right')

    ax.tick_params(axis='both', labelsize=15)
    fig.suptitle(f"{title}", fontsize='medium')
    fig.tight_layout()

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")

    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")

    # Clear the current axes.
    ax.cla()
    # Clear the current figure.
    fig.clf()

    fig.clear()

    del fig

    return data

def plot_line(x,y, title, dims=(6.4, 4.8)):
    # Generate the figure **without using pyplot**.
    fig = Figure(figsize=dims)
    ax = fig.subplots()
    ax.plot(x, y,color='darkblue')
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_locator(mticker.MaxNLocator(10))
    ax.grid(False)


    # Rotate xaxis labels
    for label in ax.xaxis.get_ticklabels():
        label.set_rotation(45)
        label.set_horizontalalignment('right')

    fig.suptitle(f"{title}", fontsize='medium')
    fig.tight_layout()

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")

    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")

    # Clear the current axes.
    ax.cla()
    # Clear the current figure.
    fig.clf()

    fig.clear()

    del fig

    return data

def spread(coins):

    spreads = []

    for c in coins:

        dt_string = c['last_updated'].split("T")[0]
        format = "%Y-%m-%d"
        dt_object = datetime.strptime(dt_string, format)

        seven = dt_object - timedelta(days=7)
        thirty = dt_object - timedelta(days=30)
        ninety = dt_object - timedelta(days=90)

        cs = {}

        try:
            df = pd.read_csv(f'datasets/{c["id"].lower()}({c["symbol"].lower()}).csv', index_col=0)
            df.index = pd.to_datetime(df.index)

            cs['id'] = c['id']

            # Highs
            cs['7d High'] = df['high'][-7:].max()
            cs['30d High'] = df['high'][-30:].max()
            cs['90d High'] = df['high'][-90:].max()

            # Lows
            cs['7d Low'] = df['low'][-7:].min()
            cs['30d Low'] = df['low'][-30:].min()
            cs['90d Low'] = df['low'][-90:].min()

            # Changes
            try:
                cs['7d change'] = float(((float(c['current_price']) - df.loc[seven]['close']) * 100 / float(c['current_price'])))
                cs['30d change'] = float(((float(c['current_price']) - df.loc[thirty]['close']) * 100 / float(c['current_price'])))
                cs['90d change'] = float(((float(c['current_price']) - df.loc[ninety]['close']) * 100 / float(c['current_price'])))

            except KeyError:
                print(f"Insufficient or corrupt dataset for {c['id']}")
                print(f"Not displaying price change percentage for {c['id']}")
                cs['7d change'] = " "
                cs['30d change'] = " "
                cs['90d change'] = " "

        except FileNotFoundError:
            print(f"No Data for {c['id']}({c['symbol']})")


        spreads.append(cs)

    return spreads



def returns(coins, period=1):

    returns = []

    for c in coins:

        try:
            df = pd.read_csv(f'datasets/{c["id"].lower()}({c["symbol"].lower()}).csv', index_col=0)
            df.index = pd.to_datetime(df.index)


        except FileNotFoundError:
            print(f"No Data for {c['id']}({c['symbol']})")

        return_pct_change = df.close.pct_change(period)
        return_pct_change.fillna(0, inplace=True)
        return_pct_change = return_pct_change.to_frame(c['symbol'])

        returns.append(return_pct_change)

    return returns


def cumulative_returns(coins):

    cumprod_returns = []

    for c in coins:

        try:
            df = pd.read_csv(f'datasets/{c["id"].lower()}({c["symbol"].lower()}).csv', index_col=0)
            df.index = pd.to_datetime(df.index)

        except FileNotFoundError:
            print(f"No Data for {c['id']}({c['symbol']})")

        return_pct_change = df.close.pct_change()
        return_pct_change.fillna(0, inplace=True)

        cumprod_daily_pct_change = (1 + return_pct_change).cumprod()
        cumprod_daily_pct_change = cumprod_daily_pct_change.to_frame(c['symbol'])
        cumprod_returns.append(cumprod_daily_pct_change)

    return cumprod_returns


def plot_multiline(dflist, figname, dims=(6.4, 4.8)):
    # Generate the figure **without using pyplot**.
    fig = Figure(figsize=dims)
    ax = fig.subplots()

    # Get values for each dataset
    for df in dflist:
        df = df[-720:]

        ax.plot(df, label=df.columns[0].upper())

    ax.yaxis.set_major_locator(mticker.MaxNLocator(10))
    ax.grid(False)
    ax.legend(loc='upper right', ncol=5)

    # Rotate xaxis labels
    for label in ax.xaxis.get_ticklabels():
        label.set_rotation(45)
        label.set_horizontalalignment('right')

    fig.suptitle(f"{figname}", fontsize='medium')
    fig.tight_layout()

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")

    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")

    # Clear the current axes.
    ax.cla()
    # Clear the current figure.
    fig.clf()

    fig.clear()

    del fig

    return data

def hbars(dflist, figname):
    # Generate the figure **without using pyplot**.
    fig = Figure()
    ax = fig.subplots()

    data = {}

    # Get Annual values for Bars
    for df in dflist:
        yr_test = df.resample('1Y').mean()
        data[yr_test.columns[0]] = yr_test[yr_test.columns[0]][-1]

    ax.barh([k.upper() for k in data.keys()], [v for v in data.values()])
    ax.grid(False)
    ax.legend(loc='upper right', ncol=5)

    # Rotate xaxis labels
    for label in ax.xaxis.get_ticklabels():
        label.set_rotation(45)
        label.set_horizontalalignment('right')

    fig.suptitle(f"{figname}", fontsize='medium')
    fig.tight_layout()

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")

    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")

    # Clear the current axes.
    ax.cla()
    # Clear the current figure.
    fig.clf()

    fig.clear()

    del fig

    return data


def multi_bars(dflist, figname, slimit, elimit):

    # Generate the figure **without using pyplot**.
    fig = Figure(figsize=(6.4, 4.8))
    ax = fig.subplots()

    # Get Annual values for Bars
    dflist = [df.resample('1Y').mean() for df in dflist]
    width = 20

    # This because the plotter rounds the xaxis dates up to the nearest year, misrepresenting the data.
    space = 0
    colors = ['red', 'lime', 'blue', 'violet', 'yellow', 'aqua', 'pink', 'saddlebrown', 'grey', 'tomato', 'magenta',
              'darkslategrey', 'indigo', 'orange', 'yellowgreen', 'darkblue', 'rosybrown',
              'rebeccapurple', 'seagreen','mediumvioletred', 'lightpink']

    mdf = reduce(lambda df1,df2: pd.merge(df1, df2, how='left', on='dates'), dflist)
    mdf.fillna(0, inplace=True)
    mdf = mdf.iloc[slimit:elimit, :]

    for col, c in zip(mdf.columns, colors):
        space += 20

        x = [(t - timedelta(days=360 + space)) for t in mdf.index]
        ax.bar(x, mdf[col], edgecolor='grey', color=c, label=col.upper(), width=width)

    ax.set_xticks([r - timedelta(days=360 + width) for r in mdf.index], [d.strftime("%Y") for d in mdf.index])
    ax.grid(False)
    ax.legend(ncol=5, fontsize='small')

    # Rotate xaxis labels
    for label in ax.xaxis.get_ticklabels():
        label.set_rotation(45)
        label.set_horizontalalignment('right')

    fig.suptitle(f"{figname}", fontsize='medium')
    fig.tight_layout()

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")

    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")

    # Clear the current axes.
    ax.cla()
    # Clear the current figure.
    fig.clf()

    fig.clear()

    del fig

    return data

def pie_chart(data, dims=(6.4, 4.8)):

    fig = Figure(figsize=dims)
    ax = fig.subplots()

    ax.pie(data.values())

    # Adding legend
    ax.legend([k.capitalize() for k in data.keys()],
              title="Coins",
              ncol=6,
              loc='upper center',
              fontsize="small",
              )

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")

    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")

    # Clear the current axes.
    ax.cla()
    # Clear the current figure.
    fig.clf()

    fig.clear()

    del fig

    return data


def pie_chart_broken(data, dims=(6.4, 4.8)):

    fig = Figure(figsize=dims)
    ax = fig.subplots()

    # Creating explode data
    explode = []
    n = len(data.keys())

    for i in range(n):
        explode.append(random.random())

    explode = [f / 2 for f in explode]

    # Creating color parameters
    colors = ['red', 'lime', 'blue', 'violet', 'yellow', 'aqua', 'pink', 'saddlebrown', 'grey', 'tomato', 'magenta',
              'darkslategrey', 'indigo', 'orange', 'yellowgreen', 'darkblue', 'rosybrown',
              'rebeccapurple', 'seagreen', 'mediumvioletred', 'lightpink']

    # Wedge properties
    wp = {'linewidth': 1, 'edgecolor': "green"}

    # Creating autocpt arguments
    def func(pct, allvalues):
        absolute = int(pct / 100. * np.sum(list(allvalues)))
        return "{:.1f}%".format(pct, absolute)

    # Creating plot
    # removed autopct because it doesn't fit neatly on the template but kept code in case better way is found later.
    wedges, texts, autotexts = ax.pie(data.values(),
                                      autopct=" ",
                                      explode=explode,
                                      labels=[f'{x.capitalize()} {np.round(y/sum(data.values())*100,1)}%' for x, y in data.items()],
                                      rotatelabels=True,
                                      shadow=True,
                                      colors=colors,
                                      startangle=90,
                                      wedgeprops=wp,
                                      textprops=dict(color="black"))

    # Set the font size for the text appearing in the pie wedges
    texts = [t.set_fontsize(9) for t in texts]

    # do the rotation of the labels
    for ea, eb in zip(wedges, autotexts):
        mang = (ea.theta1 + ea.theta2) / 2.  # get mean_angle of the wedge
        eb.set_rotation(mang + 270)  # rotate the label by (mean_angle + 270)
        eb.set_va("center")
        eb.set_ha("center")

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")

    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")

    # Clear the current axes.
    ax.cla()
    # Clear the current figure.
    fig.clf()

    fig.clear()

    del fig

    return data