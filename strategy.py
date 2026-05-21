import backtrader as bt


class EMARSI_Strategy(bt.Strategy):
    params = (
        ('fast_ema', 20),
        ('slow_ema', 50),
        ('rsi_period', 14),
        ('atr_period', 14),
        ('risk_reward', 2),
    )

    def __init__(self):
        self.fast_ema = bt.indicators.EMA(
            self.data.close,
            period=self.params.fast_ema
        )

        self.slow_ema = bt.indicators.EMA(
            self.data.close,
            period=self.params.slow_ema
        )

        self.rsi = bt.indicators.RSI(
            self.data.close,
            period=self.params.rsi_period
        )

        self.atr = bt.indicators.ATR(
            self.data,
            period=self.params.atr_period
        )

        self.crossover = bt.indicators.CrossOver(
            self.fast_ema,
            self.slow_ema
        )

        self.order = None
        self.stop_price = None
        self.target_price = None

    def next(self):

        if self.order:
            return

        if not self.position:

            if self.crossover > 0 and self.rsi > 55:

                atr = self.atr[0]

                stop_distance = atr * 1.5
                target_distance = stop_distance * self.params.risk_reward

                cash = self.broker.get_cash()
                risk_amount = cash * 0.02

                size = risk_amount / stop_distance

                self.stop_price = self.data.close[0] - stop_distance
                self.target_price = self.data.close[0] + target_distance

                self.order = self.buy(size=size)

        else:

            if (
                self.data.close[0] <= self.stop_price
                or self.data.close[0] >= self.target_price
                or self.crossover < 0
            ):
                self.order = self.sell(size=self.position.size)

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            self.order = None
