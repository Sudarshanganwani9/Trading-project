import yfinance as yf
import pandas as pd
import numpy as np
import backtrader as bt

from strategy import EMARSI_Strategy


symbol = 'AAPL'

full_data = yf.download(symbol, start='2015-01-01', end='2025-01-01')

if isinstance(full_data.columns, pd.MultiIndex):
    full_data.columns = full_data.columns.droplevel(1)

window_size = 504
out_sample = 126

scores = []

for start_idx in range(0, len(full_data) - window_size - out_sample, out_sample):

    train = full_data.iloc[start_idx:start_idx + window_size]
    test = full_data.iloc[
        start_idx + window_size:
        start_idx + window_size + out_sample
    ]

    best_return = -999
    best_params = None

    for fast in [10, 20, 30]:
        for slow in [50, 100, 150]:

            if fast >= slow:
                continue

            cerebro = bt.Cerebro()
            train_feed = bt.feeds.PandasData(dataname=train)
            cerebro.adddata(train_feed)
            cerebro.broker.setcash(100000)

            cerebro.addstrategy(
                EMARSI_Strategy,
                fast_ema=fast,
                slow_ema=slow
            )

            cerebro.run()

            final_value = cerebro.broker.getvalue()
            train_return = (
                (final_value - 100000) / 100000
            ) * 100

            if train_return > best_return:
                best_return = train_return
                best_params = (fast, slow)

    fast_best, slow_best = best_params

    test_cerebro = bt.Cerebro()
    test_feed = bt.feeds.PandasData(dataname=test)

    test_cerebro.adddata(test_feed)
    test_cerebro.broker.setcash(100000)

    test_cerebro.addstrategy(
        EMARSI_Strategy,
        fast_ema=fast_best,
        slow_ema=slow_best
    )

    test_cerebro.run()

    test_final = test_cerebro.broker.getvalue()

    out_return = (
        (test_final - 100000) / 100000
    ) * 100

    efficiency = (out_return / best_return) * 100 if best_return != 0 else 0

    scores.append(max(0, efficiency))

wfa_score = np.mean(scores)

print(f'Walk Forward Analysis Score: {wfa_score:.2f}')
