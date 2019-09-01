import json

import yaml

data = json.load(open("emojis.json"))

possible = set()

fixture_fields = []

for key, emoji in data.items():
    fixture_fields.append(
        dict(
            model="emojis.Emoji",
            pk=f":{key}:",
            fields=dict(
                keywords=emoji["keywords"],
                unicode_string=emoji["char"],
                fitzpatrick_scale=emoji["fitzpatrick_scale"],
                category=emoji["category"],
                disabled=False,
            ),
        )
    )
    possible = possible.union(set(data[key].keys()))

with open("initial_emojis.yaml", "w") as outfile:
    yaml.dump(fixture_fields, outfile, default_flow_style=False)
