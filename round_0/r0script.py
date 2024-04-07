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

PRICE_AGGRESSION = 0 # determines how aggressively we hunt for values above and below the spread

THRESHOLDS = {
	"over": -5,
	"mid": 10
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

		for ask, vol in orders_sell:
			# skip if there is no quota left
			if product_position_limit - buying_pos <= 0:
				break

			if ask < acceptable_price - PRICE_AGGRESSION:
				# we want to buy
				buy_amount = min(-vol, product_position_limit - buying_pos)
				buying_pos += buy_amount
				assert(buy_amount > 0)
				orders.append(Order(product, ask, -buy_amount))

			# if overleveraged, buy up until we are no longer leveraged
			if ask == acceptable_price and buying_pos < 0:
				buy_amount = min(-vol, -buying_pos)
				buying_pos += buy_amount
				assert(buy_amount > 0)
				orders.append(Order(product, ask, -buy_amount))

		# once we exhaust all profitable sell orders, we place additional buy orders
		# at a price acceptable to us
		# what that price looks like will depend on our position
		
		if product_position_limit - buying_pos > 0: # if we have capacity
			if buying_pos < THRESHOLDS["over"]: # if we are overleveraged to sell, buy at parity for price up to neutral position
				target_buy_price = min(acceptable_price, lowest_buy_price + 1)
				vol = -buying_pos + THRESHOLDS["over"]
				orders.append(Order(product, target_buy_price, vol))
				print(f"Market making 1: buying {vol} at {target_buy_price}")
				buying_pos += vol
			if THRESHOLDS["over"] <= buying_pos <= THRESHOLDS["mid"]:
				target_buy_price = min(acceptable_price - 1, lowest_buy_price + 1)
				vol = -buying_pos + THRESHOLDS["mid"] # if we are close to neutral
				orders.append(Order(product, target_buy_price, vol))
				print(f"Market making 2: buying {vol} at {target_buy_price}")
				buying_pos += vol
			if buying_pos >= THRESHOLDS["mid"]:
				target_buy_price = min(acceptable_price - 3, lowest_buy_price + 1)
				vol = product_position_limit - buying_pos
				orders.append(Order(product, target_buy_price, vol))
				print(f"Market making 3: buying {vol} at {target_buy_price}")
				buying_pos += vol
				
		# now we sell - we reset our position
		selling_pos = state.position.get(product, 0)

		for bid, vol in orders_buy:
			# positive orders in the list
			# but we are sending negative sell orders, so we negate it
			# max we can sell is -product_position_limit - current position
			# if current position is negative we can sell less - if positive we can sell more
			
			if -product_position_limit - selling_pos >= 0:
				break

			if bid > acceptable_price + PRICE_AGGRESSION:
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

		# start market making with remaining quota
		# if selling_pos
				
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