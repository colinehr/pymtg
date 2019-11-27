import unittest
from lookup import Lookup

class TestLookup(unittest.TestCase):

    def test_vague_name(self):
        search = Lookup.fromName("Chromium")
        self.assertTrue(search.name == "Chromium")

    def test_incomplete_name(self):
        search = Lookup.fromName("Lightning Bo").name
        self.assertTrue(search.name == "Lightning Bolt")

unittest.main()
