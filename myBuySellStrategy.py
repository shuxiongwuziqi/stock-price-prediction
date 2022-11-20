import backtrader as bt
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
rate = 0.9
rate2 = 1

# Create a subclass of Strategy to define the indicators and logic
class myStrategy(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = dict()

    def __init__(self):
        self.data_predicted = self.datas[0].predicted

    # def log(self, txt):
    #     '''Logging function'''
    #     dt = self.datas[0].datetime.date(0).isoformat()
    #     print(f'{dt}, {txt}')
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
    # def notify_trade(self, trade):
    #     if not trade.isclosed:
    #         return
    #     self.log(f'OPERATION RESULT --- Gross: {trade.pnl:.2f}, Net: {trade.pnlcomm:.2f}')
    def next(self):
        global rate
        if self.data_predicted > self.datas[0].close:
            # calculate the max number of shares ('all-in')
            size = int(self.broker.getcash() / self.datas[0].close * rate)
            if size > 0:
                # buy order
                # self.log(f'BUY CREATED --- Size: {size}, Cash: {self.broker.getcash():.2f}, Open: {self.data_open[0]}, Close: {self.data_close[0]}')
                self.buy(size=size-1)
        if self.data_predicted < self.datas[0].close and self.position:
            # sell order
            size = self.position.size * rate2
            # self.log(f'SELL CREATED --- Size: {size}')
            self.sell(size=size)

OHLCV = ['open', 'high', 'low', 'close', 'volume']
# class to define the columns we will provide
class MyData(PandasData):
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

def runTrade(prices):
    cerebro = bt.Cerebro()  # create a "Cerebro" engine instance
    data = MyData(dataname=prices)
    cerebro.broker.setcash(1000000.0)
    cerebro.broker.setcommission(commission=0)
    cerebro.adddata(data, name="2800.HK")  # Add the data feed

    cerebro.addstrategy(myStrategy)  # Add the trading strategy
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()  # run it all
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # cerebro.plot()  # and plot it with a single command
    return cerebro.broker.getvalue()

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    prices = pd.read_csv("predicted_data/RFpredicted-2800.HK-random-forest.csv", index_col=0)
    prices.index = pd.to_datetime(prices.index, format = '%Y-%m-%d')
    results = []
    X = []
    Y = []
    for i in range(10):
        rate+=0.097
        rate2=0
        for j in range(10):
            rate2+=0.099
            X.append(rate)
            Y.append(rate2)
            res = runTrade(prices)
            results.append(res)
    max_index = np.argmax(results)
    print(f"buy rate: {X[max_index]} and sell rate: {Y[max_index]} have max profit: {results[max_index]}.")
    
    # ax = plt.axes(projection='3d')
    # ax.scatter3D(X, Y, results,c=results)
    # ax.set_title('3d Scatter plot')
    # ax.set_xlabel("buy rate")
    # ax.set_ylabel("sell rate")
    # plt.show()
    
    
