import numpy as np

"""
Each tile: 7.5k * multiplier 
Every spot has its **treasure multiplier** (up to 100) and the number of 
**hunters** (up to 8). The spot's total treasure is the product of the 
**base treasure** (7500, same for all spots) and the spot's specific treasure 
multiplier. However, the resulting amount is then divided by the sum of the 
hunters and the percentage of all the expeditions (from other players) that 
took place there. For example, if a field has 5 hunters, and 10% of all the 
expeditions (from all the other players) are also going there, the prize you get 
from that field will be divided by 15. After the division, **expedition costs** 
apply (if there are any), and profit is what remains.

Second and third expeditions are optional: you are not required to do all 3. 
Fee for embarking upon a second expedition is 25 000, and for third it's 75 000. 
Order of submitted expeditions does not matter for grading.
"""

tiles = [
    [(24, 2), (70, 4), (41, 3), (21, 2), (60, 4)],
    [(47, 3), (82, 5), (87, 5), (80, 5), (35, 3)],
    [(73, 4), (89, 5), (100, 8), (90, 7), (17, 2)],
    [(77, 5), (83, 5), (85, 5), (79, 5), (55, 4)],
    [(12, 2), (27, 3), (52, 4), (15, 2), (30, 3)]
]

# formula: (7500 * multiplier) / (hunters + percentage) - expedition_cost

# convert tiles into numpy array
# Define a structured data type for the tiles
dt = np.dtype([('multiplier', np.int), ('hunters', np.int)])

# Convert the list of tuples into a structured array
tiles_np = np.array(tiles, dtype=dt)

# apply formula to each tile with percentage as variable argument

def calculate_profit(tile, percentage):
    base_treasure = 7500
    multiplier, hunters = tile
    expedition_cost = 0

    return (base_treasure * multiplier) / (hunters + percentage) - expedition_cost

def calculate_profit_for_all_tiles(tiles, percentage):
    output = (7500 * tiles['multiplier']) / (tiles['hunters'] + percentage) - 0

    return output

# calculate profit for all tiles with 0% percentage
# print(calculate_profit_for_all_tiles(tiles_np, 0))
"""
[[ 90000.         131250.         102500.          78750.       112500.        ]
 [117500.         123000.         130500.         120000.       87500.        ]
 [136875.         133500.          93750.          96428.       63750.        ]
 [115500.         124500.         127500.         118500.       103125.        ]
 [ 45000.          67500.          97500.          56250.       75000.        ]]
"""

# calculate profit for all tiles with 10% percentage
# print(calculate_profit_for_all_tiles(tiles_np, 10))
"""
[[15000.         37500.         23653.         13125.       32142.85714286]
 [27115.         41000.         43500.         40000.       20192.30769231]
 [39107.         44500.         41666.         39705.       10625.        ]
 [38500.         41500.         42500.         39500.       29464.28571429]
 [ 7500.         15576.         27857.          9375.       17307.69230769]]
"""


# calculate profit for all tiles with 20% percentage
# print(calculate_profit_for_all_tiles(tiles_np, 20))
"""
[[ 8181.         21875.         13369.         7159.        18750.        ]
 [15326.         24600.         26100.         24000.       11413.       ]
 [22812.5        26700.         26785.         25000.       5795.    ]
 [23100.         24900.         25500.         23700.       17187.5       ]
 [ 4090.          8804.         16250.          5113.      9782.60869565]]
"""


# calculate profit for all tiles with 50% percentage
# print(calculate_profit_for_all_tiles(tiles_np, 50))
"""
[[ 3461.53846154  9722.22222222  5801.88679245  3028.84615385  8333.33333333]
 [ 6650.94339623 11181.81818182 11863.63636364 10909.09090909  4952.83018868]
 [10138.88888889 12136.36363636 12931.03448276 11842.10526316  2451.92307692]
 [10500.         11318.18181818 11590.90909091 10772.72727273  7638.88888889]
 [ 1730.76923077  3820.75471698  7222.22222222  2163.46153846  4245.28301887]]
"""