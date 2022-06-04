import yfinance as yf
import pandas as pd
import numpy as np
import requests
import xlsxwriter
import math
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt


def get_stock_info(ticker):
    stock_data = yf.Ticker(ticker)
    return stock_data.info


def eq_weight_snp500():
    stocks = pd.read_csv('apps/stocks_info/static/sp_500_stocks.csv')
    return stocks['Ticker']


def finviz_parse_news():
    finviz_url = 'https://elite.finviz.com/quote.ashx?t='
    tickers = ['AAPL', 'AMD', 'TSLA']

    news_tables = {}
    for ticker in tickers:
        url = finviz_url + ticker

        req = Request(url=url, headers={'user-agent': 'my-app'})
        response = urlopen(req)
        html = BeautifulSoup(response, 'html')
        news_table = html.find(id='news-table')
        news_tables[ticker] = news_table

    # aapl_data = news_tables['AAPL']
    # aapl_rows = aapl_data.findAll('tr')
    #
    # titles = []
    # for index, row in enumerate(aapl_rows):
    #     title = row.a.text
    #     timestamp = row.td.text
    #     titles.append(timestamp + ' ' + title)

    parsed_data = []
    for ticker, news_table in news_tables.items():
        for row in news_table.findAll('tr'):
            title = row.a.text
            href = row.a.get('href')
            date_data = row.td.text.split(' ')
            if len(date_data) == 1:
                time = date_data[0]
            else:
                date = date_data[0]
                time = date_data[1]

            parsed_data.append([ticker, date, time, title, href])

    df = pd.DataFrame(parsed_data, columns=[
                      'ticker', 'date', 'time', 'title', 'href'])

    vader = SentimentIntensityAnalyzer()
    def f(title): return vader.polarity_scores(title)['compound']
    df['compound'] = df['title'].apply(f)
    df['date'] = pd.to_datetime(df.date).dt.date
    # mean_df = df.groupby(['ticker', 'date']).mean()

    return df.values.tolist()


def finviz_parse_news_form(ticker):
    finviz_url = 'https://elite.finviz.com/quote.ashx?t='
    ticker = ticker
    url = finviz_url + ticker

    req = Request(url=url, headers={'user-agent': 'my-app'})
    response = urlopen(req)
    html = BeautifulSoup(response, 'html')

    news_table = html.find(id='news-table')
    news_tables = {}
    news_tables[ticker] = news_table

    parsed_data = []
    for ticker, news_table in news_tables.items():
        for row in news_table.findAll('tr'):
            title = row.a.text
            href = row.a.get('href')
            date_data = row.td.text.split(' ')
            if len(date_data) == 1:
                time = date_data[0]
            else:
                date = date_data[0]
                time = date_data[1]

            parsed_data.append([ticker, date, time, title, href])

    df = pd.DataFrame(parsed_data, columns=[
                      'ticker', 'date', 'time', 'title', 'href'])

    vader = SentimentIntensityAnalyzer()
    def f(title): return vader.polarity_scores(title)['compound']
    df['compound'] = df['title'].apply(f)
    df['date'] = pd.to_datetime(df.date).dt.date

    return df.values.tolist()


def get_stock_fundamental_info(ticker):
    finviz_url = 'https://elite.finviz.com/quote.ashx?t='
    ticker = ticker
    url = finviz_url + ticker

    req = Request(url=url, headers={'user-agent': 'my-app'})
    response = urlopen(req)
    html = BeautifulSoup(response, 'html')
    info_table = html.find(class_='snapshot-table2')
    info_td = info_table.findAll('td')

    parsed_data = {}
    for index, row in enumerate(info_td):

        if info_td[index-1].text == 'Market Cap':
            market_cap = row.text
            parsed_data['Market Cap'] = market_cap

        if info_td[index-1].text == 'Shs Float':
            shares_float = row.text
            parsed_data['Shares Float'] = shares_float

        if info_td[index-1].text == 'Inst Own':
            inst_own = row.text
            parsed_data['Institutional Owners'] = inst_own

        if info_td[index-1].text == 'Short Float':
            short_float = row.text
            parsed_data['Short Float'] = short_float

    return parsed_data


