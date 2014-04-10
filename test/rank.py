import unittest
from app.rank import Rank


class TestRank(unittest.TestCase):

    def test_same_ranks_are_equal(self):
        r1 = Rank('1')
        r2 = Rank('1')
        self.assertTrue(r1 == r2)

if __name__ == '__main__':
    unittest.main()
