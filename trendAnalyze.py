import pandas as pd

ticker = pd.read_csv("data/predicted-2800.HK.csv", index_col=0)
ticker.index = pd.to_datetime(ticker.index, format = '%Y-%m-%d')


up = ticker["2020-12-09":"2021-01-22"]
stable = ticker["2020-03-25":"2020-05-27"]
down = ticker["2022-02-08":"2022-03-14"]

def accuracy(df):
    delta = df['adjclose'].shift(-1) - df['adjclose']
    delta2 = df['predicted']-df["adjclose"]
    same = delta * delta2 > 0
    acc = same.mean()
    return acc

total = ticker["2021-9-29":]
print(f"acc of total: {accuracy(total)}")
print(f"acc of up: {accuracy(up)}")
print(f"acc of stable: {accuracy(stable)}")
print(f"acc of down: {accuracy(down)}")