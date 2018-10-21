import unittest
from rcs_latexdiff import utils

contentWithComments = """
Lorem ipsum 1
% lorem ipsum 2
lorem ipsum 3 % lorem ipsum
\% lorem ipsum 4
lorem ipsum 5
"""

contentWithoutComments = """
Lorem ipsum 1
lorem ipsum 3 
\% lorem ipsum 4
lorem ipsum 5
"""

class TestUtils(unittest.TestCase):
  def test_remove_latex_comments(self):
    parsedContent = utils.remove_latex_comments(contentWithComments)
    self.assertEqual(parsedContent, contentWithoutComments)

if __name__ == '__main__':
    unittest.main()