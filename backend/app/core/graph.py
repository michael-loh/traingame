from typing import Dict, List, Set, Tuple
from app.models.game import Route, Player

def is_connected(player_id: str, node_start: str, node_end: str, routes: Dict[str, Route]) -> bool:
    """
    Standard BFS to check if two cities are connected by a specific player's network.
    """
    if node_start == node_end:
        return True

    # Build adjacency list for the player
    adj: Dict[str, List[str]] = {}
    for route in routes.values():
        if route.owner_id == player_id:
            adj.setdefault(route.node_a, []).append(route.node_b)
            adj.setdefault(route.node_b, []).append(route.node_a)

    if node_start not in adj:
        return False

    visited: Set[str] = {node_start}
    queue = [node_start]

    while queue:
        current = queue.pop(0)
        if current == node_end:
            return True
        for neighbor in adj.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return False

def get_longest_path(player_id: str, routes: Dict[str, Route]) -> int:
    """
    Calculates the longest continuous path (by route lengths) for a player.
    Each route (edge) can be used only once in the path.
    """
    # Filter only player's routes
    player_routes = [r for r in routes.values() if r.owner_id == player_id]
    if not player_routes:
        return 0

    # Adjacency list: node -> [(neighbor, length, route_id)]
    adj: Dict[str, List[Tuple[str, int, str]]] = {}
    for r in player_routes:
        adj.setdefault(r.node_a, []).append((r.node_b, r.length, r.id))
        adj.setdefault(r.node_b, []).append((r.node_a, r.length, r.id))

    def dfs(current_node: str, visited_edges: Set[str]) -> int:
        max_dist = 0
        for neighbor, length, route_id in adj.get(current_node, []):
            if route_id not in visited_edges:
                visited_edges.add(route_id)
                dist = length + dfs(neighbor, visited_edges)
                max_dist = max(max_dist, dist)
                visited_edges.remove(route_id) # Backtrack
        return max_dist

    total_max = 0
    # Try starting from every node that has at least one route
    for start_node in adj.keys():
        total_max = max(total_max, dfs(start_node, set()))

    return total_max