def gaps(ticker, gap):
    std = pd.DataFrame(yf.Ticker(ticker).history(
        start='2010-01-02', actions=False)).reset_index()
    all_days = std['Date'].count().tolist()

    # get ticker info from yfinance
    shares_float = round(yf.Ticker(ticker).info['floatShares']/1000000, 2)
    market_cap = round(yf.Ticker(ticker).info['marketCap']/1000000000, 2)

    for x in std.index:
        if x >= 1:
            std.loc[x, ['Gap', 'Change']] = [(std.loc[x, 'Open'] - std.loc[x - 1, 'Close']) / std.loc[x - 1, 'Close'],
                                             (std.loc[x, 'Close'] - std.loc[x, 'Open']) / std.loc[x, 'Open']]

    if gap > 0:
        gap_up_f = (std['Gap'] > gap)
    elif gap < 0:
        gap_up_f = (std['Gap'] < gap)
    std = std.loc[gap_up_f]
    std = std.round(2)
    std['Date'] = std['Date'].dt.strftime('%Y-%m-%d')
    std['Gap'] = (std['Gap']*100).astype(int)
    std['Change'] = (std['Change'] * 100).astype(int)

    df_gaps = std.values.tolist()
    count_gaps = std['Gap'].count().tolist()
    green_change = std.loc[std['Change'] > 0]['Change'].count().tolist()
    red_change = std.loc[std['Change'] < 0]['Change'].count().tolist()

    green_percent = int(std.loc[std['Change'] > 0]
                        ['Change'].count()/std['Gap'].count()*100)
    red_percent = int(std.loc[std['Change'] < 0]
                      ['Change'].count()/std['Gap'].count() * 100)
    return df_gaps, count_gaps, green_change, red_change, all_days, shares_float, market_cap, green_percent, red_percent


def premarket_analize(ticker='aapl'):
    ticker = yf.Ticker(ticker)
    hist = ticker.history(prepost=True)
    return hist


def spy_back_test():
    # daily data
    stock_data_d = yf.Ticker('spy')
    stock_data_daily = pd.DataFrame(
        stock_data_d.history(period='60d', actions=False))
    stock_data_daily = stock_data_daily.reset_index()

    # intraday data
    stock_data_i = yf.Ticker('spy')
    stock_data_intraday = pd.DataFrame(stock_data_i.history(
        period='60d', interval='5m', actions=False))
    stock_data_intraday = stock_data_intraday.reset_index()

    # add prev day low to intraday dataframe
    for y in stock_data_intraday.index:
        for i in stock_data_daily.index:
            if i > 0:
                if stock_data_intraday.loc[y, 'Datetime'].date() == stock_data_daily.loc[i, 'Date'].date():
                    stock_data_intraday.loc[y,
                                            'Prev Day Low'] = stock_data_daily.loc[i-1, 'Low']

    sig = 0
    # take_profit = 0.0
    # stop_loss = 0.0
    # stock_data_intraday.loc['take'] = 0.0
    # stock_data_intraday.loc['stop'] = 0.0
    # stock_data_intraday['pnl'] = 0.0
    for y in stock_data_intraday.index:
        stock_data_intraday.loc[y, 'Signal'] = False
        if y == 0:
            stock_data_intraday.loc[y, 'Signal'] = False
        if y > 0 and stock_data_intraday.loc[y, 'Datetime'].date() == stock_data_intraday.loc[y-1, 'Datetime'].date():
            # if take_profit != 0.0 and take_profit <= stock_data_intraday.loc[y, 'High']:
            #     stock_data_intraday.loc[y, 'pnl'] = 1.0
            # elif take_profit != 0.0 and stop_loss >= stock_data_intraday.loc[y, 'Low']:
            #     stock_data_intraday.loc[y, 'pnl'] = -1.0
            if sig == 0 and stock_data_intraday.loc[y, 'Low'] <= stock_data_intraday.loc[y, 'Prev Day Low'] and stock_data_intraday.loc[y-1, 'Low'] > stock_data_intraday.loc[y, 'Prev Day Low'] and stock_data_intraday.loc[y, 'Signal'] == False:
                stock_data_intraday.loc[y, 'Signal'] = True
                sig = 1
                # take_profit = stock_data_intraday.loc[y, 'Prev Day Low'] + 1.0
                # stop_loss = stock_data_intraday.loc[y, 'Prev Day Low'] - 1.0
                # stock_data_intraday.loc[y, 'take'] = take_profit
                # stock_data_intraday.loc[y, 'stop'] = stop_loss
    else:
        sig = 0
        # stop_loss = 0.0
        # take_profit = 0.0
    return stock_data_intraday.head()


