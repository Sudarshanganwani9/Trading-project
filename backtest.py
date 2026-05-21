import backtrader as bt
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

from strategy import EMARSI_Strategy


symbol = 'AAPL'
start = '2018-01-01'
end = '2025-01-01'


data = yf.download(symbol, start=start, end=end)

if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.droplevel(1)

cerebro = bt.Cerebro()

feed = bt.feeds.PandasData(dataname=data)
cerebro.adddata(feed)

starting_capital = 100000

cerebro.broker.setcash(starting_capital)

cerebro.broker.setcommission(commission=0.001)

cerebro.addstrategy(EMARSI_Strategy)

cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')

print('Starting Portfolio Value:', cerebro.broker.getvalue())

results = cerebro.run()
strat = results[0]

final_value = cerebro.broker.getvalue()

print('Final Portfolio Value:', final_value)

percentage_return = (
    (final_value - starting_capital) / starting_capital
) * 100

max_drawdown = strat.analyzers.drawdown.get_analysis()['max']['drawdown']

print(f'Percentage Return: {percentage_return:.2f}%')
print(f'Max Drawdown: {max_drawdown:.2f}%')

cerebro.plot(style='candlestick')
