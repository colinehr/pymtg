from color import Color

class Card:

    def __init__(self, scryfall_dict):
        """Constructs a card object from the output of a Scryfall JSON file."""
        self.values = scryfall_dict
        self.colors = [Color(x) for x in self.values["colors"]]
        self.color_identity = [Color(x) for x in self.values["color_identity"]]

    # Getter methods for different card values
    @property
    def name(self):
        return self.values["name"]

    @property
    def set(self):
        return self.values["set"]

    # Boolean methods for checking for certain qualities
    def isWhite(self):
        return Color.WHITE in self.colors

    def isBlue(self):
        return Color.BLUE in self.colors

    def isBlack(self):
        return Color.BLACK in self.colors

    def isRed(self):
        return Color.RED in self.colors

    def isGreen(self):
        return Color.GREEN in self.colors

    def isColorless(self):
        return len(self.colors) == 0

    def isMulticolored(self):
        return len(self.colors) >= 2
