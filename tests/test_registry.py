import unittest
from src import registry

class TestRegistry(unittest.TestCase):
    def test_load(self):
        data = registry.load()
        self.assertIsInstance(data, dict)
        self.assertTrue(len(data) > 0)
