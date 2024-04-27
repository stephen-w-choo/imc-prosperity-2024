import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# linear regression for combined basket
# we'll use the previous combined basket prices to predict the 'GIFT_BASKET' price

DAY_TO_TRAIN_ON = 0
DAY_TO_PREDICT = 1
COEFFICIENTS = 5

training_data_path = "data-bottle/prices_round_3_day_1.csv"
test_data_path = "data-bottle/prices_round_3_day_2.csv"

training_data: pd.DataFrame = pd.read_csv(training_data_path, delimiter=";")
test_data: pd.DataFrame = pd.read_csv(test_data_path, delimiter=";")

def combine_dataframes(input_data: pd.DataFrame, products_to_combine: list[str]) -> pd.DataFrame: 
    data: list[pd.DataFrame] = []

    for product in products_to_combine:
        product_data = input_data[input_data['product'] == product][['timestamp', 'mid_price']]
        product_data.rename(columns={'mid_price': f'mid_price_{product.lower()}'}, inplace=True)
        data.append(product_data)

    merged_data = data[0]
    
    for i in range(1, len(data)):
        merged_data = pd.merge(merged_data, data[i], on='timestamp')

    return merged_data

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
trading_data = add_combined_basket(training_data)
test_data = combine_dataframes(test_data, products_to_combine)
test_data = add_combined_basket(test_data)

def add_delayed_columns(input_data: pd.DataFrame, column_name: str, num_delays: int) -> list[str]:
    delayed_labels = []
    for i in range(1, num_delays + 1):
        input_data[f"{column_name}-{i}"] = input_data[column_name].shift(i)
        delayed_labels.append(f"{column_name}-{i}")
    input_data.dropna(inplace=True)
    
    return delayed_labels

def determine_theta(X, y) -> np.ndarray:
    theta = np.linalg.inv(X.T.dot(X)).dot(X.T).dot(y)

    return theta

def add_intercept_column(input_data, features: list[str]) -> np.ndarray:
    return np.hstack([np.ones((input_data.shape[0], 1)), input_data])

# add frames with shifted data from previous days
basket_delayed_labels = add_delayed_columns(training_data, "combined_basket", COEFFICIENTS)
premium_delayed_labels = add_delayed_columns(training_data, "mid_price_gift_basket", COEFFICIENTS)
chocolate_delayed_labels = add_delayed_columns(training_data, "mid_price_chocolate", COEFFICIENTS)
strawberries_delayed_labels = add_delayed_columns(training_data, "mid_price_strawberries", COEFFICIENTS)
roses_delayed_labels = add_delayed_columns(training_data, "mid_price_roses", COEFFICIENTS)

add_delayed_columns(test_data, "combined_basket", COEFFICIENTS)
add_delayed_columns(test_data, "mid_price_gift_basket", COEFFICIENTS)
add_delayed_columns(test_data, "mid_price_chocolate", COEFFICIENTS)
add_delayed_columns(test_data, "mid_price_strawberries", COEFFICIENTS)
add_delayed_columns(test_data, "mid_price_roses", COEFFICIENTS)

# 1 - prepare the data for theta 1 for the combined basket
FEATURES = chocolate_delayed_labels + roses_delayed_labels + premium_delayed_labels
LABEL = "mid_price_strawberries"

X1 = training_data[FEATURES].values
y1 = training_data[LABEL].values

# Add a column of ones to X for the intercept
X1 = add_intercept_column(X1, FEATURES)

theta1 = determine_theta(X1, y1)

print(f"Theta 1: {theta1.tolist()}")

def test_theta_on_data(theta, test_data, features):
    test_X = test_data[features].values
    test_X = add_intercept_column(test_X, features)
    test_data["predicted_mid_price"] = test_X.dot(theta)

    return test_data

test_data = test_theta_on_data(theta1, test_data, FEATURES)

def plot_label_vs_predicted(test_data, label, predicted_label):
    plt.plot(test_data.index, test_data[label], label="Mid Price")
    plt.plot(test_data.index, test_data[predicted_label], label="Predicted Mid Price")
    plt.legend()
    plt.show()

plot_label_vs_predicted(test_data, LABEL, "predicted_mid_price")