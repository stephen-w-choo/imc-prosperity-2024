from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string

class Trader:
	def run(self, state: TradingState):
		print("traderData: " + state.traderData)
		print("Observations: " + str(state.observations))
		print("Own trades: " + str(state.own_trades))
		print("Market trades: " + str(state.market_trades))
		print("Current position: " + str(state.position))
		result = {}
		for product in state.order_depths:
			order_depth: OrderDepth = state.order_depths[product]
			orders: List[Order] = []
			acceptable_price = 13;  # Participant should calculate this value

			if len(order_depth.sell_orders) != 0:
				# looks at the first sell order only - can be improved by iterating up to a position limit
				best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
				if int(best_ask) < acceptable_price:
					print("BUY", str(-best_ask_amount) + "x", best_ask)
					orders.append(Order(product, best_ask, -best_ask_amount))
	
			if len(order_depth.buy_orders) != 0:
				# looks at the first buy order only - can be improved by iterating up to a position limit
				best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
				if int(best_bid) > acceptable_price:
					print("SELL", str(best_bid_amount) + "x", best_bid)
					orders.append(Order(product, best_bid, -best_bid_amount))
			
			result[product] = orders
	
	
		traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
		
		conversions = 1
		return result, conversions, traderData