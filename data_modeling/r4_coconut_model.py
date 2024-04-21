import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from lin_reg_utils import add_delayed_columns, determine_theta, add_intercept_column, combine_dataframes, moving_average, test_theta_on_data, plot_label_vs_predicted


COEFFICIENTS = 4
LOOK_AHEAD = 0

training_data_path = "data/r4/prices_round_4_day_2.csv"
test_data_path = "data/r4/prices_round_4_day_1.csv"

training_data: pd.DataFrame = pd.read_csv(training_data_path, delimiter=";")
test_data: pd.DataFrame = pd.read_csv(test_data_path, delimiter=";")

products = ["COCONUT", "COCONUT_COUPON"]

# separate out coconut and coconut_coupons into separate columns, sync rows on timestamps
training_data = combine_dataframes(training_data, products)
test_data = combine_dataframes(test_data, products)

# add in delayed columns for each product
coconut_delayed_labels = add_delayed_columns(training_data, "mid_price_coconut", COEFFICIENTS)
coconut_coupon_delayed_labels = add_delayed_columns(training_data, "mid_price_coconut_coupon", COEFFICIENTS)

add_delayed_columns(test_data, "mid_price_coconut", COEFFICIENTS)
add_delayed_columns(test_data, "mid_price_coconut_coupon", COEFFICIENTS)

moving_average(training_data, 13, "mid_price_coconut")
moving_average(training_data, 13, "mid_price_coconut_coupon")
print(training_data)

FEATURES = coconut_delayed_labels[:COEFFICIENTS - LOOK_AHEAD]
LABEL = "mid_price_coconut_coupon"

X = add_intercept_column(training_data[FEATURES].values)
y = training_data[LABEL + "_moving_average"].values

theta = determine_theta(X, y, 100.0)

print(f"Theta: {theta.tolist()}")

test_data = test_theta_on_data(theta, test_data, FEATURES)
plot_label_vs_predicted(test_data, LABEL, "predicted_mid_price")