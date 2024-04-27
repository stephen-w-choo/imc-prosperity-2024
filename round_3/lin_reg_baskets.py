import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# linear regression for combined basket
# we'll use the previous combined basket prices to predict the 'GIFT_BASKET' price

DAY_TO_TRAIN_ON = 0
DAY_TO_PREDICT = 1
COEFFICIENTS = 8

training_data_path = "data-bottle/prices_round_3_day_2.csv"
test_data_path = "data-bottle/prices_round_3_day_2.csv"

training_data: pd.DataFrame = pd.read_csv(training_data_path, delimiter=";")
test_data: pd.DataFrame = pd.read_csv(test_data_path, delimiter=";")

def combine_dataframes(input_data: pd.DataFrame) -> pd.DataFrame:
    # isolate mid prices into a single frame
    # at each timepoint, create a combined basket of 4 "CHOCOLATE", 6 "STRAWBERRIES", 1 "ROSES"
    # calculate the total cost of the basket at each timepoint
    # plot the total cost of the basket over time
    # Filtering the DataFrame for each product
    
    chocolate_data = input_data[input_data['product'] == 'CHOCOLATE'][['timestamp', 'mid_price']]
    strawberries_data = input_data[input_data['product'] == 'STRAWBERRIES'][['timestamp', 'mid_price']]
    roses_data = input_data[input_data['product'] == 'ROSES'][['timestamp', 'mid_price']]
    gift_basket_data = input_data[input_data['product'] == 'GIFT_BASKET'][['timestamp', 'mid_price']]

    # Merging the DataFrames based on 'timestamp'
    merged_data = pd.merge(chocolate_data, strawberries_data, on='timestamp', suffixes=('_choc', '_straw'))
    merged_data = pd.merge(merged_data, roses_data, on='timestamp')
    merged_data = pd.merge(merged_data, gift_basket_data, on='timestamp', suffixes=('', '_gift'))
    merged_data.rename(columns={'mid_price': 'mid_price_roses', 'mid_price_gift': 'mid_price_gift_basket'}, inplace=True)

    # Calculating the 'basket cost'
    merged_data['combined_basket'] = (merged_data['mid_price_choc'] * 4 +
                                merged_data['mid_price_straw'] * 6 +
                                merged_data['mid_price_roses'] * 1)
    
    # Calculate the difference between 
    merged_data['basket_premium'] = merged_data['mid_price_gift_basket'] - merged_data['combined_basket']

    return merged_data

training_data = combine_dataframes(training_data)
test_data = combine_dataframes(test_data)

def add_delayed_columns(input_data: pd.DataFrame, column_name: str, num_delays: int) -> list[str]:
    delayed_labels = []
    for i in range(1, num_delays + 1):
        input_data[f"{column_name}-{i}"] = input_data[column_name].shift(i)
        delayed_labels.append(f"{column_name}-{i}")
    input_data.dropna(inplace=True)
    
    return delayed_labels

# calculate average basket premium
average_prem = training_data["basket_premium"].mean()

print(f"Average premium: {average_prem}")

# add the average premuim to combined basket
training_data["combined_basket"] = training_data["combined_basket"] 

# add frames with shifted data from previous days
basket_delayed_labels = add_delayed_columns(training_data, "combined_basket", COEFFICIENTS)
premium_delayed_labels = add_delayed_columns(training_data, "basket_premium", COEFFICIENTS)

add_delayed_columns(test_data, "combined_basket", COEFFICIENTS)
add_delayed_columns(test_data, "basket_premium", COEFFICIENTS)

# 1 - prepare the data for theta 1 for the combined basket
X1 = training_data[basket_delayed_labels].values
test_X1 = test_data[basket_delayed_labels].values
y1 = training_data["mid_price_gift_basket"].values

# Add a column of ones to X for the intercept
X1 = np.hstack([np.ones((X1.shape[0], 1)), X1])
test_X1 = np.hstack([np.ones((test_X1.shape[0], 1)), test_X1])

# Ridge regression
lambda_param = 1.0  # This is the regularization parameter. Adjust it as necessary.
I = np.eye(X1.shape[1])  # Identity matrix that matches the shape of X.T * X

# Modify the normal equation to include the ridge penalty
theta1 = np.linalg.inv(X1.T.dot(X1) + lambda_param * I).dot(X1.T).dot(y1)

# theta1 = np.linalg.inv(X1.T.dot(X1)).dot(X1.T).dot(y1)

# mean basket premium
mean_basket_premium = training_data["basket_premium"].mean()
print(f"Mean basket premium: {mean_basket_premium}")


# 2 - prepare the data for theta 2 for the basket premium
X2 = training_data[premium_delayed_labels].values
test_X2 = test_data[premium_delayed_labels].values
y2 = training_data["basket_premium"].values

# Add a column of ones to X for the intercept
X2 = np.hstack([np.ones((X2.shape[0], 1)), X2])
test_X2 = np.hstack([np.ones((test_X2.shape[0], 1)), test_X2])

theta2 = np.linalg.inv(X2.T.dot(X2)).dot(X2.T).dot(y2)


# add a sixth column to the mid_prices frame, using theta to calculate the predicted mid price
test_data["predicted_mid_price"] = test_X1.dot(theta1)

print(f"Theta 1: {theta1.tolist()}")


# print the predicted mid prices and the actual mid prices
print(test_data[["mid_price_gift_basket", "predicted_mid_price"]])

# use plt to plot the mid prices and the predicted mid prices
plt.plot(test_data.index, test_data["mid_price_gift_basket"], label="Mid Price")
plt.plot(test_data.index, test_data["predicted_mid_price"], label="Predicted Mid Price")
plt.legend()
plt.show()