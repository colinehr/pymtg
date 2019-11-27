class Deck:

    def __init__(self):
        self.card_list = []

    def __init__(self, file_name):
        """Construct a deck from a file containing a list of cards."""
        f = open(file_name, 'r', encoding="utf-8")
        self.card_list = []
        for line in f:
            l = line.split()
            if len(l) == 0:
                continue
            card = Lookup.fromName(' '.join(l[1:]))
            quantity = l[0]
            self.addCard(card, quantity)            

    def addCard(self, card, quantity):
        self.card_list.append([card, quantity])
