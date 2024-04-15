# Trading Pizzas with Devin the Duck 🤔

CONVERSIONS = {
    "shells": {
        "pizza": 1.41,
        "wasabi": 0.61,
        "snowball": 2.08,
    },
    "snowball": {
        "pizza": 0.64,
        "wasabi": 0.3,
        "shells": 0.46,
    },
    "wasabi": {
        "pizza": 2.05,
        "snowball": 3.26,
        "shells": 1.56,
    },
    "pizza": {
        "wasabi": 0.48,
        "snowball": 1.52,
        "shells": 0.71,
    }
}

# we start and end with seashells
# we are looking for the route where given 1 seashell, what is the highest seashell number we can get

# this is a graph search problem
# we can do a recursive dfs to find the highest number of seashells we can get


def recursion(node: str, visited: list, log: list, current_seashells: float):
    if len(visited) >= 7:
        return

    if node == "shells":
        print(f"Reached shells with {current_seashells} seashells, visited: {visited}")
        return 
    
    for resource in CONVERSIONS[node]:
        # if resource not in visited: # this is O(n), but n is small, no point creating a separate set
            visited.append(resource)
            log.append((current_seashells, CONVERSIONS[node][resource]))
            recursion(resource, visited, log, current_seashells * CONVERSIONS[node][resource])
            visited.pop()
            log.pop()

for node in CONVERSIONS["shells"]:
    recursion(node, [node], [], CONVERSIONS["shells"][node])