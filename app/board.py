import copy
import logging
import app.board_layout as board_layout

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
        log.debug(" ".join([str(p) for p in self.pieces_list]))

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
            return self.move_piece(msg.posfrom, msg.posto)
        if move_type == "loss":
            return self.remove_piece(msg.posfrom)
        if move_type == "tie":
            return self.remove_piece(msg.posfrom).remove_piece(msg.posto)

    def initialize_opponent_pieces(self):
        """
        -> Board

        Adds all of the opponent's pieces to the board in their
        initial configuration.

        """
        board = self

        for x in range(0, 5):
            for y in range(6, 12):
                ranks = Piece.ALL_RANKS

                # Camps do not have pieces in them, so skip over them
                if board_layout.is_camp((x, y)):
                    continue

                # Pieces outside the headquarters cannot be the flag
                if not board_layout.is_headquarters((x, y)):
                    ranks = ranks - {Rank('F')}

                # Landmines cannot be outside of the back two rows
                if y in range(6, 10):
                    ranks = ranks - {Rank('L')}

                # Bombs cannot be in the front row
                if y is 6:
                    ranks = ranks - {Rank('B')}

                piece = Piece((x, y), Owner.OPPONENT, ranks)
                board = board.place_piece(piece)

        return board


class Piece:
    """
    Instance variables:
    Position    position
    Owner       owner
    Set(Ranks)  ranks

    """
    RANK_NAMES = [str(i) for i in range(1, 10)] + ['B', 'L', 'F']
    ALL_RANKS = frozenset([Rank(i) for i in RANK_NAMES])

    def __init__(self, position, owner, ranks=ALL_RANKS):
        """
        Position Owner <Set(Rank)> -> Piece

        Constructs an instance of Piece initialized with its position,
        owner and set of all possible ranks. 

        """
        # Number tuple (row, column)
        self.position = position
        # Owner object
        self.owner = owner
        # Set of all possible ranks
        if isinstance(ranks, Rank):
            self.ranks = frozenset([ranks])
        else:
            self.ranks = ranks

    def move(self, new_posn):
        """
        Position -> Piece

        Returns a hard copy of this instance with a changed position. 

        """
        return Piece(new_posn, self.owner, ranks=self.ranks)

 
    def is_stationary(self):
        """
        -> Boolean 

        Returns true if this piece cannot be moved i.e. if it is a flag
        or a landmine or positioned at a headquarter. 

        """
        return (board_layout.is_headquarters(self.position) or
                len(self.ranks.difference({Rank('L'), Rank('F')})) == 0)


    def __eq__(self, piece):
        """
        Piece -> Boolean 

        Checks if the given Piece is the same as this instance
        """
        return (isinstance(piece, Piece) and
                self.ranks == piece.ranks and
                self.position == piece.position and
                self.owner == piece.owner)

    def __str__(self):
        (x, y) = self.position

        if self.owner == Owner.PLAYER:
            owner = "P"
        else:
            owner = "O"

        ranks = "[%s]" % ", ".join([str(rank) for rank in self.ranks])
        return "( %c%d %c %s )" % (ord('A') + x, y + 1, owner, ranks)

    def serialize(self):
        """
        -> String

        Serialize this Piece

        """
        x = self.position[0]
        y = self.position[1]
        (x, y) = self.position
        rank = str(next(iter(self.ranks)))
        return "( %c%d %c )" % (ord('A') + x, y + 1, rank)
