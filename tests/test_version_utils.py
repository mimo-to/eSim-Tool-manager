import unittest
from src.version_utils import is_outdated

class TestVersionUtils(unittest.TestCase):

    def test_equal_versions(self):
        self.assertFalse(is_outdated("37", "37"))

    def test_lower_version(self):
        self.assertTrue(is_outdated("36", "37"))

    def test_higher_version(self):
        self.assertFalse(is_outdated("38", "37"))

    def test_multi_segment_newer(self):
        self.assertFalse(is_outdated("3.11.9", "3.8.0"))

    def test_multi_segment_older(self):
        self.assertTrue(is_outdated("3.7.0", "3.8.0"))

    def test_empty_installed(self):
        self.assertFalse(is_outdated("", "37"))

    def test_empty_required(self):
        self.assertFalse(is_outdated("37", ""))
