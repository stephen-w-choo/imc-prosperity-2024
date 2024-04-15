import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

DAY_TO_TRAIN_ON = 0
DAY_TO_PREDICT = 1
COEFFICIENTS = 8

training_data_path = f"data/prices_round_2_day_{DAY_TO_TRAIN_ON}.csv"
test_data_path = f"data/prices_round_2_day_{DAY_TO_PREDICT}.csv"
historical_data_path = "data/log_data.csv"

def extract_transform_orchid_history_data(data_path: str, price_column_name: str) -> pd.DataFrame:
    # takes a path, extracts it into a frame, and adds the shifted data
    data: pd.DataFrame = pd.read_csv(data_path, delimiter=";")

    # isolate prices into a single frame
    prices: pd.DataFrame = data[price_column_name].to_frame()

    # add frames with shifted data from previous days
    labels = []
    for i in range (1, COEFFICIENTS + 1):
        prices[f"price_t-{i}"] = prices[price_column_name].shift(i)
        labels.append(f"price_t-{i}")

    prices.dropna(inplace = True)

    return prices

def extract_transform_data_with_column_filter(data_path: str, column_name: str, filter: str) -> pd.DataFrame:
    # takes a path, extracts it into a frame, and adds the shifted data
    data: pd.DataFrame = pd.read_csv(data_path, delimiter=";")
    # isolate prices into a single frame
    prices: pd.DataFrame = data[data[column_name] == filter]["mid_price"].to_frame()

    # add frames with shifted data from previous days
    labels = []
    for i in range (1, COEFFICIENTS + 1):
        prices[f"price_t-{i}"] = prices["mid_price"].shift(i)
        labels.append(f"price_t-{i}")

    prices.dropna(inplace = True)

    return prices

training_data_prices = extract_transform_orchid_history_data(training_data_path, "ORCHIDS")
test_data_prices = extract_transform_data_with_column_filter(historical_data_path, "product", "ORCHIDS")

feature_columns = [col for col in training_data_prices.columns if col != "ORCHIDS"]

print(feature_columns)

# prepare features and labels
X = training_data_prices[feature_columns].values
test_X = test_data_prices[feature_columns].values
y = training_data_prices["ORCHIDS"].values


# Add a column of ones to X for the intercept
X = np.hstack([np.ones((X.shape[0], 1)), X])
test_X = np.hstack([np.ones((test_X.shape[0], 1)), test_X])

# Step 2: Compute the coefficients using the Normal Equation
theta = np.linalg.inv(X.T.dot(X)).dot(X.T).dot(y)

print(test_X)
print(theta)

# add a sixth column to the mid_prices frame, using theta to calculate the predicted mid price
test_data_prices["predicted_orchid_price"] = test_X.dot(theta)

# use plt to plot the mid prices and the predicted mid prices
plt.plot(test_data_prices.index, test_data_prices["mid_price"], label="Orchid Price")
plt.plot(test_data_prices.index, test_data_prices["predicted_orchid_price"], label="Predicted Orchid Price")
plt.legend()
plt.show()