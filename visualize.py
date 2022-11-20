import backtrader as bt
import pandas as pd
from backtrader.feeds import PandasData


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Create a subclass of Strategy to define the indicators and logic
sellRate = 0
buyRate = 0

class SmaCross(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = dict()

    def __init__(self):
        self.data_predicted = self.datas[0].predicted

    def log(self, txt):
        '''Logging function'''
        dt = self.datas[0].datetime.date(0).isoformat()
        print(f'{dt}, {txt}')
    def error(self, txt):
        dt = self.datas[0].datetime.date(0).isoformat()
        print(f'{bcolors.WARNING}{dt}, {txt}{bcolors.ENDC}')
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # order already submitted/accepted - no action required
            return
        # report executed order
        if order.status in [order.Completed]:
            if order.isbuy():
                # self.log(f'BUY EXECUTED --- Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f},Commission: {order.executed.comm:.2f}')
                self.price = order.executed.price
                self.comm = order.executed.comm
            # else:
                # self.log(f'SELL EXECUTED --- Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f},Commission: {order.executed.comm:.2f}')
        # report failed order
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.error(f'Order Failed: {order.status}')
        # set no pending order
        self.order = None
    def next(self):
        global buyRate
        global sellRate

        if self.data_predicted > self.datas[0].close:
            # calculate the max number of shares ('all-in')
            size = int(self.broker.getcash() / self.datas[0].open * buyRate)
            if size > 0:
                # buy order
                self.log(f'BUY CREATED --- Size: {size}, Cash: {self.broker.getcash():.2f}, Open: {self.data_open[0]}, Close: {self.data_close[0]}')
                self.buy(size=size)
        if self.data_predicted < self.datas[0].close and self.position:
            # sell order
            size = self.position.size * sellRate
            self.log(f'SELL CREATED --- Size: {size}')
            self.sell(size=size)


cerebro = bt.Cerebro()  # create a "Cerebro" engine instance
cerebro.broker.setcash(1000000.0)
cerebro.broker.setcommission(commission=0)

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

prices = pd.read_csv("predicted_data/Predicted_2800.HK_SVM.csv", index_col=0)
prices.index = pd.to_datetime(prices.index, format = '%Y-%m-%d')
data = SignalData(dataname=prices)
cerebro.adddata(data, name="2800.HK")  # Add the data feed

buyRate = 0.7759
sellRate = 1

cerebro.addstrategy(SmaCross)  # Add the trading strategy
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
cerebro.run()  # run it all
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
cerebro.plot()  # and plot it with a single command
