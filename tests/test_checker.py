import unittest
from src import checker, registry

class TestChecker(unittest.TestCase):
    def test_check_all(self):
        reg = registry.load()
        results = checker.check_all(reg)
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) > 0)

        r = results[0]
        self.assertIn("name", r)
        self.assertIn("installed", r)
        self.assertIn("version", r)
