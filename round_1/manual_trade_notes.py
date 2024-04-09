"""
Manual trading notes.

We have a linearly distributed profit margin, where at 100 units of profit no one
will sell the product that allows us to profit

And at 0 units of profit everyone will sell the product that allows us to profit.

We are allowed to buy twice - once at an initial price, once at a resrved price.

In this case - I think we can run a brute force simulation where we go from 1 to 99.
At each point, we calculate the profit margin and the number of units we can buy 
at the first price. Then we run brute force again from the remaining units to 99.

It'll be n^2, but given that n = 100, it's not a big deal.

I've drawn it out on paper - I THINK we expect it to reach a max at 933 and 966, but I'm not sure
"""




logs = []

max_profit = 0
profit_1_max_position = 0
profit_2_max_position = 0

for profit_1 in range(100, 0, -1):
    # price will determine the volume we get
    volume_1 = 100 - profit_1

    total_profit_1 = volume_1 * profit_1

    for profit_2 in range(profit_1 - 1, 0, -1):
        # second chance to sell at lower reserve price
        volume_2 = 100 - volume_1 - profit_2

        total_profit_2 = volume_2 * profit_2

        total_profit = total_profit_1 + total_profit_2

        if total_profit > max_profit:
            max_profit = total_profit
            profit_1_max_position = profit_1
            profit_2_max_position = profit_2


        logs.append(f"Price 1 = {900 + profit_1}, Profit 1: {profit_1}, Volume 1: {volume_1}, Price 2: {profit_2 + 900} Profit 2: {profit_2}, Volume 2: {volume_2}, Total Profit: {total_profit}")


with open("manual_trade_notes.log", "w") as file:
    file.write(f"Max profit {max_profit}\n at price 1: {900 + profit_1_max_position}, price 2: {900 + profit_2_max_position}\n")
    
    for log in logs:
        file.write(log + "\n")