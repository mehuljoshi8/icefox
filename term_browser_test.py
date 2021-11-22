# The terminal browser tester tests the functionality for the first
# implementation of the browser which uses the terminal as the primary gui

import unittest
import browser

class TestBrowserV1(unittest.TestCase):
    # tests for the data scheme
    # examples of using data are
    # data:text/html,[my random stuff]
    def test_data_scheme(self):
        s = "data:text/html,&lt;div&gt;"
        expected = "<div>"
        actual = browser.data_request_handler(s)
        self.assertEqual(expected, actual)
        
if __name__ == "__main__":
    unittest.main()