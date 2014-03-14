# A Position is a tuple of Numbers (row, column)
import copy


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
            return self

    # Position -> (Piece|None)
    def piece_at(self, position):
        return next(
            (p for p in self.pieces_list if p.position == position), None)

    def serialize(self):
        return ("( " +
                " ".join([p.serialize() for p in self.pieces_list]) + " )")


class Piece:
    RANK_NAMES = [str(i) for i in range(1, 10)] + ['B', 'L', 'F']
    ALL_RANKS = set([Rank(i) for i in RANK_NAMES])

    # Position Owner <ranks=Set(Rank)> -> Piece
    def __init__(self, position, owner, ranks=ALL_RANKS):
        # Number tuple (row, column)
        self.position = position
        # Owner object
        self.owner = owner
        # Set of all possible ranks
        if isinstance(ranks, Rank):
            self.ranks = set([ranks])
        else:
            self.ranks = ranks

    # Position -> Piece
    def move(self, new_posn):
        return Piece(new_posn, self.owner, ranks=self.ranks)

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
