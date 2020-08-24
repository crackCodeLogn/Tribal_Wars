"""
@author Vivek
@since 24/08/20
"""

# PYTHON string based template
villa_template = """        ^
            "x": {x},
            "y": {y},
            "location": "{x}|{y}",
            "name": "Barb",
            "points": {pts},
            "ignore": {ignore},
            "meta": "{meta}",
            "units": [0,0,{axe},1,{lcav},0,0,0]
        $,"""

# JINJA based template
local_config_template = """
{
    "speed": {{speed}},
    "driver": "{{driver}}",
    "villa": {
        "mode": "{{base.mode}}",
        "world": {{base.world}},
        "id": {{base.id}},
        "x": {{base.x}},
        "y": {{base.y}},
        "name": "{{base.name}}",
        "points": {{base.points}},
        "meta": "{{base.meta}}"
    },
    "farming": [{% set counter = [0] %}{% for villa in villas %}{% if counter.append(counter.pop()+1) %}{% endif %}
        {
            "x": {{villa.x}},
            "y": {{villa.y}},
            "location": "{{villa.coordinates}}",
            "name": "{{villa.name}}",
            "points": {{villa.points}},
            "ignore": {{villa.ignore_json}},
            "meta": "{{villa.meta}}",
            "units": {{villa.units}}
        }{% if counter[0] < villa_count %},{% endif %}{% endfor %}
    ]
}
"""
