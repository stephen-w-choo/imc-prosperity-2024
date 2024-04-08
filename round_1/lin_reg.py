import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


df: pd.DataFrame = pd.read_csv("r1.csv", delimiter=";")
print(df.columns)

# isolate mid prices into a single frame
mid_prices: pd.DataFrame = df[df["product"] == "STARFRUIT"]["mid_price"].to_frame()

# add frames with shifted data from previously
for i in range (1, 5):
    mid_prices[f"mid_price_t-{i}"] = mid_prices["mid_price"].shift(i)
mid_prices.dropna(inplace = True)

# prepare features and labels
X = mid_prices[['mid_price_t-1', 'mid_price_t-2', 'mid_price_t-3', 
       'mid_price_t-4']].values
y = mid_prices["mid_price"].values

# Add a column of ones to X for the intercept
X = np.hstack([np.ones((X.shape[0], 1)), X])

# Step 2: Compute the coefficients using the Normal Equation
theta = np.linalg.inv(X.T.dot(X)).dot(X.T).dot(y)

print(theta)

# add a sixth column to the mid_prices frame, using theta to calculate the predicted mid price
mid_prices["predicted_mid_price"] = X.dot(theta)

print(mid_prices)

# use plt to plot the mid prices and the predicted mid prices
plt.plot(mid_prices.index, mid_prices["mid_price"], label="Mid Price")
plt.plot(mid_prices.index, mid_prices["predicted_mid_price"], label="Predicted Mid Price")
plt.legend()
plt.show()