import pandas as pd

ticker = pd.read_csv("data/predicted-2800.HK.csv", index_col=0)
ticker.index = pd.to_datetime(ticker.index, format = '%Y-%m-%d')


up = ticker["2020-12-27":"2021-01-20"]
down = ticker["2022-02-15":"2022-03-13"]
stable = ticker["2020-04-02":"2020-05-19"]

def accuracy(df):
    delta = df['adjclose'].shift(-1) - df['adjclose']
    delta2 = df['predicted']-df["adjclose"]
    same = delta * delta2 > 0
    acc = same.mean()
    return acc

def mae(df):
    delta = df['predicted']-df["adjclose"]
    mae = delta.abs().mean()
    return mae


total = ticker["2021-9-29":]
print(f"acc of total: {accuracy(total)}")
print(f"mae of total: {mae(total)}")

print(f"acc of up: {accuracy(up)}")
print(f"mae of up: {mae(up)}")

print(f"acc of stable: {accuracy(stable)}")
print(f"mae of stable: {mae(stable)}")

print(f"acc of down: {accuracy(down)}")
print(f"mae of down: {mae(down)}")

# import matplotlib.pyplot as plt

# stable['close'].plot()
# plt.show()