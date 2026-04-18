from app.models.game import Route, RouteColor
from app.core.graph import is_connected, get_longest_path

def test_is_connected():
    routes = {
        "r1": Route(id="r1", node_a="A", node_b="B", length=2, color=RouteColor.RED, owner_id="p1"),
        "r2": Route(id="r2", node_a="B", node_b="C", length=2, color=RouteColor.BLUE, owner_id="p1"),
        "r3": Route(id="r3", node_a="C", node_b="D", length=2, color=RouteColor.GREEN, owner_id="p2"),
    }
    
    assert is_connected("p1", "A", "C", routes) == True
    assert is_connected("p1", "A", "D", routes) == False
    assert is_connected("p2", "C", "D", routes) == True

def test_longest_path():
    # Simple line: A-B-C-D (lengths 2, 3, 4)
    routes = {
        "r1": Route(id="r1", node_a="A", node_b="B", length=2, color=RouteColor.ANY, owner_id="p1"),
        "r2": Route(id="r2", node_a="B", node_b="C", length=3, color=RouteColor.ANY, owner_id="p1"),
        "r3": Route(id="r3", node_a="C", node_b="D", length=4, color=RouteColor.ANY, owner_id="p1"),
        "r4": Route(id="r4", node_a="D", node_b="E", length=5, color=RouteColor.ANY, owner_id="p2"), # Not p1
    }
    # Longest path for p1 should be 2+3+4 = 9
    assert get_longest_path("p1", routes) == 9

def test_longest_path_loop():
    # Loop: A-B-C-A
    routes = {
        "r1": Route(id="r1", node_a="A", node_b="B", length=2, color=RouteColor.ANY, owner_id="p1"),
        "r2": Route(id="r2", node_a="B", node_b="C", length=2, color=RouteColor.ANY, owner_id="p1"),
        "r3": Route(id="r3", node_a="C", node_b="A", length=2, color=RouteColor.ANY, owner_id="p1"),
        "r4": Route(id="r4", node_a="C", node_b="D", length=10, color=RouteColor.ANY, owner_id="p1"),
    }
    # Longest path: D-C-B-A-C = 10+2+2+2 = 16
    # (Cannot reuse edges, but can visit nodes twice)
    assert get_longest_path("p1", routes) == 16
