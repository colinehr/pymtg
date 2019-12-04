from card import Card
from color import Color
import lookup
from deck import Deck

def card_named(name, exact=False):
    if not exact:
        name = lookup.autocomplete(name)
    return lookup.find("name", name)

def import_deck(deck_file):
    return Deck(deck_file)
