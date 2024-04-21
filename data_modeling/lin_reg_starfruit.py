import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

DAY_TO_TRAIN_ON = 0
DAY_TO_PREDICT = 0
COEFFICIENTS = 4

training_data_path = "data/r4/previous_round.csv"
test_data_path = "data/r4/previous_round.csv"

training_data: pd.DataFrame = pd.read_csv(training_data_path, delimiter=";")
test_data: pd.DataFrame = pd.read_csv(test_data_path, delimiter=";")

# isolate mid prices into a single frame
mid_prices: pd.DataFrame = training_data[training_data["product"] == "STARFRUIT"]["mid_price"].to_frame()
test_mid_prices: pd.DataFrame = test_data[test_data["product"] == "STARFRUIT"]["mid_price"].to_frame()

# add frames with shifted data from previous days
labels = []
for i in range (1, COEFFICIENTS + 1):
    mid_prices[f"mid_price_t-{i}"] = mid_prices["mid_price"].shift(i)
    test_mid_prices[f"mid_price_t-{i}"] = test_mid_prices["mid_price"].shift(i)
    labels.append(f"mid_price_t-{i}")
mid_prices.dropna(inplace = True)
test_mid_prices.dropna(inplace = True)

# prepare features and labels
X = mid_prices[labels].values
test_X = test_mid_prices[labels].values
y = mid_prices["mid_price"].values

# Add a column of ones to X for the intercept
X = np.hstack([np.ones((X.shape[0], 1)), X])
test_X = np.hstack([np.ones((test_X.shape[0], 1)), test_X])


# Step 2: Compute the coefficients using the Normal Equation
theta = np.linalg.inv(X.T.dot(X)).dot(X.T).dot(y)

print(theta.tolist())



# add a sixth column to the mid_prices frame, using theta to calculate the predicted mid price
test_mid_prices["predicted_mid_price"] = test_X.dot(theta)

# use plt to plot the mid prices and the predicted mid prices
plt.plot(test_mid_prices.index, test_mid_prices["mid_price"], label="Mid Price")
plt.plot(test_mid_prices.index, test_mid_prices["predicted_mid_price"], label="Predicted Mid Price")
plt.legend()
plt.show()