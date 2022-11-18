import re

import numpy as np
from tensorflow.keras.models import load_model

from config import FEATURE_COLUMNS, TEST_SIZE, ticker
from data import load_data
from myBuySellStrategy import runTrade

model_path = "results/2022-11-02_2800.HK-sh-1-sc-1-sbd-0-mae-adam-LSTM-seq-60-step-1-layers-2-units-256.h5"
_,_,SHUFFLE,SCALE,SPLIT_BY_DATE,LOSS,OPTIMIZER,CELLNAME,N_STEPS,LOOKUP_STEP,N_LAYERS,UNITS = \
        re.findall("(\d{4}-\d{2}-\d{2})_(.+?)-sh-(\d)-sc-(\d)-sbd-(\d)-(.+?)-(.+?)-(.+?)-seq-(\d+)-step-(\d+)-layers-(\d+)-units-(\d+)", model_path)[0]
SHUFFLE=bool(int(SHUFFLE))
SCALE=bool(int(SCALE))
SPLIT_BY_DATE=True
N_STEPS=int(N_STEPS)
LOOKUP_STEP=int(LOOKUP_STEP)
N_LAYERS=int(N_LAYERS)
UNITS=int(UNITS)
model = load_model(model_path)

# fetch the daily pricing data from yahoo finance
# load the data
data = load_data(ticker, N_STEPS, scale=SCALE, split_by_date=SPLIT_BY_DATE, 
                shuffle=False, lookup_step=LOOKUP_STEP, test_size=TEST_SIZE, 
                feature_columns=FEATURE_COLUMNS)

# load the data
data2 = load_data(ticker, N_STEPS, scale=False, split_by_date=SPLIT_BY_DATE, 
                shuffle=False, lookup_step=LOOKUP_STEP, test_size=TEST_SIZE, 
                feature_columns=FEATURE_COLUMNS)
X_test = data["X_test"]
y_test = data["y_test"]
# perform prediction and get prices
y_pred = model.predict(X_test)
y_pred = np.squeeze(data["column_scaler"]["adjclose"].inverse_transform(y_pred))
df = data2["test_df"]
df["predicted"] = y_pred

df = df["2021-9-29":]
df.to_csv("data/predicted-2800.HK.csv")
runTrade(df)
