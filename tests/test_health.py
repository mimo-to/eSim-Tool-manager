import unittest
from src import health

class TestHealth(unittest.TestCase):
    def test_compute_all_ok(self):
        data = [
            {"installed": True, "required": True},
            {"installed": True, "required": False}
        ]
        res = health.compute(data)
        self.assertEqual(res["score"], 100)

    def test_compute_none(self):
        data = [
            {"installed": False, "required": True},
            {"installed": False, "required": False}
        ]
        res = health.compute(data)
        self.assertTrue(res["score"] < 50)
