import unittest
import app.board_layout as layout


class TestBoardLayout(unittest.TestCase):
    def test_adjacent_spaces_are_adjacent(self):
        self.assertTrue(layout.adjacent((0, 0), (0, 1)))
        self.assertTrue(layout.adjacent((0, 1), (0, 0)))
        self.assertTrue(layout.adjacent((0, 1), (1, 2)))
        self.assertTrue(layout.adjacent((1, 7), (2, 8)))
        self.assertTrue(layout.adjacent((4, 11), (3, 11)))

    def test_non_adjacent_spaces_are_not_adjacent(self):
        self.assertFalse(layout.adjacent((0, 0), (2, 3)))
        self.assertFalse(layout.adjacent((4, 11), (3, 10)))

    def test_space_not_adjacent_with_itself(self):
        self.assertFalse(layout.adjacent((0, 0), (0, 0)))
        self.assertFalse(layout.adjacent((3, 4), (3, 4)))


if __name__ == '__main__':
    unittest.main()
