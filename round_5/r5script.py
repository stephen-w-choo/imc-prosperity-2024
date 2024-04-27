import jsonpickle
import json
from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState
from typing import Any, List, Dict
import math

# Note - all PRODUCT1 and PRODUCT2 strings are for unit testing purposes only.

POSITION_LIMITS = {
	"AMETHYSTS": 20,
	"STARFRUIT": 20,
	"ORCHIDS": 100,
	"PRODUCT1": 10,
	"PRODUCT2": 20,
	"CHOCOLATE": 250,
	"STRAWBERRIES": 350,
	"ROSES": 60,
	"GIFT_BASKET": 30,
	"COCONUT": 300,
	"COCONUT_COUPON": 600
}

PRICE_AGGRESSION = { # determines how aggressively we hunt for values above and below the spread
	"AMETHYSTS": 0,
	"STARFRUIT": 0,
	"ORCHIDS": 2,
	"GIFT_BASKET": 30,
	"ROSES": 30,
	"COCONUT": 10,
	"COCONUT_COUPON": 10
}

THRESHOLDS = {
	"AMETHYSTS": {
		"over": 0,
		"mid": 10
	},
	"STARFRUIT": {
		"over": 0,
		"mid": 10
	},
	"ORCHIDS": {
		"over": 20,
		"mid": 40
	},
	"GIFT_BASKET": {
		"over": 0,
		"mid": 10
	},
	"ROSES": {
		"over": 0,
		"mid": 10
	},
	"COCONUT": {
		"over": 0,
		"mid": 10
	},
	"COCONUT_COUPON": {
		"over": 0,
		"mid": 10
	}
}

STARFRUIT_COEFFICIENTS = [108.58978030240314, 0.29584445482712773, 0.259183591772433, 0.2132367610881145, 0.2100929993504117]
GIFT_BASKET_COEFFICIENTS = [-13673.546215617556, 0.6553198504769995, 0.03780108604274801, 0.06623209619669979, 0.44125000957927796]
COUPON_COEFFICIENTS = [-5360.484564543847, 0.2039640893178425, 0.050859032432779505, 0.05239892104401023, 0.291641177781248]

class Logger:
    def __init__(self) -> None:
        self.logs = ""
        self.max_log_length = 3750

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]], conversions: int, trader_data: str) -> None:
        base_length = len(self.to_json([
            self.compress_state(state, ""),
            self.compress_orders(orders),
            conversions,
            "",
            "",
        ]))

        # We truncate state.traderData, trader_data, and self.logs to the same max. length to fit the log limit
        max_item_length = (self.max_log_length - base_length) // 3

        print(self.to_json([
            self.compress_state(state, self.truncate(state.traderData, max_item_length)),
            self.compress_orders(orders),
            conversions,
            self.truncate(trader_data, max_item_length),
            self.truncate(self.logs, max_item_length),
        ]))

        self.logs = ""

    def compress_state(self, state: TradingState, trader_data: str) -> list[Any]:
        return [
            state.timestamp,
            trader_data,
            self.compress_listings(state.listings),
            self.compress_order_depths(state.order_depths),
            self.compress_trades(state.own_trades),
            self.compress_trades(state.market_trades),
            state.position,
            self.compress_observations(state.observations),
        ]

    def compress_listings(self, listings: dict[Symbol, Listing]) -> list[list[Any]]:
        compressed = []
        for listing in listings.values():
            compressed.append([listing["symbol"], listing["product"], listing["denomination"]])

        return compressed

    def compress_order_depths(self, order_depths: dict[Symbol, OrderDepth]) -> dict[Symbol, list[Any]]:
        compressed = {}
        for symbol, order_depth in order_depths.items():
            compressed[symbol] = [order_depth.buy_orders, order_depth.sell_orders]

        return compressed

    def compress_trades(self, trades: dict[Symbol, list[Trade]]) -> list[list[Any]]:
        compressed = []
        for arr in trades.values():
            for trade in arr:
                compressed.append([
                    trade.symbol,
                    trade.price,
                    trade.quantity,
                    trade.buyer,
                    trade.seller,
                    trade.timestamp,
                ])

        return compressed

    def compress_observations(self, observations: Observation) -> list[Any]:
        conversion_observations = {}
        for product, observation in observations.conversionObservations.items():
            conversion_observations[product] = [
                observation.bidPrice,
                observation.askPrice,
                observation.transportFees,
                observation.exportTariff,
                observation.importTariff,
                observation.sunlight,
                observation.humidity,
            ]

        return [observations.plainValueObservations, conversion_observations]

    def compress_orders(self, orders: dict[Symbol, list[Order]]) -> list[list[Any]]:
        compressed = []
        for arr in orders.values():
            for order in arr:
                compressed.append([order.symbol, order.price, order.quantity])

        return compressed

    def to_json(self, value: Any) -> str:
        return json.dumps(value, cls=ProsperityEncoder, separators=(",", ":"))

    def truncate(self, value: str, max_length: int) -> str:
        if len(value) <= max_length:
            return value

        return value[:max_length - 3] + "..."

