import time

import pandas as pd
from tensorflow.keras.layers import LSTM

# Window size or the sequence length
N_STEPS = 30
# Lookup step, 1 is the next day
LOOKUP_STEP = 1
# whether to scale feature columns & output price as well
SCALE = True
scale_str = f"sc-{int(SCALE)}"
# whether to shuffle the dataset
SHUFFLE = True
shuffle_str = f"sh-{int(SHUFFLE)}"
# whether to split the training/testing set by date
SPLIT_BY_DATE = True
split_by_date_str = f"sbd-{int(SPLIT_BY_DATE)}"
# test ratio size, 0.2 is 20%
TEST_SIZE = 0.2
# features to use
FEATURE_COLUMNS = ["adjclose", "volume", "open", "high", "low"]
# date now
date_now = time.strftime("%Y-%m-%d")
### model parameters
N_LAYERS = 2
# LSTM cell
CELL = LSTM
# 256 LSTM neurons
UNITS = 256
# 10% dropout
DROPOUT = 0.1
# whether to use bidirectional RNNs
BIDIRECTIONAL = False
### training parameters
# mean absolute error loss
LOSS = "mae"
# huber loss
# LOSS = "huber_loss"
OPTIMIZER = "adam"
BATCH_SIZE = 256
EPOCHS = 500
# Amazon stock market
ticker = pd.read_csv("data/2800.HK.csv", index_col=0)
ticker.index = pd.to_datetime(ticker.index, format = '%Y-%m-%d')
# ticker = "2800.HK"
# model name to save, making it as unique as possible based on parameters
model_name = f"{date_now}_2800.HK-{shuffle_str}-{scale_str}-{split_by_date_str}-\
{LOSS}-{OPTIMIZER}-{CELL.__name__}-seq-{N_STEPS}-step-{LOOKUP_STEP}-layers-{N_LAYERS}-units-{UNITS}"
if BIDIRECTIONAL:
    model_name += "-b"
