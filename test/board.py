import unittest
from app.board import Board, Owner, PieceNotFoundException
from app.piece import Piece
from app.rank import Rank
from app.message import *
from fractions import Fraction


opponent_board = Board().initialize_opponent_pieces()
p1 = Piece((0, 1), Owner.PLAYER, Rank('1'))
p2 = Piece((0, 0), Owner.PLAYER, Rank('4'))
opponent = Piece((1, 2), Owner.OPPONENT, Rank('8'))
flag = Piece((0, 1), Owner.PLAYER, Rank('F'))
landmine = Piece((0, 0), Owner.PLAYER, Rank('L'))


class TestBoard(unittest.TestCase):
    def test_serialize_empty_board(self):
        self.assertEqual(Board().serialize(), "(  )")

    def test_serialize_board_with_piece(self):
        b = Board().place_piece(p1)
        self.assertEqual(b.serialize(), "( ( A2 1 ) )")

    def test_piece_at_with_no_piece(self):
        b = Board()
        self.assertEqual(b.piece_at((0, 0)), None)

    def test_piece_at_with_piece(self):
        b = Board().place_piece(p1)
        self.assertEqual(b.piece_at((0, 1)), p1)

    def test_move_piece(self):
        b = Board().place_piece(p2).move_piece((0, 0), (0, 1))
        self.assertTrue(isinstance(b.piece_at((0, 1)), Piece))
        self.assertEqual(b.piece_at((0, 0)), None)

    def test_move_piece_nonexistant(self):
        p = Piece((0, 0), Owner.PLAYER, Rank('1'))
        b = Board().place_piece(p).move_piece((0, 0), (0, 1))
        self.assertRaises(PieceNotFoundException, b.move_piece, (2, 1), (3, 2))

    def test_remove_piece(self):
        p = Piece((0, 0), Owner.PLAYER, Rank('1'))
        mt = Board()
        b = Board().place_piece(p).remove_piece((0, 0))
        self.assertEqual(mt.serialize(), b.serialize())

    def test_remove_piece_nonexistant(self):
        mt = Board()
        self.assertRaises(PieceNotFoundException, mt.remove_piece, (0, 0))

    def test_is_space_blocked_for(self):
        b = Board().place_piece(p2)
        self.assertTrue(b.is_space_blocked_for((0, 0), Owner.PLAYER))
        self.assertFalse(b.is_space_blocked_for((0, 0), Owner.OPPONENT))
        self.assertFalse(b.is_space_blocked_for((0, 1), Owner.PLAYER))
        self.assertFalse(b.is_space_blocked_for((0, 1), Owner.OPPONENT))

    def test_iterate_pieces_with_one_piece(self):
        b = Board().place_piece(p2)
        self.assertEqual(len(list(b.iterate_pieces(Owner.PLAYER))), 1)
        self.assertEqual(len(list(b.iterate_pieces(Owner.OPPONENT))), 0)

    def test_iterate_pieces_with_more_pieces(self):
        b = Board().place_piece(p2).place_piece(p1)
        self.assertEqual(len(list(b.iterate_pieces(Owner.PLAYER))), 2)
        self.assertEqual(len(list(b.iterate_pieces(Owner.OPPONENT))), 0)

    def test_iterate_pieces_with_opponent_pieces(self):
        b = Board().place_piece(p1).place_piece(p2).place_piece(opponent)
        self.assertEqual(len(list(b.iterate_pieces(Owner.PLAYER))), 2)
        self.assertEqual(len(list(b.iterate_pieces(Owner.OPPONENT))), 1)

    def test_iterate_moves_for_piece_simple(self):
        b = Board().place_piece(p2)
        self.assertEqual(list(b.iterate_moves_for_piece(p2)), [(0, 1), (1, 0)])

    def test_iterate_moves_for_piece_forbids_moving_onto_blocked_spaces(self):
        b = Board().place_piece(p2).place_piece(p1)
        self.assertEqual(list(b.iterate_moves_for_piece(p2)), [(1, 0)])

    def test_iterate_moves_for_piece_forbids_attacking_in_camp(self):
        b = Board().place_piece(p1).place_piece(opponent)
        self.assertEqual(len(list(b.iterate_moves_for_piece(p1))), 3)
        self.assertFalse((1, 2) in list(b.iterate_moves_for_piece(p1)))
        self.assertTrue((0, 1) in list(b.iterate_moves_for_piece(opponent)))

    def test_iterate_all_moves_with_one_piece(self):
        b = Board().place_piece(p2)

        expected = [((0, 0), m) for m in b.iterate_moves_for_piece(p2)]
        self.assertEqual(list(b.iterate_all_moves(Owner.PLAYER)), expected)

    def test_iterate_all_moves_with_multiple_pieces(self):
        b = Board().place_piece(p2).place_piece(p1)

        expected = ([((0, 0), m) for m in b.iterate_moves_for_piece(p2)] +
                    [((0, 1), m) for m in b.iterate_moves_for_piece(p1)])
        self.assertEqual(list(b.iterate_all_moves(Owner.PLAYER)), expected)

    def test_iterate_all_moves_with_both_players(self):
        p3 = Piece((0, 1), Owner.OPPONENT, Rank('4'))
        b = Board().place_piece(p2).place_piece(p3)

        expected_for_player = [((0, 0), m)
                               for m in b.iterate_moves_for_piece(p2)]
        expected_for_opponent = [((0, 1), m)
                                 for m in b.iterate_moves_for_piece(p3)]
        self.assertEqual(list(b.iterate_all_moves(Owner.PLAYER)),
                         expected_for_player)
        self.assertEqual(list(b.iterate_all_moves(Owner.OPPONENT)),
                         expected_for_opponent)

    def test_iterate_all_moves_with_landmine_and_flag(self):
        b = Board().place_piece(landmine).place_piece(flag)
        self.assertEqual(list(b.iterate_all_moves(Owner.PLAYER)), [])

    def test_initialize_opponent_pieces(self):
        hq_piece = opponent_board.piece_at((1, 11))
        back_piece = opponent_board.piece_at((0, 11))
        middle_piece = opponent_board.piece_at((0, 9))
        front_piece = opponent_board.piece_at((0, 6))

        self.assertEqual(hq_piece.probability(Rank('F')), Fraction('1/2'))
        self.assertEqual(hq_piece.probability(Rank('L')), Fraction('1/6'))
        self.assertEqual(hq_piece.probability(Rank('B')), Fraction('1/24'))
        self.assertEqual(hq_piece.probability(Rank('1')), Fraction('21/456'))
        self.assertEqual(hq_piece.probability(Rank('7')), Fraction('14/456'))
        self.assertEqual(hq_piece.probability(Rank('8')), Fraction('7/456'))
        self.assertEqual(front_piece.probability(Rank('8')), Fraction('1/19'))

        self.assertEqual(back_piece.probability(Rank('F')), Fraction('0'))
        self.assertEqual(middle_piece.probability(Rank('L')), Fraction('0'))

    def test_set_flag(self):
        b = opponent_board.set_flag((1, 11))
        flag = b.piece_at((1, 11))

        self.assertEqual(flag.probability(Rank('L')), Fraction('0'))
        self.assertEqual(flag.probability(Rank('F')), Fraction('1'))

if __name__ == '__main__':
    unittest.main()
