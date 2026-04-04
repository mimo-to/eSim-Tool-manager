import unittest
from src import platform_mgr

class TestPlatform(unittest.TestCase):
    def test_get_os(self):
        os_name = platform_mgr.get_os()
        self.assertIsInstance(os_name, str)
        self.assertIn(os_name, ["linux", "windows", "macos"])
