import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from lin_reg_utils import add_delayed_columns, determine_theta, add_intercept_column, combine_dataframes, moving_average, test_theta_on_data, plot_label_vs_predicted

# linear regression for combined basket
# we'll use the previous combined basket prices to predict the 'GIFT_BASKET' price

DAY_TO_TRAIN_ON = 0
DAY_TO_PREDICT = 1
COEFFICIENTS = 20
LOOK_AHEAD = 16

training_data_path = "data/r4/previous_round.csv"
test_data_path = "data/r3/prices_round_3_day_2.csv"

training_data: pd.DataFrame = pd.read_csv(training_data_path, delimiter=";")
print(training_data)
test_data: pd.DataFrame = pd.read_csv(test_data_path, delimiter=";")

def add_combined_basket(merged_data: pd.DataFrame) -> pd.DataFrame:
    # Calculating the 'basket cost'
    merged_data['combined_basket'] = (merged_data['mid_price_chocolate'] * 4 +
                                merged_data['mid_price_strawberries'] * 6 +
                                merged_data['mid_price_roses'] * 1)
    
    # Calculate the difference between 
    merged_data['basket_premium'] = merged_data['mid_price_gift_basket'] - merged_data['combined_basket']

    return merged_data

products_to_combine = ["CHOCOLATE", "STRAWBERRIES", "ROSES", "GIFT_BASKET"]

training_data = combine_dataframes(training_data, products_to_combine)

print(training_data)
trading_data = add_combined_basket(training_data)
test_data = combine_dataframes(test_data, products_to_combine)
test_data = add_combined_basket(test_data)

# add frames with shifted data from previous days
basket_delayed_labels = add_delayed_columns(training_data, "combined_basket", COEFFICIENTS)
premium_delayed_labels = add_delayed_columns(training_data, "mid_price_gift_basket", COEFFICIENTS)

add_delayed_columns(test_data, "combined_basket", COEFFICIENTS)
add_delayed_columns(test_data, "mid_price_gift_basket", COEFFICIENTS)

# 1 - prepare the data for theta 1 for the combined basket
FEATURES = basket_delayed_labels[:COEFFICIENTS - LOOK_AHEAD]

LABEL = "mid_price_gift_basket"
moving_average(training_data, 1, LABEL)

X1 = training_data[FEATURES].values
test_X1 = test_data[FEATURES].values
y1 = training_data[LABEL + "_moving_average"].values


# Add a column of ones to X for the intercept
X1 = add_intercept_column(X1)
test_X1 = add_intercept_column(test_X1)

theta1 = determine_theta(X1, y1, 5.0)

test_data["predicted_mid_price"] = test_X1.dot(theta1) 

print(f"Theta 1: {theta1.tolist()}")

# print the predicted mid prices and the actual mid prices
print(test_data[[LABEL, "predicted_mid_price"]])


# use plt to plot the mid prices and the predicted mid prices
plt.plot(test_data.index, test_data[LABEL], label="Mid Price")
plt.plot(test_data.index, test_data["predicted_mid_price"], label="Predicted Mid Price")
plt.legend()
plt.show()