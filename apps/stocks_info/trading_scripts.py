import yfinance as yf
import pandas as pd


class GetStockData:
    def __init__(self, ticker='spy', period='max', interval='1d'):
        self.ticker = ticker
        self.period = period
        self.interval = interval

    def history(self):
        tick_data = yf.Ticker(self.ticker)
        history = pd.DataFrame(tick_data.history(period=self.period, interval=self.interval, actions=False)).reset_index()
        return history
