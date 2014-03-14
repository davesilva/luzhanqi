import unittest
from app.board import Board, Piece, Owner, Rank


class TestRank(unittest.TestCase):
    def test_same_ranks_are_equal(self):
        r1 = Rank('1')
        r2 = Rank('1')
        self.assertTrue(r1 == r2)


class TestPiece(unittest.TestCase):
    def test_create_rank_with_set(self):
        p = Piece((0, 0), Owner.PLAYER, set([Rank('1')]))
        self.assertEqual(p.serialize(), "( A1 1 )")

    def test_create_rank_with_one_rank(self):
        p = Piece((0, 0), Owner.PLAYER, Rank('1'))
        self.assertEqual(p.serialize(), "( A1 1 )")

    def test_same_pieces_are_equal(self):
        p1 = Piece((0, 1), Owner.PLAYER, Rank('1'))
        p2 = Piece((0, 1), Owner.PLAYER, Rank('1'))
        self.assertTrue(p1 == p2)

    def test_pieces_with_different_owners_not_equal(self):
        p1 = Piece((0, 1), Owner.PLAYER, Rank('1'))
        p2 = Piece((0, 1), Owner.OPPONENT, Rank('1'))
        self.assertFalse(p1 == p2)


class TestBoard(unittest.TestCase):
    def test_serialize_empty_board(self):
        self.assertEqual(Board().serialize(), "(  )")

    def test_serialize_board_with_piece(self):
        p = Piece((0, 1), Owner.PLAYER, Rank('1'))
        b = Board().place_piece(p)
        self.assertEqual(b.serialize(), "( ( A2 1 ) )")

    def test_piece_at_with_no_piece(self):
        b = Board()
        self.assertEqual(b.piece_at((0, 0)), None)

    def test_piece_at_with_piece(self):
        p = Piece((0, 0), Owner.PLAYER, Rank('1'))
        b = Board().place_piece(p)
        self.assertEqual(b.piece_at((0, 0)), p)

    def test_move_piece(self):
        p = Piece((0, 0), Owner.PLAYER, Rank('1'))
        b = Board().place_piece(p).move_piece((0, 0), (0, 1))
        self.assertTrue(isinstance(b.piece_at((0, 1)), Piece))
        self.assertEqual(b.piece_at((0, 0)), None)

if __name__ == '__main__':
    unittest.main()
