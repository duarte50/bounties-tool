from queue import PriorityQueue
from itertools import count
from algorithm.gps import GPS
from algorithm.bounties import Bounties
from algorithm.bounty_status import BountyStatus
from algorithm.nodes import bounty_board, portals

class Pathfinder:
    def __init__(self, inventory_space):
        self.include_teleport_steps = True  # Whether to include teleport steps in the path
        self.include_walking_steps = True  # Whether to include walking steps in the path
        self.inventory_space = inventory_space  # The maximum number of items that can be carried at once
        self.time_to_buy = 3  # The time in seconds it takes to buy an item
        self.time_to_sell = 4  # The time in seconds it takes to sell an item

    def find_best_bounties(self, bounties, detective_level, battle_of_fortunehold_completed,
                           starting_node=bounty_board, ending_node=bounty_board):
        result = {
            "bounties": bounties,
            "actions": [],
            "distance": float("inf")
        }

        gps = GPS(detective_level, battle_of_fortunehold_completed)
        route = self.find_best_route(bounties, gps, result["distance"], starting_node, ending_node)

        result["distance"] = route["distance"]
        result["actions"] = route["actions"]
        return result

    def find_best_route(self, bounties, gps, threshold=float("inf"), starting_node=bounty_board, ending_node=bounty_board):
        pq = PriorityQueue()
        visited = {}
        counter = count()

        pq.put((0, next(counter), {
            "distance": 0,
            "previous_node": None,
            "current_node": starting_node["node"],
            "bounty_states": [BountyStatus.NOT_STARTED for _ in bounties],
            "actions": [],
        }))

        best_distance = float("inf")
        best_route = {}

        while not pq.empty():
            _, _, data = pq.get()

            distance = data["distance"]
            previous_node = data["previous_node"]
            current_node = data["current_node"]
            original_bounty_states = data["bounty_states"]
            original_actions = data["actions"]

            bounty_states = original_bounty_states.copy()
            actions = original_actions.copy()

            # Check if already visited
            visited_key = f"{current_node}-{bounty_states}"

            if visited.get(visited_key, float("inf")) <= distance:
                continue
            visited[visited_key] = distance


            distance_after_trading = distance
            num_items_bought, num_items_sold = 0, 0

            # Sell items at the current location
            for i, bounty in enumerate(bounties):
                if current_node != Bounties.get_bounty(bounty)["buyer"]["node"]:
                    continue

                if bounty_states[i] != BountyStatus.IN_PROGRESS:
                    continue

                if num_items_bought + num_items_sold == 0:
                    self._add_travel_steps(gps, actions, previous_node, current_node)

                num_items_sold += 1
                distance_after_trading += self.time_to_sell

                actions.append({
                    "type": "sell",
                    "item": bounty,
                    "location": Bounties.get_bounty(bounty)["buyer"]["name"],
                    "distance": distance_after_trading,
                })
                bounty_states[i] = BountyStatus.COMPLETED

            # Buy items at the current location
            for i, bounty in enumerate(bounties):
                if not self._can_purchase_more_items(bounty_states):
                    break

                if current_node != Bounties.get_bounty(bounty)["seller"]["node"]:
                    continue

                if bounty_states[i] != BountyStatus.NOT_STARTED:
                    continue

                if num_items_bought + num_items_sold == 0:
                    self._add_travel_steps(gps, actions, previous_node, current_node)

                if num_items_bought == 0:
                    distance_after_trading += self.time_to_buy
                num_items_bought += 1

                actions.append({
                    "type": "buy",
                    "item": bounty,
                    "location": Bounties.get_bounty(bounty)["seller"]["name"],
                    "distance": distance_after_trading,
                })
                bounty_states[i] = BountyStatus.IN_PROGRESS

            if distance_after_trading > threshold:
                return None

            if self._deliveries_completed(bounty_states):
                self._add_travel_steps(gps, actions, current_node, ending_node["node"])
                next_distance = gps.distance(current_node, ending_node["node"])["distance"]
                distance_after_trading += next_distance

                actions.append({
                    "type": "return",
                    "location": ending_node["name"],
                    "distance": distance_after_trading,
                })

                if distance_after_trading < best_distance:
                    best_distance = distance_after_trading
                    best_route = {"actions": actions, "distance": distance_after_trading}

                continue

            # Enqueue next purchase locations
            if self._can_purchase_more_items(bounty_states):
                for i, bounty in enumerate(bounties):
                    if bounty_states[i] == BountyStatus.NOT_STARTED:
                        next_node = Bounties.get_bounty(bounty)["seller"]["node"]
                        next_distance = gps.distance(current_node, next_node)["distance"]
                        pq.put((distance_after_trading + next_distance, next(counter), {
                            "distance": distance_after_trading + next_distance,
                            "previous_node": current_node,
                            "current_node": next_node,
                            "bounty_states": bounty_states.copy(),
                            "actions": actions,
                        }))

            # Enqueue next sell locations
            for i, bounty in enumerate(bounties):
                if bounty_states[i] == BountyStatus.IN_PROGRESS:
                    next_node = Bounties.get_bounty(bounty)["buyer"]["node"]
                    next_distance = gps.distance(current_node, next_node)["distance"]
                    pq.put((distance_after_trading + next_distance, next(counter), {
                        "distance": distance_after_trading + next_distance,
                        "previous_node": current_node,
                        "current_node": next_node,
                        "bounty_states": bounty_states.copy(),
                        "actions": actions,
                    }))

        return best_route

    def _add_travel_steps(self, gps, actions, start_node, end_node):
        if start_node is None:
            start_node = end_node

        path = gps.distance(start_node, end_node)["path"]
        if len(path) < 2:
            return

        current_distance = actions[-1]["distance"] if actions else 0

        for i in range(1, len(path)):
            if self.include_teleport_steps and path[i] in [portals["CRENOPOLIS_MARKET"]["node"], portals["CRENOPOLIS_OUTSKIRTS"]["node"]]:
                portal = portals["CRENOPOLIS_MARKET"] if path[i] == portals["CRENOPOLIS_MARKET"]["node"] else portals["CRENOPOLIS_OUTSKIRTS"]
                actions.append({
                    "type": "teleport",
                    "location": portal["name"],
                    "distance": current_distance + portal["teleport_time"],
                })
            elif self.include_walking_steps:
                actions.append({
                    "type": "walk",
                    "location": path[i],
                })

    def _can_purchase_more_items(self, bounty_states):
        available_space = self.inventory_space
        for state in bounty_states:
            if state == BountyStatus.IN_PROGRESS:
                available_space -= 6
        return available_space >= 6

    def _deliveries_completed(self, bounty_states):
        return all(state == BountyStatus.COMPLETED for state in bounty_states)
