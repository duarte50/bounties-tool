from queue import PriorityQueue
from algorithm.nodes import edges, portals

class GPS:
    def __init__(self, detective_level, battle_of_fortunehold_completed):
        """
        Initializes the GPS system with the given detective level and quest completion status.
        Builds the adjacency map used for calculating shortest paths.
        """
        self._adjacency_map = {}
        self._cache = {}
        self._build_adjacency_map(detective_level, battle_of_fortunehold_completed)

    def distance(self, node1, node2):
        """
        Returns the shortest path between two nodes.
        Caches results to optimize repeated queries.
        """
        key = f"{node1}-{node2}"
        if key not in self._cache:
            distance_data = self._calculate_distance(node1, node2)
            self._cache[key] = distance_data
        return self._cache[key]

    def _calculate_distance(self, node1, node2):
        """
        Uses Dijkstra's algorithm to find the shortest path between two nodes.
        """
        if node1 == node2:
            return {"distance": 0, "path": [node1]}

        pq = PriorityQueue()
        pq.put((0, node1))

        distances = {node: float("inf") for node in self._adjacency_map}
        previous = {node: None for node in self._adjacency_map}

        distances[node1] = 0

        while not pq.empty():
            current_distance, current_node = pq.get()

            if current_node == node2:
                path = self._reconstruct_path(previous, node1, node2)
                return {"distance": current_distance, "path": path}

            if current_distance > distances[current_node]:
                continue

            for neighbor, weight in self._adjacency_map.get(current_node, []):
                new_distance = current_distance + weight
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current_node
                    pq.put((new_distance, neighbor))

        raise ValueError(f"No path found between {node1} and {node2}")

    def _reconstruct_path(self, previous, start, target):
        """
        Reconstructs the shortest path using the previous nodes dictionary.
        """
        path = []
        current = target
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        return path if path[0] == start else []

    def _add_edge(self, node1, node2, weight):
        """
        Adds an edge to the adjacency map.
        """
        if node1 not in self._adjacency_map:
            self._adjacency_map[node1] = []

        neighbors = self._adjacency_map[node1]

        # Prevent duplicate edges
        for neighbor, existing_weight in neighbors:
            if neighbor == node2:
                print(f"Edge between {node1} and {node2} already exists. Keeping existing edge with weight {existing_weight}.")
                return

        neighbors.append((node2, weight))

    def _build_adjacency_map(self, detective_level, battle_of_fortunehold_completed):
        """
        Builds the adjacency map based on edges, detective level, and quest completion.
        """
        for edge in edges:
            node1, node2 = edge["nodes"]

            # Skip edges requiring higher detective level
            if edge.get("detective", 0) > detective_level:
                continue

            # Skip edges requiring an incomplete quest
            if edge.get("quest") and not battle_of_fortunehold_completed:
                continue

            # Add weight adjustment for hostile zones
            weight = edge["weight"]
            if edge.get("hostile"):
                weight += edge["chanceOfEncounter"] * edge["timeToResolve"]

            self._add_edge(node1, node2, weight)

            if not edge.get("directed", False):
                self._add_edge(node2, node1, weight)

        # Add portals as universal connections
        for node in self._adjacency_map.keys():
            for portal in portals.values():
                self._add_edge(node, portal["node"], portal["teleport_time"])
