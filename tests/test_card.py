import unittest
from card import Card
import lookup
from color import Color

class TestCard(unittest.TestCase):

    def setUp(self):
        self.bolt = lookup.from_name("Lightning Bolt")
        self.lotus = lookup.from_name("Black Lotus")
        self.avacyn = lookup.from_name("Archangel Avacyn // Avacyn, the Purifier")
        self.fire_ice = lookup.from_name("Fire // Ice")

    def test_name(self):
        self.assertEqual(self.bolt.name, "Lightning Bolt")
        self.assertEqual(self.lotus.name, "Black Lotus")

    def test_cmc(self):
        self.assertEqual(self.bolt.cmc, 1)
        self.assertEqual(self.lotus.cmc, 0)
        self.assertEqual(self.avacyn.cmc, 5)

    def test_colors(self):
        self.assertEqual(self.bolt.colors, [Color.RED])
        self.assertEqual(self.lotus.colors, [])
        self.assertEqual(self.avacyn.colors, [Color.WHITE])

    def test_type(self):
        self.assertTrue("Instant" in self.bolt.type_line)
        self.assertTrue("Artifact" in self.lotus.type_line)
        self.assertTrue("Creature" in self.avacyn.type_line)
        self.assertTrue("Angel" in self.avacyn.type_line)

    def test_text(self):
        self.assertEqual(self.avacyn, "Flash\nFlying, vigilance\nWhen Archangel Avacyn enters the battlefield, creatures you control gain indestructible until end of turn.\nWhen a non-Angel creature you control dies, transform Archangel Avacyn at the beginning of the next upkeep.\n//\nFlying\nWhen this creature transforms into Avacyn, the Purifier, it deals 3 damage to each other creature and each opponent.")

unittest.main()
