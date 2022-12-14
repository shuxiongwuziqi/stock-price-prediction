import glob
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model

from config import FEATURE_COLUMNS, TEST_SIZE, ticker
from data import load_data


def plot_graph(test_df, LOOKUP_STEP):
    """
    This function plots true close price along with predicted close price
    with blue and red colors respectively
    """
    plt.figure(figsize=(8, 6))
    plt.plot(test_df[f'true_adjclose_{LOOKUP_STEP}'], c='b',linewidth=1.0)
    plt.plot(test_df[f'adjclose_{LOOKUP_STEP}'], c='r',linewidth=1.0)
    plt.xlabel("Days")
    plt.ylabel("Price")
    plt.legend(["Actual Price", "Predicted Price"])
    plt.savefig('results/predict.jpg', dpi=1200, bbox_inches='tight')
    # plt.show()

def get_final_df(model, data, SCALE, LOOKUP_STEP):
    """
    This function takes the `model` and `data` dict to 
    construct a final dataframe that includes the features along 
    with true and predicted prices of the testing dataset
    """
    # if predicted future price is higher than the current, 
    # then calculate the true future price minus the current price, to get the buy profit
    buy_profit  = lambda current, pred_future, true_future: true_future - current if pred_future > current else 0
    # if the predicted future price is lower than the current price,
    # then subtract the true future price from the current price
    sell_profit = lambda current, pred_future, true_future: current - true_future if pred_future < current else 0
    X_test = data["X_test"]
    y_test = data["y_test"]
    # perform prediction and get prices
    y_pred = model.predict(X_test)
    if SCALE:
        y_test = np.squeeze(data["column_scaler"]["adjclose"].inverse_transform(np.expand_dims(y_test, axis=0)))
        y_pred = np.squeeze(data["column_scaler"]["adjclose"].inverse_transform(y_pred))
    test_df = data["test_df"]
    # add predicted future prices to the dataframe
    test_df[f"adjclose_{LOOKUP_STEP}"] = y_pred
    # add true future prices to the dataframe
    test_df[f"true_adjclose_{LOOKUP_STEP}"] = y_test
    
    # calculate the mean absolute error (inverse scaling)
    mae = np.sum(np.abs(y_pred-y_test))/y_pred.size

    # sort the dataframe by date
    test_df.sort_index(inplace=True)
    final_df = test_df
    # add the buy profit column
    final_df["buy_profit"] = list(map(buy_profit, 
                                    final_df["adjclose"], 
                                    final_df[f"adjclose_{LOOKUP_STEP}"], 
                                    final_df[f"true_adjclose_{LOOKUP_STEP}"])
                                    # since we don't have profit for last sequence, add 0's
                                    )
    # add the sell profit column
    final_df["sell_profit"] = list(map(sell_profit, 
                                    final_df["adjclose"], 
                                    final_df[f"adjclose_{LOOKUP_STEP}"], 
                                    final_df[f"true_adjclose_{LOOKUP_STEP}"])
                                    # since we don't have profit for last sequence, add 0's
                                    )
    return final_df, mae

def predict(model, data, N_STEPS, SCALE):
    # retrieve the last sequence from data
    last_sequence = data["last_sequence"][-N_STEPS:]
    # expand dimension
    last_sequence = np.expand_dims(last_sequence, axis=0)
    # get the prediction (scaled from 0 to 1)
    prediction = model.predict(last_sequence)
    # get the price (by inverting the scaling)
    if SCALE:
        predicted_price = data["column_scaler"]["adjclose"].inverse_transform(prediction)[0][0]
    else:
        predicted_price = prediction[0][0]
    return predicted_price


model_paths = glob.glob("results/*.h5")
results = []
for i in range(len(model_paths)):
    path = model_paths[i]
    print(path)
    _,_,SHUFFLE,SCALE,SPLIT_BY_DATE,LOSS,OPTIMIZER,CELLNAME,N_STEPS,LOOKUP_STEP,N_LAYERS,UNITS = \
        re.findall("(\d{4}-\d{2}-\d{2})_(.+?)-sh-(\d)-sc-(\d)-sbd-(\d)-(.+?)-(.+?)-(.+?)-seq-(\d+)-step-(\d+)-layers-(\d+)-units-(\d+)", path)[0]
    SHUFFLE=bool(int(SHUFFLE))
    SCALE=bool(int(SCALE))
    SPLIT_BY_DATE=bool(int(SPLIT_BY_DATE))
    N_STEPS=int(N_STEPS)
    LOOKUP_STEP=int(LOOKUP_STEP)
    N_LAYERS=int(N_LAYERS)
    UNITS=int(UNITS)
    model = load_model(path)

    # load the data
    data = load_data(ticker, N_STEPS, scale=SCALE, split_by_date=True, 
                    shuffle=SHUFFLE, lookup_step=LOOKUP_STEP, test_size=TEST_SIZE, 
                    feature_columns=FEATURE_COLUMNS)

    # get the final dataframe for the testing set
    final_df, mae = get_final_df(model, data, SCALE, LOOKUP_STEP)
    # plot_graph(final_df, LOOKUP_STEP)

    # predict the future price
    future_price = predict(model, data, N_STEPS, SCALE)

    # we calculate the accuracy by counting the number of positive profits
    accuracy_score = (len(final_df[final_df['sell_profit'] > 0]) + len(final_df[final_df['buy_profit'] > 0])) / len(final_df)
    # calculating total buy & sell profit
    total_buy_profit  = final_df["buy_profit"].sum()
    total_sell_profit = final_df["sell_profit"].sum()
    # total profit by adding sell & buy together
    total_profit = total_buy_profit + total_sell_profit
    # dividing total profit by number of testing samples (number of trades)
    profit_per_trade = total_profit / len(final_df)

    # printing metrics
    print(f"Future price after {LOOKUP_STEP} days is {future_price:.2f}$")
    print("Mean Absolute Error:", mae)
    print("Accuracy score:", accuracy_score)
    print("Total buy profit:", total_buy_profit)
    print("Total sell profit:", total_sell_profit)
    print("Total profit:", total_profit)
    print("Profit per trade:", profit_per_trade)
    result = [N_STEPS, LOOKUP_STEP,SCALE,SHUFFLE,SPLIT_BY_DATE,N_LAYERS, mae, accuracy_score, total_buy_profit, total_sell_profit, total_profit, profit_per_trade]
    results.append(result)
    
pd = pd.DataFrame(results, columns=["N_STEPS","LOOKUP_STEP","SCALE","SHUFFLE","SPLIT_BY_DATE","N_LAYERS","mae",\
     "accuracy_score", "total_buy_profit", "total_sell_profit", "total_profit", "profit_per_trade"])
pd.to_csv("data/compare_model.csv")
