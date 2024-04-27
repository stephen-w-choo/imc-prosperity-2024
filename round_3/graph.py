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

    # at each timepoint, create a combined basket of 4 "CHOCOLATE", 6 "STRAWBERRIES", 1 "ROSES"
    # calculate the total cost of the basket at each timepoint
    # plot the total cost of the basket over time
    # Filtering the DataFrame for each product
    chocolate_data = df[df['product'] == 'CHOCOLATE'][['timestamp', 'mid_price']]
    strawberries_data = df[df['product'] == 'STRAWBERRIES'][['timestamp', 'mid_price']]
    roses_data = df[df['product'] == 'ROSES'][['timestamp', 'mid_price']]
    gift_basket_data = df[df['product'] == 'GIFT_BASKET'][['timestamp', 'mid_price']]

    # Merging the DataFrames based on 'timestamp'
    merged_data = pd.merge(chocolate_data, strawberries_data, on='timestamp', suffixes=('_choc', '_straw'))
    merged_data = pd.merge(merged_data, roses_data, on='timestamp')
    merged_data = pd.merge(merged_data, gift_basket_data, on='timestamp', suffixes=('', '_gift'))
    merged_data.rename(columns={'mid_price': 'mid_price_roses', 'mid_price_gift': 'mid_price_gift_basket'}, inplace=True)

    # Calculating the 'basket cost'
    merged_data['basket cost'] = (merged_data['mid_price_choc'] * 4 +
                                merged_data['mid_price_straw'] * 6 +
                                merged_data['mid_price_roses'] * 1 + 400)

    # Displaying the result
    print(merged_data[['timestamp', 'basket cost']])

    merged_data['basket_premium'] = merged_data['mid_price_gift_basket'] - merged_data['basket cost']

    # Plotting
    plt.figure()
    plt.plot(merged_data['timestamp'], merged_data['basket cost'], label='Basket Cost')
    plt.plot(merged_data['timestamp'], merged_data['mid_price_gift_basket'], label='Gift Basket Price')
    plt.title('Basket Cost Over Time')
    plt.xlabel('Time')
    plt.ylabel('Cost')
    plt.legend()
    plt.show()

    # separate plot for basket premium
    plt.figure()
    plt.plot(merged_data['timestamp'], merged_data['basket_premium'], label='Basket Premium')
    plt.title('Basket Premium Over Time')
    plt.xlabel('Time')
    plt.ylabel('Cost')
    plt.legend()
    plt.show()
