import json
import jsonschema
from kitchen import Kitchen, KitchenItem


def load():
    schema = {
        "type": "object",
        "properties": {
            "kitchen_shape": {
                "type": "object",
                "properties": {
                    "width": {"type": "number"}
                },
                "required": ["width"]
            },
            "available_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "type": {"type": "string"},
                        "zone": {"type": "string"},
                        "position_top": {"type": "boolean"},
                        "position_bottom": {"type": "boolean"},
                        "width_min": {"type": "number"},
                        "width_max": {"type": "number"},
                        "worktop": {"type": "boolean"},
                        "allow_edge": {"type": "boolean"},
                    },
                    "required": ["name", "width_min"]
                }
            }
        },
        "required": ["kitchen_shape", "available_items"]
    }

    with open('input.json') as f:
        # raises an exception if json is not valid
        loaded_data = json.load(f)

    # raises an exception if validation fails
    jsonschema.validate(instance=loaded_data, schema=schema)

    items = [KitchenItem(item['name'], item['width_min'], item['width_max'])
             for item in loaded_data['available_items']]
    kitchen = Kitchen(loaded_data['kitchen_shape']['width'], items)

    return kitchen
