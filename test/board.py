import unittest
from app.board import Board, Piece, Owner, Rank


class TestRank(unittest.TestCase):
    def test_same_ranks_are_equal(self):
        r1 = Rank('1')
        r2 = Rank('1')
        self.assertTrue(r1 == r2)


class TestPiece(unittest.TestCase):
    def test_create_rank_with_set(self):
        p = Piece((0, 0), Owner.PLAYER, frozenset([Rank('1')]))
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

    def test_is_stationary_with_stationary_pieces(self):
        p = Piece((0, 0), Owner.PLAYER, Rank('F'))
        self.assertTrue(p.is_stationary())
        p = Piece((0, 0), Owner.PLAYER, {Rank('F'), Rank('L')})
        self.assertTrue(p.is_stationary())

    def test_is_stationary_with_piece_in_headquarters(self):
        p = Piece((1, 0), Owner.PLAYER, Rank('1'))
        self.assertTrue(p.is_stationary())

    def test_is_stationary_with_non_stationary_pieces(self):
        p = Piece((0, 0), Owner.PLAYER, Rank('1'))
        self.assertFalse(p.is_stationary())
        p = Piece((0, 0), Owner.PLAYER, {Rank('F'), Rank('4')})
        self.assertFalse(p.is_stationary())


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

    def test_is_space_blocked_by(self):
        p = Piece((0, 0), Owner.PLAYER, Rank('1'))
        b = Board().place_piece(p)
        self.assertTrue(b.is_space_blocked_by((0, 0), Owner.PLAYER))
        self.assertFalse(b.is_space_blocked_by((0, 0), Owner.OPPONENT))
        self.assertFalse(b.is_space_blocked_by((0, 1), Owner.PLAYER))
        self.assertFalse(b.is_space_blocked_by((0, 1), Owner.OPPONENT))

    def test_iterate_pieces_with_one_piece(self):
        p1 = Piece((0, 0), Owner.PLAYER, Rank('8'))
        b = Board().place_piece(p1)
        self.assertEqual(len(list(b.iterate_pieces(Owner.PLAYER))), 1)
        self.assertEqual(len(list(b.iterate_pieces(Owner.OPPONENT))), 0)

    def test_iterate_pieces_with_more_pieces(self):
        p1 = Piece((0, 0), Owner.PLAYER, Rank('8'))
        p2 = Piece((0, 1), Owner.PLAYER, Rank('2'))
        b = Board().place_piece(p1).place_piece(p2)
        self.assertEqual(len(list(b.iterate_pieces(Owner.PLAYER))), 2)
        self.assertEqual(len(list(b.iterate_pieces(Owner.OPPONENT))), 0)

    def test_iterate_pieces_with_opponent_pieces(self):
        p1 = Piece((0, 0), Owner.PLAYER, Rank('8'))
        p2 = Piece((0, 1), Owner.PLAYER, Rank('2'))
        p3 = Piece((1, 1), Owner.OPPONENT, Rank('2'))
        b = Board().place_piece(p1).place_piece(p2).place_piece(p3)
        self.assertEqual(len(list(b.iterate_pieces(Owner.PLAYER))), 2)
        self.assertEqual(len(list(b.iterate_pieces(Owner.OPPONENT))), 1)

    def test_iterate_moves_for_piece_simple(self):
        p = Piece((0, 0), Owner.PLAYER, Rank('8'))
        b = Board().place_piece(p)
        self.assertEqual(list(b.iterate_moves_for_piece(p)), [(0, 1), (1, 0)])

    def test_iterate_moves_for_piece_forbids_moving_onto_blocked_spaces(self):
        p1 = Piece((0, 0), Owner.PLAYER, Rank('8'))
        p2 = Piece((0, 1), Owner.PLAYER, Rank('4'))
        b = Board().place_piece(p1).place_piece(p2)
        self.assertEqual(list(b.iterate_moves_for_piece(p1)), [(1, 0)])

    def test_iterate_moves_for_piece_forbids_attacking_in_camp(self):
        p1 = Piece((0, 1), Owner.PLAYER, Rank('8'))
        p2 = Piece((1, 2), Owner.OPPONENT, Rank('4'))
        b = Board().place_piece(p1).place_piece(p2)
        self.assertEqual(len(list(b.iterate_moves_for_piece(p1))), 3)
        self.assertFalse((1, 2) in list(b.iterate_moves_for_piece(p1)))
        self.assertTrue((0, 1) in list(b.iterate_moves_for_piece(p2)))

    def test_iterate_all_moves_with_one_piece(self):
        p = Piece((0, 0), Owner.PLAYER, Rank('8'))
        b = Board().place_piece(p)

        expected = [((0, 0), m) for m in b.iterate_moves_for_piece(p)]
        self.assertEqual(list(b.iterate_all_moves(Owner.PLAYER)), expected)

    def test_iterate_all_moves_with_multiple_pieces(self):
        p1 = Piece((0, 0), Owner.PLAYER, Rank('8'))
        p2 = Piece((0, 1), Owner.PLAYER, Rank('4'))
        b = Board().place_piece(p1).place_piece(p2)

        expected = ([((0, 0), m) for m in b.iterate_moves_for_piece(p1)] +
                    [((0, 1), m) for m in b.iterate_moves_for_piece(p2)])
        self.assertEqual(list(b.iterate_all_moves(Owner.PLAYER)), expected)

    def test_iterate_all_moves_with_both_players(self):
        p1 = Piece((0, 0), Owner.PLAYER, Rank('8'))
        p2 = Piece((0, 1), Owner.OPPONENT, Rank('4'))
        b = Board().place_piece(p1).place_piece(p2)

        expected_for_player = [((0, 0), m)
                               for m in b.iterate_moves_for_piece(p1)]
        expected_for_opponent = [((0, 1), m)
                                 for m in b.iterate_moves_for_piece(p2)]
        self.assertEqual(list(b.iterate_all_moves(Owner.PLAYER)),
                         expected_for_player)
        self.assertEqual(list(b.iterate_all_moves(Owner.OPPONENT)),
                         expected_for_opponent)

    def test_iterate_all_moves_with_landmine_and_flag(self):
        p1 = Piece((0, 0), Owner.PLAYER, Rank('L'))
        p2 = Piece((0, 1), Owner.PLAYER, Rank('F'))
        b = Board().place_piece(p1).place_piece(p2)

        self.assertEqual(list(b.iterate_all_moves(Owner.PLAYER)), [])


if __name__ == '__main__':
    unittest.main()
