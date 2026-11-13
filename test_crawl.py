import unittest
from crawl import normalize_url

test_cases = [
    "www.boot.dev/blog/path",
    "https://www.boot.dev/blog/path",
    "http://www.boot.dev/blog/path",
    "www.boot.dev/blog/path/",
    "http://www.boot.dev/blog/path",
    "https://www.boot.dev/blog/path/"
]


class TestCrawl(unittest.TestCase):
    def test_normalize_url(self):
        for test in test_cases:
            input_url = test
            actual = normalize_url(input_url)
            expected = "www.boot.dev/blog/path"
            self.assertEqual(actual, expected, f"failed for {input_url}")


if __name__ == "__main__":
    unittest.main()
