import unittest
from file_handler import *

class TestFileHandler(unittest.TestCase):
    def testDirectory(self):
        self.assertEquals(
            file_request_handler("file:///Users/"),
            ".\n..\n.localized\nShared\nvarshajoshi\nGuest\nmehuljoshi\n")
    
    def testFile(self):
        self.assertEquals(
            file_request_handler("file:///Users/mehuljoshi/workspace/icefox/html.txt"),
            "<body>\n    <h1>Hi</h1>\n</body>")
