import numpy as np

from config import *
from data import load_data
from model import create_model

# fetch the daily pricing data from yahoo finance
# load the data
data = load_data(ticker, N_STEPS, scale=SCALE, split_by_date=SPLIT_BY_DATE, 
                shuffle=False, lookup_step=LOOKUP_STEP, test_size=TEST_SIZE, 
                feature_columns=FEATURE_COLUMNS)
model_path = "results/2022-10-29_2800.HK-sh-1-sc-1-sbd-1-mae-adam-LSTM-seq-30-step-1-layers-2-units-256.h5"
model = create_model(N_STEPS, len(FEATURE_COLUMNS), loss=LOSS, units=UNITS, cell=CELL, n_layers=N_LAYERS,
                    dropout=DROPOUT, optimizer=OPTIMIZER, bidirectional=BIDIRECTIONAL)
model.load_weights(model_path)

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
df.to_csv("data/predicted-2800.HK.csv")
