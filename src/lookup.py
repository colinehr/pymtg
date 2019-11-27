import json
from const import ALL_CARDS
from card import Card

class Lookup:

    def generate_from_file(f):
        with open(f, "r", encoding="utf-8") as json_file:
            for line in json_file:
                line = line.strip()
                if line[0] == '{':
                    try:
                        yield json.loads(line[:-1])
                    except json.decoder.JSONDecodeError:
                        yield None

    def search(key, value):
        """Returns a card object representing the first card found in the JSON
        card list. Generally this will be the most recent printing in a
        so-called "regular" product."""
        for obj in Lookup.generate_from_file(ALL_CARDS):
            if key in obj and obj[key] == value and Lookup.isRegularSet(obj["set_type"]):
                return Card(obj)

    def isRegularSet(set_type):
        return set_type == "core" or \
            set_type == "expansion" or \
            set_type == "masters" or \
            set_type == "draft_innovation" or \
            set_type == "commander"

    def autocomplete(name):
        """Find the closest match of an actual card name from given input."""
        return
                
    def fromName(name):
        """Return a card object whose name matches the input exactly."""
        return Lookup.search("name", name)
