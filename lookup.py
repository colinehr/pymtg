import json
from const import ALL_CARDS, CARD_NAMES
from card import Card
from enum import Enum

class Property(Enum):
    NAME = "name"
    CMC = "cmc"
    COLORS = "colors"
    TYPE = "type_line"
    COLOR_ID = "color_identity"
    SET_CODE = "set"

def generate_from_file(f):
    with open(f, "r", encoding="utf-8") as json_file:
        for line in json_file:
            line = line.strip()
            if line[0] == '{':
                try:
                    yield json.loads(line[:-1])
                except json.decoder.JSONDecodeError:
                    yield None

def find(key, value):
    """Returns a card object representing the first card found in the JSON
    card list. Generally this will be the most recent printing in a
    so-called "regular" product."""
    for obj in generate_from_file(ALL_CARDS):
        if obj == None:
            print("ERROR: no card found with", key, value)
            break
        if key in obj and obj[key] == value and isRegularSet(obj["set_type"]):
            return Card(obj)

def search(bool_list):
    pass

def isRegularSet(set_type):
    return set_type == "core" or \
        set_type == "expansion" or \
        set_type == "masters" or \
        set_type == "draft_innovation" or \
        set_type == "commander"

def autocomplete(name):
    """Find the closest match of an actual card name from given input.
    
    TODO Work for case-insensitive matches."""
    with open(CARD_NAMES, "r", encoding="utf-8") as f:
        name_list = json.loads(f.read())["data"]
        casefolded_names = [name.casefold() for name in name_list]
        # check for exact matches
        if name.casefold() in casefolded_names:
            i = casefolded_names.index(name.casefold())
            return name_list[i]      
        # check for names that start with q
        starts_with_name = [x for x in name_list \
                            if x.casefold().startswith(name.casefold())]
        if len(starts_with_name) > 0:
            return shortest(starts_with_name)
        # check for names that contain query
        contains_name = [x for x in name_list if name in x]
        if len(contains_name) > 0:
            return shortest(contains_name)
        return None

def from_name(name):
    """Return a card object whose name matches the input exactly."""
    return find("name", autocomplete(name))

def shortest(l):
    return sorted(l, key=len)[0]
