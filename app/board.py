# A Position is a tuple of Numbers (row, column)

import copy 

class Board:
	def __init__(self):
		self.pieces_list = []

	def __init__(self, pieces_list):
		self.pieces_list = pieces_list

	# -> Board
	def get_empty_board():
		return Board()

	# Piece Position -> Board
	# Add piece to the board for initial setup
	def place_piece(self, piece):
		new_list = copy.deepcopy(self.pieces_list)
		new_list.add(piece)
		Board(new_list)

	# Position Position -> Board
	def move_piece(self, piece, dest)	
		# List without piece
		new_list = []
		for p in self.pieces_list
			if(!p.equals(piece))
				ins_p = copy.deepcopy(p)
				new_list.append(ins_p)
		# Add list to piece
		new_list.append(piece.move(dest))

    def serialize(self):
        return "( " + " ".join(map(lambda x: x.serialize(), self.pieces_list)) + " )"


class Piece:

	# Number Position -> Piece
	def __init__(self, rank, position):
		# Integer from 1 - 12
		self.rank = rank
		# Number tuple (row, column)
		self.position = 0

	# Position -> Piece
	def move(self, new_posn):
		return Position(self.rank, new_posn) 

	# Piece -> Boolean
	# Check if the given piece is the same as this instance
	def equal(self, piece):
		return (self.rank == piece.rank & self.tuple == pice.tuple)


    def serialize(self):
        x = self.position[0]
        y = self.position[1]
        return "( %c%d %c )"%(ord('A') + x, y + 1, self.rank)





