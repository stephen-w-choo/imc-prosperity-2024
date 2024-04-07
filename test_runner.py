from datamodel import TradingState, Observation, Listing, OrderDepth
from base_script_with_limits import Trader

test_state_1 = TradingState(
    "traderData", 
    1000, 
    {
        "PRODUCT1": Listing(
            symbol="PRODUCT1", 
            product="PRODUCT1", 
            denomination= "SEASHELLS"
        ),
        "PRODUCT2": Listing(
            symbol="PRODUCT2", 
            product="PRODUCT2", 
            denomination= "SEASHELLS"
        ),
    }, 
    {
        "PRODUCT1": OrderDepth(
            buy_orders={10: 7, 9: 5},
            sell_orders={11: -4, 12: -8}
        ),
        "PRODUCT2": OrderDepth(
            buy_orders={142: 3, 141: 5},
            sell_orders={144: -5, 145: -8}
        ),	
    }, 
    {}, 
    {}, 
    {
        "PRODUCT1": 3,
        "PRODUCT2": -5
    },
    observations=Observation({}, {})
)

trader = Trader()
output = trader.run(test_state_1)[0]

print(output)

# Test - 

