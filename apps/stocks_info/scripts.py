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

    df = pd.DataFrame(parsed_data, columns=['ticker', 'date', 'time', 'title', 'href'])

    vader = SentimentIntensityAnalyzer()
    f = lambda title: vader.polarity_scores(title)['compound']
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

    df = pd.DataFrame(parsed_data, columns=['ticker', 'date', 'time', 'title', 'href'])

    vader = SentimentIntensityAnalyzer()
    f = lambda title: vader.polarity_scores(title)['compound']
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
