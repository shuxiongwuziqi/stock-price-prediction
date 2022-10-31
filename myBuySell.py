import backtrader as bt
import pandas as pd
from backtrader.feeds import PandasData

# Create a subclass of Strategy to define the indicators and logic

class SmaCross(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = dict()

    def __init__(self):
        self.data_predicted = self.datas[0].predicted

    def log(self, txt):
        '''Logging function'''
        dt = self.datas[0].datetime.date(0).isoformat()
        print(f'{dt}, {txt}')

    def next(self):
        if self.data_predicted > self.datas[0].close:
            # calculate the max number of shares ('all-in')
            size = int(self.broker.getcash() / self.datas[0].open)
            if size > 0:
                # buy order
                self.log(f'BUY CREATED --- Size: {size}, Cash: {self.broker.getcash():.2f}, Open: {self.data_open[0]}, Close: {self.data_close[0]}')
                self.buy(size=size)
        if self.data_predicted < self.datas[0].close and self.position:
            # sell order
            size = self.position.size * 1
            self.log(f'SELL CREATED --- Size: {size}')
            self.sell(size=size)


cerebro = bt.Cerebro()  # create a "Cerebro" engine instance

OHLCV = ['open', 'high', 'low', 'close', 'volume']
# class to define the columns we will provide
class SignalData(PandasData):
    """
    Define pandas DataFrame structure
    """
    cols = OHLCV + ['predicted']
    # create lines
    lines = tuple(cols)
    # define parameters
    params = {c: -1 for c in cols}
    params.update({'datetime': None})
    params = tuple(params.items())

prices = pd.read_csv("data/predicted-2800.HK.csv", index_col=0)
prices.index = pd.to_datetime(prices.index, format = '%Y-%m-%d')
data = SignalData(dataname=prices)
cerebro.adddata(data, name="2800.HK")  # Add the data feed

cerebro.addstrategy(SmaCross)  # Add the trading strategy
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
cerebro.run()  # run it all
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
cerebro.plot()  # and plot it with a single command
