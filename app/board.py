import copy
import logging
import app.board_layout as board_layout
from fractions import Fraction, gcd

"""
A Position is a tuple of Numbers (row, column)
"""

log = logging.getLogger("board")


class Rank:
    """
    Instance variables:
    Char rank 

    """

    def __init__(self, rank):
        """
        Char -> Rank

        Constructs a Rank with the given rank 

        """
        self.rank = rank

    def __str__(self):
        """
        -> String

        Returns a human readable string of this Rank 

        >>> print(Rank('L'))
        L

        """
        return self.rank

    def __eq__(self, other):
        """
        -> Rank

        Checks if this is equal to the given Rank by comparing
        self.rank for equality. 

        """
        return self.rank == other.rank

    def __hash__(self):
        """
        -> Number

        Hashes this instance. 

        """
        return hash(self.rank)


class Owner:

    PLAYER = 0
    OPPONENT = 1

class PieceNotFoundException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

class Board:
    """
    Instance variables:
    [Listof Piece] pieces_list

    """

    def __init__(self, pieces_list=[]):
        """
        [Listof Piece] -> Board

        Constructs a Board with the specified list of pieces. 

        """
        self.pieces_list = pieces_list

    def place_piece(self, piece):
        """
        Piece -> Board

        Adds the given piece to this Board for initial setup. 

        """
        new_list = copy.copy(self.pieces_list)
        new_list.append(piece)
        return Board(new_list)

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
            raise PieceNotFoundException("Cannot move piece from ( %c%d )" \
                    %(ord('A') + src[0], src[1] + 1))

    def piece_at(self, position):
        """
        Position -> (Piece | None)

        Returns the piece at the given position. 

        """
        return next(
            (p for p in self.pieces_list if p.position == position), None)

    def is_space_blocked_for(self, position, owner):
        """
        Position Owner -> Boolean 

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
        Owner -> [Generator_of Piece]

        Returns a generator for all pieces owned by the given player

        """
        i = iter(self.pieces_list)
        return filter(lambda p: p.owner == owner, i)

    def iterate_moves_for_piece(self, piece):
        """
        Piece -> [Generator_of Position]

        Returns a generator for all possible moves that can
        be made by the given piece. A move is a position that the given
        piece can consider for relocation or attack.

        """
        # TODO: if given piece is an engineer, also need to consider
        # railway positions i.e. not just adjacent pieces
        # The paths to these positions should also not be blocked by
        # the player/opponent's pieces.

        if piece.is_stationary():
            return iter([])

        i = board_layout.iterate_adjacent(piece.position)
        # Make sure we exclude blocked spaces
        i = filter(lambda m: not self.is_space_blocked_for(m, piece.owner), i)
        return i

    def iterate_all_moves(self, owner):
        """
        Owner -> [Generator_of (Position, Position)] 

        Returns a generator for all possible moves that can be made
        by the given player. A move is a tuple of positions 
        (position_from, position_to). The piece at position_from belongs to
        the given player and is allowed to relocate to position_to or attack
        a piece that is currently present at position_to

        """
        for piece in self.iterate_pieces(owner):
            for move in self.iterate_moves_for_piece(piece):
                yield (piece.position, move)

    def serialize(self):
        """
        -> String

        Serialize this Board. 

        """
        return ("( " +
                " ".join([p.serialize() for p in self.pieces_list]) + " )")

    def dump_debug_board(self):
        log.debug(" | ".join([str(p) for p in self.pieces_list]))

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

    def update(self, msg):
        """
        MoveMessage -> Board 

        Move pieces if a "move" or "win" is indicated by the given
        MoveMessage, otherwise if a "loss" or "tie" is indicated, 
        then remove pieces appropriately. 

        """
        move_type = msg.movetype
        if move_type == "move":
            return self.move_piece(msg.posfrom, msg.posto)
        if move_type == "win":
            without_loser = self.remove_piece(msg.posto)
            return without_loser.move_piece(msg.posfrom, msg.posto)
        if move_type == "loss":
            return self.remove_piece(msg.posfrom)
        if move_type == "tie":
            return self.remove_piece(msg.posfrom).remove_piece(msg.posto)

    def initialize_opponent_pieces(self):
        """
        -> Board

        Adds all of the opponent's pieces to the board in their
        initial configuration. The initial probabilities are
        set as follows:

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
        board = self

        for x in range(0, 5):
            for y in range(6, 12):
                # Camps do not have pieces in them, so skip over them
                if board_layout.is_camp((x, y)):
                    continue

                p = {}  # dictionary of probabilities

                # Pieces outside the headquarters cannot be the flag
                if board_layout.is_headquarters((x, y)):
                    p[Rank('F')] = Fraction(1, 2)
                else:
                    p[Rank('F')] = Fraction(0)

                # Landmines cannot be outside of the back two rows
                if y in range(10, 12):
                    p[Rank('L')] = Fraction(1, 3) * (1 - p[Rank('F')])
                else:
                    p[Rank('L')] = Fraction(0)

                # Bombs cannot be in the front row
                if y in range(7, 12):
                    p[Rank('B')] = (Fraction(1, 10) *
                                    (1 - p[Rank('F')] - p[Rank('L')]))
                else:
                    p[Rank('B')] = Fraction(0)

                # Probability that the piece is not Flag, Landmine or Bomb
                p_numeric_rank = (1 - p[Rank('F')]
                                    - p[Rank('L')]
                                    - p[Rank('B')])

                # Any square can potentially contain a piece 1-9
                for r in range(1, 4):
                    p[Rank(str(r))] = Fraction(3, 19) * p_numeric_rank
                for r in range(4, 8):
                    p[Rank(str(r))] = Fraction(2, 19) * p_numeric_rank
                for r in range(8, 10):
                    p[Rank(str(r))] = Fraction(1, 19) * p_numeric_rank

                piece = Piece((x, y), Owner.OPPONENT, p)
                board = board.place_piece(piece)

        return board


class Piece:
    """
    Instance variables:
    Position                  position
    Owner                     owner
    Dictionary(Rank, Fraction)  ranks

    The ranks Dictionary is a mapping from a Rank to a
    probability. Probabilities are represented as a python
    Fraction.

    """

    def __init__(self, position, owner, ranks):
        """
        Position Owner Rank|Dictionary(Rank, Fraction) -> Piece

        Constructs an instance of Piece initialized with its position,
        owner and a dictionary that maps all possible ranks to the
        probability of this piece having that rank. Alternatively,
        ranks can be a single rank, in which case the probability
        of that rank will be 1 and all others will be 0.

        """
        # Number tuple (row, column)
        self.position = position
        # Owner object
        self.owner = owner

        # If ranks is a single Rank rather than a dictionary, convert
        # it into a dictionary where the probability of this piece
        # having that rank is 1.0
        if isinstance(ranks, Rank):
            self.probabilities = {ranks: 1}
        else:
            self.probabilities = ranks

    def move(self, new_posn):
        """
        Position -> Piece

        Returns a hard copy of this instance with a changed position. 

        """
        return Piece(new_posn, self.owner, self.probabilities)

    def adjust_probabilities(self, ranks):
        """
        Dictionary(Rank, Fraction) -> Piece

        Returns a Piece with the Rank probabilities adjusted according
        to the given ranks Dictionary.

        """
        new_prob = {}
        for rank, prob in ranks:
            if rank in self.ranks:
                self.denominator = self.denominator - prob
                if self.ranks[rank] - prob > 0:
                    new_prob[rank] = self.probability(rank) - prob

        return Piece(self.position, self.owner, new_prob)

    def is_stationary(self):
        """
        -> Boolean 

        Returns true if this piece cannot be moved i.e. if it is a flag
        or a landmine or positioned at a headquarter. 

        """
        return (board_layout.is_headquarters(self.position) or
                self.probability(Rank('L')) + self.probability(Rank('F')) == 1)

    def probability(self, rank):
        """
        -> Fraction

        Returns the probability that this piece has the given Rank.

        """
        if rank in self.probabilities:
            return self.probabilities[rank]
        else:
            return 0

    def __eq__(self, piece):
        """
        Piece -> Boolean 

        Checks if the given Piece is the same as this instance
        """
        return (isinstance(piece, Piece) and
                self.probabilities == piece.probabilities and
                self.position == piece.position and
                self.owner == piece.owner)

    def __str__(self):
        (x, y) = self.position

        if self.owner == Owner.PLAYER:
            owner = "P"
        else:
            owner = "O"

        ranks = "[%s]" % ", ".join([str(rank) for rank in self.probabilities])
        return "%c%d %c %s" % (ord('A') + x, y + 1, owner, ranks)

    def serialize(self):
        """
        -> String

        Serialize this Piece

        """
        x = self.position[0]
        y = self.position[1]
        (x, y) = self.position
        rank = str(next(iter(self.probabilities)))
        return "( %c%d %c )" % (ord('A') + x, y + 1, rank)
