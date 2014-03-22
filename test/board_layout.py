import unittest
import app.board_layout as layout
from app.position import * 

class TestBoardLayout(unittest.TestCase):
    def test_adjacent_spaces_are_adjacent(self):
        self.assertTrue(layout.is_adjacent(Position(0, 0), Position(0, 1)))
        self.assertTrue(layout.is_adjacent(Position(0, 1), Position(0, 0)))
        self.assertTrue(layout.is_adjacent(Position(0, 1), Position(1, 2)))
        self.assertTrue(layout.is_adjacent(Position(1, 7), Position(2, 8)))
        self.assertTrue(layout.is_adjacent(Position(4, 11), Position(3, 11)))

    def test_non_adjacent_spaces_are_not_adjacent(self):
        self.assertFalse(layout.is_adjacent(Position(0, 0), Position(2, 3)))
        self.assertFalse(layout.is_adjacent(Position(4, 11), Position(3, 10)))

    def test_space_not_adjacent_with_itself(self):
        self.assertFalse(layout.is_adjacent(Position(0, 0), Position(0, 0)))
        self.assertFalse(layout.is_adjacent(Position(3, 4), Position(3, 4)))

    def test_iterate_adjacent_length(self):
        self.assertEqual(len(list(layout.iterate_adjacent(Position(0, 0)))), 2)
        self.assertEqual(len(list(layout.iterate_adjacent(Position(2, 2)))), 4)
        self.assertEqual(len(list(layout.iterate_adjacent(Position(1, 2)))), 8)
        self.assertEqual(len(list(layout.iterate_adjacent(Position(2, 5)))), 6)


if __name__ == '__main__':
    unittest.main()
