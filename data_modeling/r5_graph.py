import sys
import matplotlib.pyplot as plt
import pandas as pd
from io import StringIO

# this is a graphing and parsing problem

# we need to graph the price over time

# and then we mark the trades for a given snake

ROUND = 3
DAY = 2

PRICES_FILE = f"data/r{ROUND}/prices_round_{ROUND}_day_{DAY}.csv"
TRADES_FILE = f"data/r5/trades_round_{ROUND}_day_{DAY}_wn.csv"
OUTPUT_DIRECTORY = "bot_graphs"

def read_csv(file_path: str) -> pd.DataFrame:
    with open(file_path) as csv_data:
        # Load the CSV data into a DataFrame
        stringified_csv_data = csv_data.read()
        df = pd.read_csv(StringIO(stringified_csv_data), delimiter=';')
        return df
    
def plot_price_chart(df: pd.DataFrame, product: str):
    product_data = df[df['product'] == product]
    plt.plot(product_data['timestamp'], product_data['mid_price'], label='Mid Price')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()

def get_trader_names(df: pd.DataFrame) -> list[str]:
    # get all unique strings in the buyer and seller columns as a list
    # remove duplicates between the two lists
    traders = list(df['buyer'].unique()) + list(df['seller'].unique())
    return list(set(traders))

def get_trades(df: pd.DataFrame, product: str, trader: str):
    trader_buy_data = df[(df['symbol'] == product) & (df['buyer'] == trader)]
    trader_sell_data = df[(df['symbol'] == product) & (df['seller'] == trader)]

    if len(trader_buy_data) == 0 and len(trader_sell_data) == 0:
        return None
    
    print(f"Found {len(trader_buy_data)} buys and {len(trader_sell_data)} sells for {trader} in {product}")

    return (trader_buy_data, trader_sell_data)

def plot_trades(df: pd.DataFrame, product: str, trader: str, trader_data: tuple[pd.DataFrame, pd.DataFrame]):
    trader_buy_data, trader_sell_data = trader_data
    
    plt.scatter(trader_buy_data['timestamp'], trader_buy_data['price'], label='Buy', color='black', marker='X')
    plt.scatter(trader_sell_data['timestamp'], trader_sell_data['price'], label='Sell', color='red', marker='X')
    plt.title(f'Trades for {trader} in {product}')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()

def main():
    prices = read_csv(PRICES_FILE)
    trades = read_csv(TRADES_FILE)

    # for each product
    for product in prices['product'].unique():
        # for each trader for that product
        for trader in get_trader_names(trades):
            trader_data = get_trades(trades, product, trader)
            if not trader_data:
                # print(f"No trades found for {trader} in {product}")
                continue
            
            plt.figure()
            plot_price_chart(prices, product)
            plot_trades(trades, product, trader, trader_data)

            # save the plot
            plt.show()


main()