# A Position is a tuple of Numbers (row, column)
import copy
import app.board_layout as board_layout


class Rank:

    def __init__(self, rank):
        self.rank = rank

    def __str__(self):
        return self.rank

    def __eq__(self, other):
        return self.rank == other.rank

    def __hash__(self):
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

    def __init__(self, pieces_list=[]):
        self.pieces_list = pieces_list

    # Piece Position -> Board
    # Add piece to the board for initial setup
    def place_piece(self, piece):
        new_list = copy.copy(self.pieces_list)
        new_list.append(piece)
        return Board(new_list)

    # Position Position -> Board
    def move_piece(self, src, dest):
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

    # Position -> (Piece|None)
    def piece_at(self, position):
        return next(
            (p for p in self.pieces_list if p.position == position), None)

    # Position Owner -> Boolean
    # Returns true if this space is blocked for the given player
    def is_space_blocked_by(self, position, owner):
        p = self.piece_at(position)
        # TODO: if a player move into an opponent's headquarters,
        # it may not move again
        if p is None:
            return False
        elif p.owner == owner:
            return True
        else:
            return board_layout.is_camp(position)

    # Owner -> Generator(Piece)
    # Returns a generator which returns all pieces owned by the given player
    def iterate_pieces(self, owner):
        i = iter(self.pieces_list)
        return filter(lambda p: p.owner == owner, i)

    # Piece -> Generator(Position)
    # Returns a generator which returns all possible moves that can be made
    # by that piece, where a move is a position that this piece can move to.
    def iterate_moves_for_piece(self, piece):
        if piece.is_stationary():
            return iter([])

        i = board_layout.iterate_adjacent(piece.position)
        # Make sure we exclude blocked spaces
        i = filter(lambda m: not self.is_space_blocked_by(m, piece.owner), i)
        return i

    # Owner -> Generator((Position, Position))
    # Returns generator which returns all possible moves that can be made
    # by the given player (where a move is a tuple of positions
    # (position_from, position_to)).
    def iterate_all_moves(self, owner):
        for piece in self.iterate_pieces(owner):
            for move in self.iterate_moves_for_piece(piece):
                yield (piece.position, move)

    def serialize(self):
        return ("( " +
                " ".join([p.serialize() for p in self.pieces_list]) + " )")


    # Position -> Board
    # remove the piece at pos
    def remove_piece(self, pos):
        piece = self.piece_at(pos)

        if piece is not None:
            # List without piece
            new_list = [p for p in self.pieces_list if p != piece]

            return Board(new_list)
        else:
            raise PieceNotFoundException("Cannot remove piece from ( %c%d )" \
                    %(ord('A') + pos[0], pos[1] + 1))

    # Message -> Board
    # delegates to the appropriate functions
    # move or delete 
    def update(self, msg):
        move_type = msg.movetype
        if move_type == "move":
            return self.move_piece(msg.posfrom, msg.posto)
        if move_type == "win":
            return self.move_piece(msg.posfrom, msg.posto)
        if move_type == "loss":
            return self.remove_piece(msg.posfrom)
        if move_type == "tie":
            return self.remove_piece(msg.posfrom).remove_piece(msg.posto)

class Piece:
    RANK_NAMES = [str(i) for i in range(1, 10)] + ['B', 'L', 'F']
    ALL_RANKS = frozenset([Rank(i) for i in RANK_NAMES])

    # Position Owner <ranks=Set(Rank)> -> Piece
    def __init__(self, position, owner, ranks=ALL_RANKS):
        # Number tuple (row, column)
        self.position = position
        # Owner object
        self.owner = owner
        # Set of all possible ranks
        if isinstance(ranks, Rank):
            self.ranks = frozenset([ranks])
        else:
            self.ranks = ranks

    # Position -> Piece
    def move(self, new_posn):
        return Piece(new_posn, self.owner, ranks=self.ranks)

    # -> Boolean
    # Returns true if the piece cannot be moved (it is a flag or landmine)
    def is_stationary(self):
        return (board_layout.is_headquarters(self.position) or
                len(self.ranks.difference({Rank('L'), Rank('F')})) == 0)

    # Piece -> Boolean
    # Check if the given piece is the same as this instance
    def __eq__(self, piece):
        return (isinstance(piece, Piece) and
                self.ranks == piece.ranks and
                self.position == piece.position and
                self.owner == piece.owner)

    def serialize(self):
        x = self.position[0]
        y = self.position[1]
        rank = str(next(iter(self.ranks)))
        return "( %c%d %c )" % (ord('A') + x, y + 1, rank)
