import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def add_delayed_columns(input_data: pd.DataFrame, column_name: str, num_delays: int) -> list[str]:
    delayed_labels = []
    for i in range(1, num_delays + 1):
        input_data[f"{column_name}-{i}"] = input_data[column_name].shift(i)
        delayed_labels.append(f"{column_name}-{i}")
    input_data.dropna(inplace=True)
    
    return delayed_labels

def determine_theta(X, y, alpha = 0.0) -> np.ndarray:
    """
    Ridge regression using the normal equation.
    """
    n, m = X.shape
    I = np.eye(m)
    I[0, 0] = 0

    theta = np.linalg.inv(X.T.dot(X) + alpha * I).dot(X.T).dot(y)

    return theta

def add_intercept_column(input_data) -> np.ndarray:
    return np.hstack([np.ones((input_data.shape[0], 1)), input_data])

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

def moving_average(data, window_size, column):
    """
    Turns the values of a specific column into a moving average.
    """

    data[f"{column}_moving_average"] = data[column].rolling(window=window_size, center=True).mean()
    data[f"{column}_moving_average"].fillna(data[column], inplace=True)

    return data

def test_theta_on_data(theta, test_data, features):
    """
    Takes a theta and features, and returns the predicted label on the test data.
    """
    test_X = test_data[features].values
    test_X = add_intercept_column(test_X)
    test_data["predicted_mid_price"] = test_X.dot(theta)

    return test_data


def plot_label_vs_predicted(test_data, label, predicted_label):
    """
    Takes the test data, the label, and the predicted label and plots them.
    """
    plt.plot(test_data.index, test_data[label], label="Mid Price")
    plt.plot(test_data.index, test_data[predicted_label], label="Predicted Mid Price")
    plt.legend()
    plt.show()