import lookup
from card import Card

class Deck:

    def __init__(self):
        self.mainboard = []
        self.sideboard = []

    def __init__(self, file_name):
        """Construct a deck from a file containing a list of cards."""
        f = open(file_name, 'r', encoding="utf-8")
        self.mainboard = []
        self.sideboard = []
        add = self.add_card
        for line in f:
            l = line.split()
            if len(l) == 0:
                add = self.add_to_sideboard
                continue
            card = lookup.from_name(' '.join(l[1:]))
            quantity = l[0]
            add(card, quantity)

    def __str__(self):
        main = _card_list_to_str(self.mainboard)
        side = _card_list_to_str(self.sideboard)
        return "Mainboard:\n" + main + "\n\nSideboard:\n" + side

    def add_card(self, card, quantity):
        self.mainboard.append([card, quantity])
        self.mainboard.sort(key=parse_cmc)

    def add_to_sideboard(self, card, quantity):
        self.sideboard.append([card, quantity])

    def lands(self):
        return [card for card in self.mainboard if card.is_land()]

def parse_cmc(quantity_and_card):
    return quantity_and_card[0].cmc

def _card_list_to_str(l):
    return '\n'.join([c[1] + " " + c[0].name for c in l])
