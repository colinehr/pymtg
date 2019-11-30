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
            if obj == None:
                print("ERROR: no card found with", key, value)
                break
            if key in obj and obj[key] == value and Lookup.isRegularSet(obj["set_type"]):
                return Card(obj)

    def isRegularSet(set_type):
        return set_type == "core" or \
            set_type == "expansion" or \
            set_type == "masters" or \
            set_type == "draft_innovation" or \
            set_type == "commander"

    def autocomplete(name):
        """Find the closest match of an actual card name from given input.

        TODO Work for case-insensitive matches."""
        with open("../data/card-names.json", "r", encoding="utf-8") as f:
            name_list = json.loads(f.read())["data"]
            # check for exact matches
            if name in name_list:
                return name
            # check for names that start with q
            starts_with_name = [x for x in name_list if x.startswith(name)]
            if len(starts_with_name) > 0:
                return shortest(starts_with_name)
            # check for names that contain query
            contains_name = [x for x in name_list if name in x]
            if len(contains_name) > 0:
                return shortest(contains_name)
            return None
                
    def from_name(name):
        """Return a card object whose name matches the input exactly."""
        return Lookup.search("name", Lookup.autocomplete(name))

def shortest(l):
    return sorted(l, key=len)[0]
