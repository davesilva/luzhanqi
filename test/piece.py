import unittest
from app.piece import Piece
from app.rank import Rank
from app.board import Board, Owner

opponent_board = Board().initialize_opponent_pieces()
p1 = Piece((0, 1), Owner.PLAYER, Rank('1'))
p2 = Piece((0, 0), Owner.PLAYER, Rank('4'))
opponent = Piece((1, 2), Owner.OPPONENT, Rank('8'))
flag = Piece((0, 1), Owner.PLAYER, Rank('F'))
landmine = Piece((0, 0), Owner.PLAYER, Rank('L'))


class TestPiece(unittest.TestCase):
    def test_create_rank_with_dict_of_ranks(self):
        p = Piece((0, 0), Owner.PLAYER, {Rank('1'): 1})
        self.assertEqual(p.serialize(), "( A1 1 )")

    def test_create_rank_with_one_rank(self):
        p = Piece((0, 0), Owner.PLAYER, Rank('1'))
        self.assertEqual(p.serialize(), "( A1 1 )")

    def test_same_pieces_are_equal(self):
        p1_copy = Piece((0, 1), Owner.PLAYER, Rank('1'))
        self.assertTrue(p1 == p1_copy)

    def test_pieces_with_different_owners_not_equal(self):
        self.assertFalse(p1 == p2)

    def test_is_stationary_with_stationary_pieces(self):
        self.assertTrue(flag.is_stationary())
        self.assertTrue(landmine.is_stationary())

    def test_is_stationary_with_piece_in_headquarters(self):
        p = Piece((1, 0), Owner.PLAYER, Rank('1'))
        self.assertTrue(p.is_stationary())

    def test_is_stationary_with_non_stationary_pieces(self):
        p_unknown_rank = Piece((0, 0), Owner.OPPONENT,
                               {Rank('F'): 1, Rank('4'): 1},
                               {Rank('F'): 2, Rank('4'): 1})
        self.assertFalse(p1.is_stationary())
        self.assertFalse(p_unknown_rank.is_stationary())

    def test_exclude_ranks_with_front_row_piece(self):
        p_before = opponent_board.piece_at((0, 6))
        p_after = p_before.exclude_ranks({Rank(str(r)) for r in range(1, 7)})

        self.assertEqual(p_after.probability(Rank('1')), 0)
        self.assertEqual(p_after.probability(Rank('7')), Fraction('1/2'))
        self.assertEqual(p_after.probability(Rank('8')), Fraction('1/4'))
        self.assertEqual(p_after.probability(Rank('9')), Fraction('1/4'))

if __name__ == '__main__':
    unittest.main()
