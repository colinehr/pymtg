import unittest
import lookup

class TestLookup(unittest.TestCase):

    def assertCompletion(self, query, goal):
        search = lookup.from_name(query)
        self.assertEqual(search.name, goal)

    def test_vague_name(self):
        self.assertCompletion("Chromium", "Chromium")
        self.assertCompletion("Shatter", "Shatter")
        
    def test_incomplete_name(self):
        self.assertCompletion("Lightning Bo", "Lightning Bolt")
        self.assertCompletion("Thief of Crowns", "Oko, Thief of Crowns")
        self.assertCompletion("Jac Bel", "Jace Beleren")
        self.assertCompletion("Fblthp the Lost", "Fblthp, the Lost")

    def test_front_face_name(self):
        search = lookup.from_name("Bonecrusher Giant")
        self.assertEqual(search.name, "Bonecrusher Giant // Stomp")
        search = lookup.from_name("Fire")
        self.assertEqual(search.name, "Fire // Ice")

    def test_back_face_name(self):
        search = lookup.from_name("Stomp")
        self.assertEqual(search.name, "Bonecrusher Giant // Stomp")
        search = lookup.from_name("Ice")
        self.assertEqual(search.name, "Fire // Ice")

    def test_case_insensitivity(self):
        self.assertCompletion("giant growth", "Giant Growth")
        self.assertCompletion("bAYou", "Bayou")

    def test_case_and_incomplete(self):
        self.assertCompletion("jac bel", "Jace Beleren")

unittest.main()
