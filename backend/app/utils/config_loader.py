import json
from pathlib import Path
from typing import Dict, List, Tuple
from app.models.game import City, Route, RouteColor

def load_map_config(file_path: str) -> Tuple[Dict[str, City], Dict[str, Route]]:
    """
    Parses a map JSON file and returns dictionaries of Cities and Routes.
    Automatically wires sibling_id for parallel routes.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Map config not found at {file_path}")

    with open(path, "r") as f:
        data = json.load(f)

    cities: Dict[str, City] = {}
    for city_data in data.get("cities", []):
        city = City(**city_data)
        cities[city.id] = city

    routes: Dict[str, Route] = {}
    for conn in data.get("connections", []):
        nodes = conn["nodes"]
        length = conn["length"]
        conn_routes = conn["routes"]
        
        # Keep track of routes in this connection to wire siblings
        connection_route_ids = []
        
        for r_data in conn_routes:
            route_id = r_data["id"]
            node_a, node_b = nodes
            
            if node_a not in cities or node_b not in cities:
                raise ValueError(f"Route {route_id} references missing cities: {node_a}, {node_b}")

            route = Route(
                id=route_id,
                node_a=nodes[0],
                node_b=nodes[1],
                length=length,
                color=RouteColor(r_data["color"]),
                required_wildcards=r_data.get("required_wildcards", 0)
            )
            routes[route_id] = route
            connection_route_ids.append(route_id)
        
        # Wire siblings if there are exactly 2 routes (Double Route)
        if len(connection_route_ids) == 2:
            id_a, id_b = connection_route_ids
            routes[id_a].sibling_id = id_b
            routes[id_b].sibling_id = id_a
        # Note: If there were 3+ routes, we'd need a list of sibling_ids, 
        # but the spec currently handles standard double routes.

    return cities, routes
