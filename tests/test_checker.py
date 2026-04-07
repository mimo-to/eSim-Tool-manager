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
        self.assertIn("path_issue", r)
        self.assertIn("min_version", r)
        self.assertIn("conflict", r)

        self.assertIsInstance(r["path_issue"], bool)
        self.assertIsInstance(r["conflict"], bool)

    def test_check_python3(self):
        reg = registry.load()
        res = checker.check_tool("python3", reg["python3"])

        self.assertTrue(res["installed"])
        self.assertIsNotNone(res["version"])
        self.assertFalse(res["conflict"])
        self.assertFalse(res["path_issue"])
