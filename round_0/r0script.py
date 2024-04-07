from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict
import math
import collections

# Note - all PRODUCT1 and PRODUCT2 strings are for unit testing purposes only.

POSITION_LIMIT = 20

POSITION_LIMITS = {
	"AMETHYSTS": 20,
	"STARFRUIT": 20,
	"PRODUCT1": 10,
	"PRODUCT2": 20
}


class Trader:
	def get_orders(self, state: TradingState, acceptable_price: int, product: str) -> List[Order]:
		# market taking + making based on Stanford's 2023 entry
		product_order_depth = state.order_depths[product]
		product_position_limit = POSITION_LIMITS[product]
		orders = []
		
		# sort the order books by price (will sort by the key by default)
		orders_sell = sorted(list(product_order_depth.sell_orders.items()), key = lambda x: x[0])
		orders_buy = sorted(list(product_order_depth.buy_orders.items()), key=lambda x: x[0], reverse=True)
		
		lowest_sell_price = orders_sell[0][0]
		lowest_buy_price = orders_buy[0][0]

		# we start with buying - using our current position to determine how much and how aggressively we buy from the market

		buying_pos = state.position.get(product, 0)
		print(f"Acceptable price for {product}: {acceptable_price}")

		for ask, vol in orders_sell:
			# skip if there is no quota left
			if product_position_limit - buying_pos <= 0:
				break

			if ask < acceptable_price:
				# we want to buy
				buy_amount = min(-vol, product_position_limit - buying_pos)
				buying_pos += buy_amount
				assert(buy_amount > 0)
				orders.append(Order(product, ask, buy_amount))

			# if at parity, buy up until we are no longer leveraged
			if ask == acceptable_price and buying_pos < 0:
				buy_amount = min(-vol, -buying_pos)
				buying_pos += buy_amount
				assert(buy_amount > 0)
				orders.append(Order(product, ask, buy_amount))


		
		# TODO - add in market making logic to make our own buy orders if we are not buying enough
				
		# now we sell - we reset our position
		selling_pos = state.position.get(product, 0)

		for bid, vol in orders_buy:
			# positive orders in the list
			# but we are sending negative sell orders, so we negate it
			# max we can sell is -product_position_limit - current position
			# if current position is negative we can sell less - if positive we can sell more
			if -product_position_limit - selling_pos >= 0:
				break

			if bid > acceptable_price:
				sell_amount = max(-vol, -product_position_limit - selling_pos)
				selling_pos += sell_amount
				assert(sell_amount < 0)
				orders.append(Order(product, bid, sell_amount))
		

			# if at parity, sell up until we are no longer leveraged
			if bid == acceptable_price and selling_pos > 0:
				sell_amount = max(-vol, -selling_pos)
				selling_pos += sell_amount
				assert(sell_amount < 0)
				orders.append(Order(product, bid, sell_amount))

		# TODO - add in market making logic to make our own sell orders to undercut
				
		return orders
	
	def get_acceptable_price(self, state: TradingState, product: str) -> int:
		if product == "AMETHYSTS":
			return 10000
		if product == "STARFRUIT":
			return 450 # TODO: implement a linear regression model to determine the acceptable price
		return 0


	def run(self, state: TradingState):
		result = {}

		for product in state.order_depths:
			# TODO - ignoring starfruits for now to get amethyst results
			if product == "STARFRUIT":
				continue
			product_acceptable_price = self.get_acceptable_price(state, product)
			orders = self.get_orders(state, product_acceptable_price, product)
			result[product] = orders
	
	
		traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
		
		conversions = 0 # Don't fully understand conversions? Not really documented in the task description

		return result, conversions, traderData