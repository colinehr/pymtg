from color import Color

class Card:
    """Interface for Magic cards.

    Attributes:
        name
        colors
        color_identity
        cmc
        set
        text
        mana_cost
        faces
    """

    def __init__(self, scryfall_dict):
        """Constructs a card object from the output of a Scryfall JSON file."""
        self.values = scryfall_dict
        self.layout = self.values["layout"]
        if self.is_multifaced():
            self.faces = [Face(face) for face in self.values["card_faces"]]
        else:
            self.faces = []
        if "colors" in self.values:
            self.colors = self.parse_colors(self.values["colors"])
        else:
            # Get colors from front face
            self.colors = self.parse_colors(self.faces[0].colors)
        self.color_identity = [Color(x) for x in self.values["color_identity"]]

    def parse_colors(self, color_list):
        return [Color(x) for x in color_list]

    def __str__(self):
        return "{:<30} {:>30}\n{}\n{:<30}".format(
            self.name,
            self.mana_cost,
            self.type_line,
            self.text)

    def __repr__(self):
        return str(self.values)

    # Getter methods for different card values
    @property
    def name(self):
        return self.values["name"]

    @property
    def set(self):
        return self.values["set"]

    @property
    def cmc(self):
        return self.values["cmc"]

    @property
    def text(self):
        if "oracle_text" in self.values:
            return self.values["oracle_text"]
        else:
            return ""

    @property
    def mana_cost(self):
        return self.values["mana_cost"]

    @property
    def type_line(self):
        return self.values["type_line"]

    @property
    def types(self):
        return self.type_line.split(" —")

    # Boolean methods for checking for color
    # (should these check color or color identity?)
    def is_white(self):
        return Color.WHITE in self.colors

    def is_blue(self):
        return Color.BLUE in self.colors

    def is_black(self):
        return Color.BLACK in self.colors

    def is_red(self):
        return Color.RED in self.colors

    def is_green(self):
        return Color.GREEN in self.colors

    def is_colorless(self):
        return len(self.colors) == 0

    def is_multicolored(self):
        return len(self.colors) >= 2

    def is_land(self):
        return "Land" in self.types

    def is_creature(self):
        return "Creature" in self.types

    def is_spell(self):
        return not self.is_land() and not self.is_creature()

    def is_multifaced(self):
        multifaced = ["split", "transform", "flip", "meld", "adventure"]
        return self.layout in multifaced

class Face:

    def __init__(self, face_dict):
        """Contstructs a card face object."""
        self.values = face_dict
        self.name = self.values["name"]
        if "colors" in self.values:
            self.colors = [Color(x) for x in self.values["colors"]]
        else:
            self.colors = []
        
