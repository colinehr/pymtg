import unittest
from card import Card
from card import Color
import datetime


class TestCard(unittest.TestCase):

    def setUp(self):
        self.bolt = Card.named("Lightning Bolt")
        self.lotus = Card.named("Black Lotus")
        self.skyknight = Card.named("Skyknight Legionnaire")
        self.bears = Card.named("Grizzly Bears")
        self.blow = Card.named("Dismantling Blow")
        self.suspend = Card.named("Ancestral Vision")
        self.liliana = Card.named("Liliana of the Veil")
        self.nissa = Card.named("Nissa, Steward of Elements")
        self.fireice = Card.named("Fire // Ice")

    def test_name(self):
        self.assertEqual(self.bolt.name, "Lightning Bolt")
        self.assertEqual(self.lotus.name, "Black Lotus")

    def test_mana_cost(self):
        self.assertEqual(self.bolt.mana_cost, "{R}")
        self.assertEqual(self.lotus.mana_cost, "{0}")
        self.assertEqual(self.bears.mana_cost, "{1}{G}")
        self.assertEqual(self.suspend.mana_cost, "")

    def test_cmc(self):
        self.assertEqual(self.bolt.cmc, 1)
        self.assertEqual(self.lotus.cmc, 0)
        self.assertEqual(self.suspend.cmc, 0)

    def test_colors(self):
        self.assertEqual(self.bolt.colors, {Color.RED})
        self.assertEqual(self.lotus.colors, set())
        self.assertEqual(self.skyknight.colors, {Color.WHITE, Color.RED})
        self.assertEqual(self.blow.colors, {Color.WHITE})
        self.assertEqual(self.suspend.colors, {Color.BLUE})

    def test_color_id(self):
        self.assertEqual(self.blow.color_identity,
                         {Color.WHITE, Color.BLUE})

    def test_type(self):
        self.assertTrue("Instant" in self.bolt.type_line)
        self.assertTrue("Artifact" in self.lotus.type_line)

    def test_text(self):
        self.assertEqual(self.bolt.oracle_text,
                         "Lightning Bolt deals 3 damage to any target.")
        self.assertEqual(self.bears.oracle_text, "")

    def test_power(self):
        self.assertEqual(self.bears.power, "2")
        self.assertEqual(self.bolt.power, None)

    def test_toughness(self):
        self.assertEqual(self.bears.toughness, "2")
        self.assertEqual(self.lotus.toughness, None)

    def test_loyalty(self):
        self.assertEqual(self.liliana.loyalty, "3")
        self.assertEqual(self.nissa.loyalty, "X")
        self.assertEqual(self.bears.loyalty, None)

    def test_multifaced(self):
        self.assertEqual(self.fireice.cmc, 4)

    def test_property_typing(self):
        self.assertEqual(type(self.skyknight.name), str)
        self.assertEqual(type(self.skyknight.cmc), float)
        self.assertEqual(type(self.skyknight.mana_cost), str)
        self.assertEqual(type(self.skyknight.colors), set)


unittest.main()
