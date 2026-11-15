import unittest
from crawl import *

url_test_cases = [
    "www.boot.dev/blog/path",
    "https://www.boot.dev/blog/path",
    "http://www.boot.dev/blog/path",
    "www.boot.dev/blog/path/",
    "http://www.boot.dev/blog/path",
    "https://www.boot.dev/blog/path/"
]


class TestCrawl(unittest.TestCase):
    # tests for normalize url, uses test cases list above
    def test_normalize_url(self):
        for test in url_test_cases:
            input_url = test
            actual = normalize_url(input_url)
            expected = "www.boot.dev/blog/path"
            self.assertEqual(actual, expected, f"failed for {input_url}")

    # test suite for get_heading
    def test_get_heading_from_html_basic(self):
        input_body = "<html><body><h1>Test Title</h1></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_medium(self):
        input_body = "<html><body><h2>Test Title</h2></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_none(self):
        input_body = "<html><body><p>Test paragraph should fail</p></body></html>"
        actual = get_heading_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    # test suite for get first paragraph
    def test_get_first_paragraph_from_html_main_priority(self):
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_no_main(self):
        input_body = """<html><body>
                <p>Main paragraph.</p>
                <p>Second paragraph.</p>
                </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_no_p(self):
        input_body = """<html><body>
            <h1>Blank Body</h1>
            </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    # test suite for get url function
    # tests an absolute url present in input body
    def test_get_urls_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="https://crawler-test.com"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com"]
        self.assertEqual(actual, expected)

    # tests a relative url present in input body
    def test_get_urls_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="/image.png"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/image.png"]
        self.assertEqual(actual, expected)

    # tests multiple urls present in input body
    def test_get_urls_from_html_multiple(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
        <a href="https://crawler-test.com"><span>Boot.dev</span></a>
        <a href="https://crawler-test.com/image.png"><span>Boot.dev</span></a>
        <a href="/image.png"><span>Boot.dev</span></a>
        <a href="https://crawler-test.com/data"><span>Boot.dev</span></a>
        </body></html>"""
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com",
                    "https://crawler-test.com/image.png",
                    "https://crawler-test.com/image.png",
                    "https://crawler-test.com/data",]
        self.assertEqual(actual, expected)

    #test suite for image urls in input body
    def test_get_images_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="https://crawler-test.com/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_multiple(self):
        input_url = "https://crawler-test.com"
        input_body = """
            <html><body>
            <img src="/logo.png" alt="Logo">
            <img src="https://crawler-test.com/logo.png" alt="Logo">
            <img src="https://crawler-test.com/resources/noods.png" alt="secret">
            </body></html>
            """
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png",
            "https://crawler-test.com/logo.png",
            "https://crawler-test.com/resources/noods.png"]
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main()
