# A Position is a tuple of Numbers (row, column)

import copy

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
    def move_piece(self, piece, dest):
        # List without piece
        new_list = filter(lambda p: p != piece, self.pieces_list)

        # Add piece to list
        new_list.append(piece.move(dest))

        return Board(new_list)

    def serialize(self):
        return "( " + " ".join(map(lambda x: x.serialize(), self.pieces_list)) + " )"


class Piece:

    # Number Position -> Piece
    def __init__(self, rank, position):
        # Integer from 1 - 12
        self.rank = rank
        # Number tuple (row, column)
        self.position = position

    # Position -> Piece
    def move(self, new_posn):
        return Piece(self.rank, new_posn)

    # Piece -> Boolean
    # Check if the given piece is the same as this instance
    def __eq__(self, piece):
        return self.rank == piece.rank and self.position == piece.position


    def serialize(self):
        x = self.position[0]
        y = self.position[1]
        return "( %c%d %c )"%(ord('A') + x, y + 1, self.rank)





