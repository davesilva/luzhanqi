import copy
import logging
import app.board_layout as board_layout
from app.piece import Piece, Owner
from app.rank import Rank


"""
A Position is a (row, col) where
row is 0 - 11 and col is 0 - 4.
"""

log = logging.getLogger("board")


class PieceNotFoundException(Exception):
    """
    Exception thrown when a piece is not found when trying to move
    a piece that does not exist.

    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        """
        -> str

        Returns the message causing exception

        """
        return repr(self.msg)


class Board:
    """
    Instance variables:
    list(Piece) pieces_list

    """

    def __init__(self, pieces_list=[]):
        """
        list(Piece) -> Board
        Constructs a Board with the specified list of pieces.

        """
        self.pieces_list = pieces_list

    def initialize_opponent_pieces(self):
        """
        -> Board

        Adds all of the opponent's pieces to the board in their
        initial configuration.

        """
        board = self

        for x in range(0, 5):
            for y in range(6, 12):
                (numerators, denominators) = _initial_probability_for((x, y))
                piece = Piece((x, y), Owner.OPPONENT, numerators, denominators)
                board = board.place_piece(piece)

        return board

    def serialize(self):
        """
        -> str

        Serialize this Board.

        """
        return ("( " +
                " ".join([p.serialize() for p in self.pieces_list]) + " )")

    def place_piece(self, piece):
        """
        Piece -> Board

        Adds the given piece to this Board for initial setup.

        """
        new_list = copy.copy(self.pieces_list)
        new_list.append(piece)
        return Board(new_list)

    def piece_at(self, position):
        """
        Position -> (Piece | None)

        Returns the piece at the given position.

        """
        return next(
            (p for p in self.pieces_list if p.position == position), None)

    def move_piece(self, src, dest):
        """
        Position Position -> Board

        Moves the piece at the src position to the dest position.

        """
        piece = self.piece_at(src)

        if piece is not None:
            # List without piece
            new_list = [p for p in self.pieces_list if p != piece]

            # Add piece to list
            new_list.append(piece.move(dest))

            return Board(new_list)
        else:
            raise PieceNotFoundException("Cannot move piece from ( %c%d )"
                                         % (ord('A') + src[0], src[1] + 1))

    def remove_piece(self, pos):
        """
        Position -> Board

        Removes the piece at the given position from the Board.

        """
        piece = self.piece_at(pos)

        if piece is not None:
            # List without piece
            new_list = [p for p in self.pieces_list if p != piece]
            return Board(new_list)
        else:
            raise PieceNotFoundException("Cannot remove piece from ( %c%d )"
                                         % (ord('A') + pos[0], pos[1] + 1))

    def is_space_blocked_for(self, position, owner):
        """
        Position Owner -> bool

        Checks if the given position
        - can be moved into by the given player
        - contains an opponent's piece that can be attacked but only if
        the given position is not a camp

        """

        p = self.piece_at(position)
        if p is None:
            return False
        elif p.owner == owner:
            return True
        else:
            return board_layout.is_camp(position)

    def iterate_pieces(self, owner):
        """
        Owner -> iter(Piece)

        Returns a generator for all pieces owned by the given player

        """
        i = iter(self.pieces_list)
        return filter(lambda p: p.owner == owner, i)

    def iterate_moves_for_piece(self, piece):
        """
        Piece -> iter(Position)

        Returns a generator for all possible moves that can
        be made by the given piece. A move is a position that the given
        piece can consider for relocation or attack.

        """
        if piece.is_stationary():
            return iter([])

        i = board_layout.iterate_adjacent(piece.position)
        # Make sure we exclude blocked spaces
        i = filter(lambda m: not self.is_space_blocked_for(m, piece.owner), i)
        return i

    def iterate_all_moves(self, owner):
        """
        Owner -> iter((Position, Position))

        Returns a generator for all possible moves that can be made
        by the given player. A move is a tuple of positions
        (position_from, position_to). The piece at position_from belongs to
        the given player and is allowed to relocate to position_to or attack
        a piece that is currently present at position_to

        """
        for piece in self.iterate_pieces(owner):
            for move in self.iterate_moves_for_piece(piece):
                yield (piece.position, move)

    def update_probabilities_from_attack(self, msg):
        """
        MoveMessage -> Board

        Updates all of the opponent_piece probabilities given an
        attack message.

        """
        attacking_piece = self.piece_at(msg.posfrom)
        defending_piece = self.piece_at(msg.posto)
        if attacking_piece.owner == Owner.OPPONENT:
            opponent_piece = attacking_piece
            player_piece = defending_piece
            attack_result = msg.movetype
        else:
            opponent_piece = defending_piece
            player_piece = attacking_piece
            if msg.movetype == "win":
                attack_result = "loss"
            elif msg.movetype == "loss":
                attack_result = "win"
            else:
                attack_result = "tie"

        ranks_to_exclude = []
        for rank in opponent_piece.ranks():
            if not (rank.attack_outcome(player_piece.get_rank()) ==
                    attack_result):
                ranks_to_exclude.append(rank)

        return self.exclude_ranks(opponent_piece, ranks_to_exclude)

    def exclude_ranks(self, piece, ranks):
        """
        Piece list(ranks) -> Board

        Excludes the given set of ranks for the given piece, returning
        the updated board.

        """
        new_piece = piece.exclude_ranks(ranks)
        new_list = []

        for p in self.pieces_list:
            if p == piece:
                new_list.append(new_piece)
            # TODO: Adjust probabilities for the other pieces
            # elif p.owner == piece.owner:
            #     new_list.append(p.adjust_probabilities(piece, ranks))
            else:
                new_list.append(p)

        return Board(new_list)

    def update(self, msg):
        """
        MoveMessage -> Board

        Move pieces if a "move" or "win" is indicated by the given
        MoveMessage, otherwise if a "loss" or "tie" is indicated,
        then remove pieces appropriately.

        """
        move_type = msg.movetype
        if move_type == "move":
            # If a piece moves, it cannot be a landmine
            piece = self.piece_at(msg.posfrom)
            updated = self.exclude_ranks(piece, {Rank('L')})
            return updated.move_piece(msg.posfrom, msg.posto)

        updated = self.update_probabilities_from_attack(msg)

        if move_type == "win":
            without_loser = updated.remove_piece(msg.posto)
            return without_loser.move_piece(msg.posfrom, msg.posto)
        if move_type == "loss":
            return updated.remove_piece(msg.posfrom)
        if move_type == "tie":
            return updated.remove_piece(msg.posfrom).remove_piece(msg.posto)

    def set_flag(self, position):
        """
        Position -> Board

        Indicates that the given position is the position of
        the opponent's flag.

        Precondition: The given position must be located in
                      a headquarters.

        """
        assert(board_layout.is_headquarters(position))

        piece = self.piece_at(position)
        return self.exclude_ranks(piece, set(piece.ranks()) - {Rank('F')})

    def dump_debug_board(self):
        """
        ->

        Logs the current state of the board.

        """
        log.debug(" | ".join([str(p) for p in self.pieces_list]))


def _initial_probability_for(position):
    """
    Position -> dict(Rank, Fraction)

    Returns the initial probability dictionary for a piece placed
    at the given position. Probabilities are calculated as follows:

    P(flag | is_headquarters) = 1/2
    P(flag | ~is_headquarters) = 0
    P(landmine | (y in range(10, 12))) = 1/3 * (1 - P(flag))
    P(landmine | ~(y in range(10, 12))) = 0
    P(bomb | (y in range(7, 12))) = 1/10 * (1 - (P(flag) + P(landmine)))
    P(bomb | ~(y in range(7, 12))) = 0
    P(1) = P(2) = P(3) = 3/19 * (1 - (P(flag) + P(landmine) + P(bomb)))
    P(4) = P(5) = P(6) = P(7) =
    2/19 * (1 - (P(flag) + P(landmine) + P(bomb)))
    P(8) = P(9) = 1/19 * (1 - (P(flag) + P(landmine) + P(bomb)))

    """
    (x, y) = position

    numerators = {}
    denominators = {}

    # Pieces outside the headquarters cannot be the flag
    if board_layout.is_headquarters(position):
        numerators[Rank('F')] = 1
        denominators[Rank('F')] = 2

    # Landmines cannot be outside of the back two rows
    if y in range(10, 12):
        numerators[Rank('L')] = 1
        denominators[Rank('L')] = 3

    # Bombs cannot be in the front row
    if y in range(7, 12):
        numerators[Rank('B')] = 1
        denominators[Rank('B')] = 8

    # Any square can potentially contain a piece 1-9
    for r in range(1, 4):
        numerators[Rank(str(r))] = 3
        denominators[Rank(str(r))] = 19
    for r in range(4, 8):
        numerators[Rank(str(r))] = 2
        denominators[Rank(str(r))] = 19
    for r in range(8, 10):
        numerators[Rank(str(r))] = 1
        denominators[Rank(str(r))] = 19

    return (numerators, denominators)
