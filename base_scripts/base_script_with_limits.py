from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import math

# Note - all PRODUCT1 and PRODUCT2 strings are for unit testing purposes only.

POSITION_LIMIT = 20

position_limits = {
	"AMETHYSTS": 20,
	"STARFRUIT": 20,
	"PRODUCT1": 10,
	"PRODUCT2": 20
}

ACCEPTABLE_PRICES = {
	"AMETHYSTS": 1000,
	"STARFRUIT": 450,
	"PRODUCT1": 13,
	"PRODUCT2": 142
}

class Trader:
	def run(self, state: TradingState):
		print("traderData: " + state.traderData)
		print("Observations: " + str(state.observations))
		print("Listings: " + str(state.listings))
		print("Own trades: " + str(state.own_trades))
		print("Market trades: " + str(state.market_trades))
		print("Current position: " + str(state.position))
		result = {}
		for product in state.order_depths:
			order_depth: OrderDepth = state.order_depths[product]
			orders: List[Order] = []
			acceptable_price = ACCEPTABLE_PRICES[product]
			product_position = state.position.get(product, 0)
			product_position_limit = position_limits[product]
			max_buys = product_position_limit - product_position
			max_sells = product_position_limit - (product_position * -1)

			print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))

			for sell_order in list(order_depth.sell_orders.items()):
				print("max buys", max_buys)
				if max_buys <= 0:
					break
				best_ask, best_ask_amount = sell_order
				if int(best_ask) < acceptable_price:
					amount_to_buy = min(max_buys, abs(best_ask_amount))
					print("BUY", str(amount_to_buy) + "x", best_ask)
					orders.append(Order(product, best_ask, amount_to_buy))
					max_buys -= amount_to_buy
				else: 
					print("buying skipped")
					break

			for buy_order in list(order_depth.buy_orders.items()):
				print("max sells", max_sells)
				if max_sells <= 0:
					break
				best_ask, best_ask_amount = buy_order
				if int(best_ask) > acceptable_price:
					amount_to_sell = min(max_buys, best_ask_amount)
					print("SELL", str(-amount_to_sell) + "x", best_ask)
					orders.append(Order(product, best_ask, -amount_to_sell))
					max_sells -= amount_to_sell
				else: 
					print("selling skipped")
					break
			
			# If neither existing buy or sell orders are placed, try to revert to the neutral position
			if len(orders) == 0:
				print("No profitable orders for", product)
				orders.append(Order(product, acceptable_price, product_position * -1))
			
			result[product] = orders
	
	
		traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
		
		conversions = 0 # Don't fully understand conversions? Not really documented in the task description

		return result, conversions, traderData