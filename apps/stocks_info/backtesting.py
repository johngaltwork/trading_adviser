import pandas as pd
import yfinance as yf
import datetime


class BreakOutMorningRange:

    def backtest(self, ticker, tf, period, profit):
        stock_data = yf.Ticker(ticker)
        stock_data = pd.DataFrame(stock_data.history(period=str(period) + 'd', interval=str(tf) + 'm', actions=False))
        sd = stock_data.reset_index().round(2)

        filt = sd['Datetime'].dt.time == datetime.time(9, 30)
        sd['FirstBar'] = False
        sd.loc[filt, 'FirstBar'] = True
        sd['state'] = None
        sd['time'] = sd['Datetime'].dt.time
        last_bar = 60 - int(tf)

        long_price = 0
        short_price = 0
        sd['PnL'] = 0
        test_stat = {
            'all_trades': 0,
            'long_trades': 0,
            'short_trades': 0,
            'profit_long_trades': 0,
            'loss_long_trades': 0,
            'profit_short_trades': 0,
            'loss_short_trades': 0,
        }

        sd['long_profit'] = 0
        sd['long_loss'] = 0
        sd['short_profit'] = 0
        sd['short_loss'] = 0

        for i in sd.index:
            if sd.loc[i, 'FirstBar']:
                long_price = sd.loc[i, 'High']
                short_price = sd.loc[i, 'Low']
                sd.loc[i, 'state'] = 'no trade'
            else:
                if sd.loc[i - 1, 'state'] == 'closed trade':
                    sd.loc[i, 'state'] = 'closed trade'
                if long_price > sd.loc[i, 'High'] and short_price < sd.loc[i, 'Low'] \
                        and sd.loc[i - 1, 'state'] == 'no trade':
                    sd.loc[i, 'state'] = 'no trade'

                if long_price <= sd.loc[i, 'High'] and sd.loc[i - 1, 'state'] == 'no trade':
                    sd.loc[i, 'state'] = 'long'
                    test_stat['long_trades'] += 1
                    test_stat['all_trades'] += 1

                elif short_price >= sd.loc[i, 'Low'] and sd.loc[i - 1, 'state'] == 'no trade':
                    sd.loc[i, 'state'] = 'short'
                    test_stat['short_trades'] += 1
                    test_stat['all_trades'] += 1

                elif sd.loc[i - 1, 'state'] == 'long':
                    if short_price < sd.loc[i, 'Low'] and sd.loc[i, 'time'] < datetime.time(15, last_bar):
                        sd.loc[i, 'state'] = 'long'
                        if sd.loc[i, 'High'] > long_price + profit * (long_price - short_price):
                            sd.loc[i, 'PnL'] = profit
                            sd.loc[i, 'state'] = 'closed trade'

                            sd.loc[i, 'long_profit'] = 1
                            test_stat['profit_long_trades'] += 1

                    elif short_price >= sd.loc[i, 'Low']:
                        sd.loc[i, 'state'] = 'closed trade'
                        sd.loc[i, 'PnL'] = -1

                        sd.loc[i, 'long_loss'] = 1
                        test_stat['loss_long_trades'] += 1

                    elif sd.loc[i, 'time'] == datetime.time(15, last_bar):
                        sd.loc[i, 'state'] = 'closed trade'
                        long_pnl_on_close = (sd.loc[i, 'Close'] - long_price) / (long_price - short_price)
                        sd.loc[i, 'PnL'] = round(long_pnl_on_close, 2)
                        if long_pnl_on_close >= 0:
                            sd.loc[i, 'long_profit'] = 1
                            test_stat['profit_long_trades'] += 1
                        else:
                            sd.loc[i, 'long_loss'] = 1
                            test_stat['loss_long_trades'] += 1
                elif sd.loc[i - 1, 'state'] == 'short':
                    if long_price > sd.loc[i, 'High'] and sd.loc[i, 'time'] < datetime.time(15, last_bar):
                        sd.loc[i, 'state'] = 'short'
                        if sd.loc[i, 'Low'] < short_price - profit * (long_price - short_price):
                            sd.loc[i, 'PnL'] = profit
                            sd.loc[i, 'state'] = 'closed trade'

                            sd.loc[i, 'short_profit'] = 1
                            test_stat['profit_short_trades'] += 1

                    elif long_price <= sd.loc[i, 'High']:
                        sd.loc[i, 'state'] = 'closed trade'
                        sd.loc[i, 'PnL'] = -1

                        sd.loc[i, 'short_loss'] = 1
                        test_stat['loss_short_trades'] += 1

                    elif sd.loc[i, 'time'] == datetime.time(15, last_bar):
                        sd.loc[i, 'state'] = 'closed trade'
                        short_pnl_on_close = (short_price - sd.loc[i, 'Close']) / (long_price - short_price)
                        sd.loc[i, 'PnL'] = round(short_pnl_on_close, 2)
                        if short_pnl_on_close >= 0:
                            sd.loc[i, 'short_profit'] = 1
                            test_stat['profit_short_trades'] += 1
                        else:
                            sd.loc[i, 'short_loss'] = 1
                            test_stat['loss_short_trades'] += 1

        profit_trades = sd.loc[sd['PnL'] > 0, 'PnL'].count()
        loss_trades = sd.loc[sd['PnL'] < 0, 'PnL'].count()
        long_profit = sd['long_profit'].sum()
        long_loss = sd['long_loss'].sum()
        short_profit = sd['short_profit'].sum()
        short_loss = sd['short_loss'].sum()
        winrate = profit_trades / (profit_trades + loss_trades) * 100

        return ticker, round(sd['PnL'].sum(), 2), test_stat, profit_trades, \
               loss_trades, long_profit, long_loss, short_profit, short_loss, round(winrate, 2), profit, tf
