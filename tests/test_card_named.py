import unittest
import card

class TestCardNamed(unittest.TestCase):

    def assertFuzzyMatch(self, query, target):
        self.assertEqual(card.named(query).name, target)

    def test_exact_match(self):
        self.assertFuzzyMatch("Lightning Bolt", "Lightning Bolt")

    def test_ambiguous_name(self):
        self.assertFuzzyMatch("Chromium", "Chromium")
        self.assertFuzzyMatch("Shatter", "Shatter")

    def test_completion(self):
        self.assertFuzzyMatch("Lightning Bo", "Lightning Bolt")
        self.assertFuzzyMatch("Thal", "Thallid")
        self.assertFuzzyMatch("Bonecrusher Giant",
                              "Bonecrusher Giant // Stomp")

    def test_match_face(self):
        self.assertFuzzyMatch("Fire", "Fire // Ice")
        self.assertFuzzyMatch("Ice", "Fire // Ice")

    def test_case_insensitivity(self):
        self.assertFuzzyMatch("jace beleren", "Jace Beleren")
        self.assertFuzzyMatch("giaNT GrOwth", "Giant Growth")

    def test_single_quote(self):
        self.assertFuzzyMatch("Thalia's Lancers", "Thalia's Lancers")

    def test_comma(self):
        self.assertFuzzyMatch("Ugin, the Ineffable", "Ugin, the Ineffable")

    def test_double_quote(self):
        self.assertFuzzyMatch('"Ach! Hans, Run!"', '"Ach! Hans, Run!"')

    def test_regular_set(self):
        search = card.named("Lightning Bolt")
        self.assertEqual(search.set_code, "a25")

    def test_funny_set(self):
        search = card.named("The Cheese Stands Alone")
        self.assertEqual(search.set_code, "ugl")

unittest.main()
