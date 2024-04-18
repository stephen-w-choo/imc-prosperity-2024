import pandas as pd
import numpy as np

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