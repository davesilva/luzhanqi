import unittest
from app.board import Board, Piece, Owner, Rank, PieceNotFoundException
from app.message import *
from fractions import Fraction


p1 = Piece((0, 1), Owner.PLAYER, Rank('1'))
p2 = Piece((0, 0), Owner.PLAYER, Rank('4'))
opponent = Piece((1,2), Owner.OPPONENT, Rank('8'))
flag = Piece((0, 1), Owner.PLAYER, Rank('F'))
landmine = Piece((0, 0), Owner.PLAYER, Rank('L'))


class TestRank(unittest.TestCase):

    def test_same_ranks_are_equal(self):
        r1 = Rank('1')
        r2 = Rank('1')
        self.assertTrue(r1 == r2)


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
        b = Board().initialize_opponent_pieces()
        p_before = b.piece_at((0, 6))
        p_after = p_before.exclude_ranks({Rank('1'), Rank('2'), Rank('3'),
                                          Rank('4'), Rank('5'), Rank('6')})

        self.assertEqual(p_after.probability(Rank('1')), 0)
        self.assertEqual(p_after.probability(Rank('9')), Fraction('1/13'))


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
        self.assertRaises(PieceNotFoundException, b.move_piece, (2,1), (3,2))

    def test_remove_piece(self):
        p = Piece((0, 0), Owner.PLAYER, Rank('1'))
        mt = Board()
        b = Board().place_piece(p).remove_piece((0, 0))
        self.assertEqual(mt.serialize(), b.serialize())

    def test_remove_piece_nonexistant(self):
        p = Piece((0, 0), Owner.PLAYER, Rank('1'))
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
        b = Board().initialize_opponent_pieces()
        hq_piece = b.piece_at((1, 11))
        back_piece = b.piece_at((0, 11))
        middle_piece = b.piece_at((0, 9))
        front_piece = b.piece_at((0, 6))

        self.assertEqual(hq_piece.probability(Rank('F')), Fraction('1/2'))
        self.assertEqual(hq_piece.probability(Rank('L')), Fraction('1/6'))
        self.assertEqual(hq_piece.probability(Rank('B')), Fraction('1/24'))
        self.assertEqual(hq_piece.probability(Rank('1')), Fraction('21/456'))
        self.assertEqual(hq_piece.probability(Rank('7')), Fraction('14/456'))
        self.assertEqual(hq_piece.probability(Rank('8')), Fraction('7/456'))
        self.assertEqual(front_piece.probability(Rank('8')), Fraction('1/19'))

        self.assertEqual(back_piece.probability(Rank('F')), Fraction('0'))
        self.assertEqual(middle_piece.probability(Rank('L')), Fraction('0'))

if __name__ == '__main__':
    unittest.main()
