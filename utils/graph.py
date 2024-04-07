import sys
import matplotlib.pyplot as plt
import pandas as pd
from io import StringIO

file_path = sys.argv[1]

# CSV data
with open(file_path) as csv_data:
    # Load the CSV data into a DataFrame
    stringified_csv_data = csv_data.read()
    df = pd.read_csv(StringIO(stringified_csv_data), delimiter=';')

    # Split the data by product
    for product in df['product'].unique():
        product_data = df[df['product'] == product]

        # Plotting
        plt.figure()
        plt.plot(product_data['timestamp'], product_data['mid_price'], label='Mid Price')
        plt.plot(product_data['timestamp'], product_data['ask_price_1'], label='Ask Price 1')
        plt.plot(product_data['timestamp'], product_data['bid_price_1'], label='Bid Price 1')
        
        plt.title(f'Price Chart for {product}')
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.legend()
        plt.show()