class GetPandasDF:

    def __init__(self, ticker, stop, take):
        self.ticker = ticker
        self.stop = stop
        self.take = take

    # intraday data
    def get_intraday_data(self):

        stock_data_i = yf.Ticker(self.ticker)
        stock_daily = pd.DataFrame(stock_data_i.history(period='60d', interval='1d', actions=False)).reset_index()
        stock_data_intraday = pd.DataFrame(stock_data_i.history(period='60d', interval='5m', actions=False))
        stock_data_intraday = stock_data_intraday.reset_index()

        # get ATR
        tr = 0
        for i in stock_daily.index:
            tr += stock_daily.loc[i, 'High'] - stock_daily.loc[i, 'Low']
        ATR = tr/len(stock_daily.index)

        # add prev day low to intraday dataframe
        for i in stock_data_intraday.index:
            stock_data_intraday.loc[i, 'Date'] = stock_data_intraday.loc[i, 'Datetime'].date()

        for y in stock_data_intraday.index:
            filt = stock_data_intraday['Date'] == stock_data_intraday.loc[y, 'Date']
            day_low = stock_data_intraday.loc[filt, 'Low'].min()
            stock_data_intraday.loc[y, 'Day Low'] = day_low

        for v in stock_data_intraday.index:
            if v == 0:
                stock_data_intraday.loc[v, 'Prev Day Low'] = 0
            else:
                if stock_data_intraday.loc[v-1, 'Date'] < stock_data_intraday.loc[v, 'Date']:
                    stock_data_intraday.loc[v, 'Prev Day Low'] = stock_data_intraday.loc[v-1, 'Day Low']
                else:
                    stock_data_intraday.loc[v, 'Prev Day Low'] = stock_data_intraday.loc[v-1, 'Prev Day Low']

        one_day = 0
        sig = 0
        long_price = 0
        stop = self.stop
        take = self.take
        for i in stock_data_intraday.index:
            if i == 0:
                stock_data_intraday.loc[i, 'one day'] = 0
                stock_data_intraday.loc[i, 'pnl'] = 0
            elif i <= len(stock_data_intraday.index):
                if stock_data_intraday.loc[i-1, 'Date'] == stock_data_intraday.loc[i, 'Date']:
                    stock_data_intraday.loc[i, 'one day'] = one_day
                    stock_data_intraday.loc[i, 'pnl'] = 0
                    if sig == 0 and stock_data_intraday.loc[i, 'Low'] <= stock_data_intraday.loc[i, 'Prev Day Low'] and stock_data_intraday.loc[i - 1, 'Low'] > stock_data_intraday.loc[i, 'Prev Day Low']:
                        stock_data_intraday.loc[i, 'trade'] = 1
                        stock_data_intraday.loc[i, 'pnl'] = 0
                        sig = 1
                        long_price = stock_data_intraday.loc[i, 'Prev Day Low']
                        stop_price = long_price - stop
                        profit_price = long_price + take
                    if sig == 1 and long_price != 0:
                        if stop_price >= stock_data_intraday.loc[i, 'Low']:
                            stock_data_intraday.loc[i, 'pnl'] = -stop
                            long_price = 0
                        if profit_price <= stock_data_intraday.loc[i, 'High'] and stock_data_intraday.loc[i, 'trade'] != 1:
                            stock_data_intraday.loc[i, 'pnl'] = take
                            long_price = 0

                elif stock_data_intraday.loc[i - 1, 'Date'] < stock_data_intraday.loc[i, 'Date']:
                    if one_day == 0:
                        one_day = 1
                    else:
                        one_day = 0

                    if long_price != 0:
                        stock_data_intraday.loc[i, 'pnl'] = stock_data_intraday.loc[i-1, 'Close'] - long_price
                        long_price = 0
                    stock_data_intraday.loc[i, 'one day'] = one_day
                    stock_data_intraday.loc[i, 'pnl'] = 0
                    sig = 0
        pnl = stock_data_intraday['pnl'].sum()
        all_trades = stock_data_intraday.loc[stock_data_intraday['pnl'] != 0, 'pnl'].count()
        profit_trades = stock_data_intraday.loc[stock_data_intraday['pnl'] > 0, 'pnl'].count()
        loss_trades = stock_data_intraday.loc[stock_data_intraday['pnl'] < 0, 'pnl'].count()
        return stock_data_intraday.loc[stock_data_intraday['pnl'] != 0], pnl, ATR, all_trades, profit_trades, loss_trades