logger = Logger()

class Trader:
	previous_starfruit_prices = []
	previous_gift_basket_prices = []
	previous_chocolate_prices = []
	previous_strawberry_prices = []
	previous_rose_prices = []
	previous_premium_basket_prices = []
	previous_coconut_prices = []
	previous_coconut_coupon_prices = []
	market_taking: list[tuple[str, int, bool]] = []
	next_market_taking: list[tuple[str, int]] = []

	def arbitrage(self, state: TradingState, product: str) -> tuple[list[Order], int]:
		south_state = state.observations.conversionObservations["ORCHIDS"]
		south_sell_price = south_state.askPrice + south_state.transportFees + south_state.importTariff
		south_buy_price = south_state.bidPrice - south_state.transportFees - south_state.exportTariff

		acceptable_buy_price = math.floor(south_buy_price)
		acceptable_sell_price = math.ceil(south_sell_price)

		# Get the orders
		orders = self.get_orders(state, acceptable_sell_price, acceptable_buy_price, product, PRICE_AGGRESSION[product])

		# Get the conversions
		conversions: int = 0

		conversion_limit = state.position.get(product, 0)

		for index, (market_taking_product, market_taking_amount, seen) in enumerate(self.market_taking):
			if conversion_limit == 0:
				break
			if market_taking_product == product:
				if conversion_limit > 0 and market_taking_amount > 0:
					conversions -= min(conversion_limit, market_taking_amount)
					conversion_limit += conversions
					self.market_taking[index] = (market_taking_product, market_taking_amount, True)
				elif conversion_limit < 0 and market_taking_amount < 0:
					conversions += min(-conversion_limit, -market_taking_amount)
					conversion_limit += conversions
					self.market_taking[index] = (market_taking_product, market_taking_amount, True)

		return orders, conversions
	
	def update_conversions(self, previousStateData, state: TradingState):
		self.market_taking = previousStateData.market_taking

		# remove all market taking that has been seen
		self.market_taking = [(product, amount, seen) for product, amount, seen in self.market_taking if not seen]
			
	def update_starfruit_price_history(self, previousTradingState, tradingState: TradingState):
		self.previous_starfruit_prices = previousTradingState.previous_starfruit_prices

		# get the current price and append it to the list
		lowest_sell_price = sorted(tradingState.order_depths["STARFRUIT"].sell_orders.keys())[0]
		highest_buy_price = sorted(tradingState.order_depths["STARFRUIT"].buy_orders.keys(), reverse=True)[0]

		current_mid_price = (lowest_sell_price + highest_buy_price) / 2

		self.previous_starfruit_prices.append(current_mid_price)

		if len(self.previous_starfruit_prices) > 4:
			self.previous_starfruit_prices.pop(0)

	def update_coconut_price_history(self, previousTradingState, tradingState: TradingState):
		self.previous_coconut_coupon_prices = previousTradingState.previous_coconut_coupon_prices
		self.previous_coconut_prices = previousTradingState.previous_coconut_prices

		for product in ["COCONUT", "COCONUT_COUPON"]:
			# get the current price and append it to the list
			lowest_sell_price = sorted(tradingState.order_depths[product].sell_orders.keys())[0]
			highest_buy_price = sorted(tradingState.order_depths[product].buy_orders.keys(), reverse=True)[0]

			current_mid_price = (lowest_sell_price + highest_buy_price) / 2

			if product == "COCONUT":
				self.previous_coconut_prices.append(current_mid_price)
			elif product == "COCONUT_COUPON":
				self.previous_coconut_coupon_prices.append(current_mid_price)

			if len(self.previous_coconut_prices) > 5:
				self.previous_coconut_prices.pop(0)
			if len(self.previous_coconut_coupon_prices) > 5:
				self.previous_coconut_coupon_prices.pop(0)

	def update_combined_gift_basket_price_history(self, previousTradingState, tradingState: TradingState):
		self.previous_chocolate_prices = previousTradingState.previous_chocolate_prices
		self.previous_rose_prices = previousTradingState.previous_rose_prices
		self.previous_strawberry_prices = previousTradingState.previous_strawberry_prices
		self.previous_gift_basket_prices = previousTradingState.previous_gift_basket_prices
		self.previous_premium_basket_prices = previousTradingState.previous_premium_basket_prices

		good_to_list = {
			"CHOCOLATE": self.previous_chocolate_prices,
			"STRAWBERRIES": self.previous_strawberry_prices,
			"ROSES": self.previous_rose_prices,
			"GIFT_BASKET": self.previous_premium_basket_prices
		}

		# get the current price and append it to the list
		gift_basket = 0

		for good in good_to_list:
			current_mid_price = self.get_mid_price(good, tradingState)

			if good == "CHOCOLATE":
				gift_basket += current_mid_price * 4
			elif good == "STRAWBERRIES":
				gift_basket += current_mid_price * 6
			elif good == "ROSES":
				gift_basket += current_mid_price
		
			good_to_list[good].append(current_mid_price)

			if len(good_to_list[good]) > 5:
				good_to_list[good].pop(0)
		
		self.previous_gift_basket_prices.append(gift_basket)

		if len(self.previous_gift_basket_prices) > 5:
			self.previous_gift_basket_prices.pop(0)

	def get_mid_price(self, product: str, state) -> float:
		lowest_sell_price = sorted(state.order_depths[product].sell_orders.keys())[0]
		highest_buy_price = sorted(state.order_depths[product].buy_orders.keys(), reverse=True)[0]

		return (lowest_sell_price + highest_buy_price) / 2

	def get_combined_gift_basket_price(self, state: TradingState) -> float | None:
		# if we don't have enough data, return None
		if len(self.previous_gift_basket_prices) < 4:
			return None

		return None

	def get_starfruit_price(self) -> float | None:
		# if we don't have enough data, return None
		if len(self.previous_starfruit_prices) < 4:
			return None

		# calculate the average of the last four prices
		expected_price = STARFRUIT_COEFFICIENTS[0] + sum([STARFRUIT_COEFFICIENTS[i + 1] * self.previous_starfruit_prices[i] for i in range(4)])

		return expected_price
	
	def get_coconut_coupon_price(self) -> float | None:
		return None

	def get_orders(self, state: TradingState, acceptable_sell_price: int, acceptable_buy_price: int, product: str, price_aggression: int) -> List[Order]:
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

			if ask < acceptable_buy_price - price_aggression:
				# we want to buy
				buy_amount = min(-vol, product_position_limit - buying_pos)
				buying_pos += buy_amount
				assert(buy_amount > 0)
				orders.append(Order(product, ask, buy_amount))
				self.market_taking.append((product, buy_amount, False))

			# if overleveraged, buy up until we are no longer leveraged
			if ask == acceptable_buy_price - price_aggression and buying_pos < 0:
				buy_amount = min(-vol, -buying_pos)
				buying_pos += buy_amount
				assert(buy_amount > 0)
				orders.append(Order(product, ask, buy_amount))
				self.market_taking.append((product, buy_amount, False))

		# once we exhaust all profitable sell orders, we place additional buy orders
		# at a price acceptable to us
		# what that price looks like will depend on our position
		
		if product_position_limit - buying_pos > 0: # if we have capacity
			if buying_pos < THRESHOLDS[product]["over"]: # if we are overleveraged to sell, buy at parity for price up to neutral position
				target_buy_price = min(acceptable_buy_price - price_aggression, lowest_buy_price + 1)
				vol = -buying_pos + THRESHOLDS[product]["over"]
				orders.append(Order(product, target_buy_price, vol))
				buying_pos += vol
			if THRESHOLDS[product]["over"] <= buying_pos <= THRESHOLDS[product]["mid"]:
				target_buy_price = min(acceptable_buy_price - 1 - price_aggression, lowest_buy_price + 1)
				vol = -buying_pos + THRESHOLDS[product]["mid"] # if we are close to neutral
				orders.append(Order(product, target_buy_price, vol))
				buying_pos += vol
			if buying_pos >= THRESHOLDS[product]["mid"]:
				target_buy_price = min(acceptable_buy_price - 2 - price_aggression, lowest_buy_price + 1)
				vol = product_position_limit - buying_pos
				orders.append(Order(product, target_buy_price, vol))
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

			if bid > acceptable_sell_price + price_aggression:
				sell_amount = max(-vol, -product_position_limit - selling_pos)
				selling_pos += sell_amount
				assert(sell_amount < 0)
				orders.append(Order(product, bid, sell_amount))
				self.market_taking.append((product, sell_amount, False))
		
			# if at parity, sell up until we are no longer leveraged
			if bid == acceptable_sell_price + price_aggression and selling_pos > 0:
				sell_amount = max(-vol, -selling_pos)
				selling_pos += sell_amount
				assert(sell_amount < 0)
				orders.append(Order(product, bid, sell_amount))
				self.market_taking.append((product, sell_amount, False))

		# start market making with remaining quota
		# if selling_pos
		if -product_position_limit - selling_pos < 0:
			if selling_pos > -THRESHOLDS[product]["over"]:
				target_sell_price = max(acceptable_sell_price + price_aggression, lowest_sell_price - 1)
				vol = -selling_pos - THRESHOLDS[product]["over"]
				orders.append(Order(product, target_sell_price, vol))
				selling_pos += vol
			if -THRESHOLDS[product]["over"] >= selling_pos >= -THRESHOLDS[product]["mid"]:
				target_sell_price = max(acceptable_sell_price + 1 + price_aggression, lowest_sell_price - 1)
				vol = -selling_pos - THRESHOLDS[product]["mid"]
				orders.append(Order(product, target_sell_price, vol))
				selling_pos += vol
			if -THRESHOLDS[product]["mid"] >= selling_pos:
				target_sell_price = max(acceptable_sell_price + 2 + price_aggression, lowest_sell_price - 1)
				vol = -product_position_limit - selling_pos
				orders.append(Order(product, target_sell_price, vol))
				selling_pos += vol
				
		return orders
	
	def get_acceptable_price(self, state: TradingState, product: str) -> int | float | None:
		if product == "AMETHYSTS":
			return 10000
		if product == "STARFRUIT":
			return self.get_starfruit_price()
		if product == "GIFT_BASKET":
			return self.get_combined_gift_basket_price(state)
		if product == "COCONUT_COUPON":
			return self.get_coconut_coupon_price()
		return None

	def refresh_runner_state(self, state: TradingState):
		try:
			previousStateData = jsonpickle.decode(state.traderData)
			self.update_starfruit_price_history(previousStateData, state)
			self.update_conversions(previousStateData, state)
			self.update_combined_gift_basket_price_history(previousStateData, state)
			self.update_coconut_price_history(previousStateData, state)
		except:
			pass

	def follow_rhianna_roses(self, trades: List[Trade], state: TradingState):
		# we want to follow Rhianna's trades
		# if she buys, we buy
		# if she sells, we sell
		orders = []

		for trade in trades:
			logger.print(f"ROSES being bought by {trade.buyer} sold by {trade.seller}")

			if trade.seller.lower() == "rhianna":
				lowest_sell_price = sorted(state.order_depths["ROSES"].sell_orders.keys())[0]
				sell_limit = -state.position.get("ROSES", 0) - POSITION_LIMITS["ROSES"]
				orders.append(Order("ROSES", lowest_sell_price - 1, sell_limit))
			if trade.buyer.lower() == "rhianna":
				highest_buy_price = sorted(state.order_depths["ROSES"].buy_orders.keys(), reverse=True)[0]
				buy_limit = -state.position.get("ROSES", 0) + POSITION_LIMITS["ROSES"]
				orders.append(Order("ROSES", highest_buy_price + 1, buy_limit))
		
		return orders
	
	def follow_trader(self, trades: List[Trade], state: TradingState, trader: str, product: str, price_aggression: int):
		# we want to follow a trader's trades
		# if they buy, we buy
		# if they sell, we sell
		orders = []

		for trade in trades:
			logger.print(f"{product} being bought by {trade.buyer} sold by {trade.seller}")

			if trade.seller.lower() == trader:
				lowest_sell_price = sorted(state.order_depths[product].sell_orders.keys())[0]
				sell_limit = -state.position.get(product, 0) - POSITION_LIMITS[product]
				orders.append(Order(product, lowest_sell_price - 1 + price_aggression, sell_limit))
			if trade.buyer.lower() == trader:
				highest_buy_price = sorted(state.order_depths[product].buy_orders.keys(), reverse=True)[0]
				buy_limit = -state.position.get(product, 0) + POSITION_LIMITS[product]
				orders.append(Order(product, highest_buy_price + 1 - price_aggression, buy_limit))
		
		return orders
	
	def follow_other_traders(self, state: TradingState):
		orders = []

		market_trades = state.market_trades

		for product in market_trades:
			if product == "ROSES":
				orders += self.follow_trader(market_trades[product], state, "rhianna", product, 0)
			if product == "CHOCOLATE":
				orders += self.follow_trader(market_trades[product], state, "vinnie", product, 2)

		return orders

	def run(self, state: TradingState):
		self.refresh_runner_state(state)

		result = {}

		conversions = 0

		# follow other traders
		followed_orders = self.follow_other_traders(state)
		for order in followed_orders:
			if order.symbol not in result:
				result[order.symbol] = []

			result[order.symbol].append(order)

		for product in state.order_depths:
			if product == "ORCHIDS":
				orders, conversions = self.arbitrage(state, product)
				result[product] = orders
				continue

			product_acceptable_price = self.get_acceptable_price(state, product)
			if product_acceptable_price is None:
				continue
			else:
				product_acceptable_buy_price = math.floor(product_acceptable_price)
				product_acceptable_sell_price = math.ceil(product_acceptable_price)
				orders = self.get_orders(state, product_acceptable_sell_price, product_acceptable_buy_price, product, PRICE_AGGRESSION[product])
				result[product] = orders

		serialisedTraderData = jsonpickle.encode(self)
		if serialisedTraderData == None:
			serialisedTraderData = ""
		
		orchid_orders = 0

		for order in result["ORCHIDS"]:
			orchid_orders += order.quantity

		logger.print(result)

		logger.flush(state, result, conversions, "")

		return result, conversions, serialisedTraderData