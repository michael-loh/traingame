import pytest
import json
from app.utils.config_loader import load_map_config

def test_load_map_config_success(tmp_path):
    # Create a dummy map file
    map_data = {
        "cities": [{"id": "A", "name": "City A"}, {"id": "B", "name": "City B"}],
        "connections": [
            {
                "nodes": ["A", "B"],
                "length": 3,
                "routes": [
                    {"id": "r1", "color": "red"},
                    {"id": "r2", "color": "blue"}
                ]
            }
        ]
    }
    d = tmp_path / "maps"
    d.mkdir()
    f = d / "test.json"
    f.write_text(json.dumps(map_data))

    cities, routes = load_map_config(str(f))
    
    assert len(cities) == 2
    assert len(routes) == 2
    assert routes["r1"].sibling_id == "r2"
    assert routes["r2"].sibling_id == "r1"
    assert routes["r1"].node_a == "A"
    assert routes["r1"].length == 3

def test_load_map_config_missing_city(tmp_path):
    map_data = {
        "cities": [{"id": "A", "name": "City A"}],
        "connections": [
            {"nodes": ["A", "B"], "length": 2, "routes": [{"id": "r1", "color": "any"}]}
        ]
    }
    f = tmp_path / "bad_map.json"
    f.write_text(json.dumps(map_data))

    with pytest.raises(ValueError, match="references missing cities"):
        load_map_config(str(f))
