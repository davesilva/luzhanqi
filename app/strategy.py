from app.board import Board, Rank, Owner
from app.board_layout import *

# Note that we are ONLY considering movable pieces i.e. no landmines or flags
RANK_WORTH = {Rank('1'):2, Rank('2'):2, Rank('3'):3, Rank('4'):4, Rank('5'):5, 
	Rank('6'):6, Rank('7'):7, Rank('8'):8, Rank('9'):9, Rank('B'):5}

RANK_INIT_AMT = {Rank('1'):3, Rank('2'):3, Rank('3'):3, Rank('4'):2, 
	Rank('5'):2, Rank('6'):2, Rank('7'):2, Rank('8'):1, Rank('9'):1, 
	Rank('B'):2}

WORTH_FACTOR = 0.3
WINNING_FACTOR = 0.3
COMMONALITY_FACTOR = 0.05
PROXIMITY_FACTOR = 0.25
BRAVE_FACTOR = 0.1
MOVE_VALUE = 0

def action_value(board, src, dest):
	"""
	Board Position Position -> Number

	Returns the value of an attack from 0 - 1

	"""
	if board.piece_at(dest) == None:
		return MOVE_VALUE
	else:
		(win, loss, tie) = prob_win_loss_tie(board, src, dest)
		value = 10000
			#WORTH_FACTOR * piece_worth(board, src) + \
			#WINNING_FACTOR * win + \
			#COMMONALITY_FACTOR * piece_commonality_rating(board, src) + \
			#PROXIMITY_FACTOR * proximity_rating(board, src, dest) + \
			#BRAVE_FACTOR * brave_rating(board, src) 
		return value

def piece_worth(board, pos):
	"""
	Board Position -> Number

	Returns the hard-coded worth of a piece

	"""
	max = 9
	min = 2
	piece = board.piece_at(pos)
	rank = piece.get_rank()
	return (RANK_WORTH[rank] - min) / (max - min)


def piece_commonality_rating(board, src):
	"""
	Board Position -> Number

	Rates the commonality of the piece in the 
	board with ratio to their initial amount

	"""
	max = 2
	min = 2/3
	lop = board.iterate_pieces(Owner.PLAYER)
	src_piece = board.piece_at(src)
	src_rank = src_piece.get_rank()
	num_same_pieces = len(list(
		filter(lambda p: p.get_rank() == src_rank, lop)))
	num_orig = RANK_INIT_AMT[src_rank]

	current_present = num_same_pieces / num_orig 
	rarity_rating = num_orig / 3 # 3 is max init amt of most popular piece
	
	rating = rarity_rating + current_present
	return (rating - min)/ (max - min)


def proximity_rating(board, src, dest):
	"""
	Board Position Position -> Number

	Produces a proximity rating of destination to 
	flag and destination to a camp 

	"""
	max = 11
	min = 0
	if is_camp(dest) : 
		return (dest[1] + 1) / (max - min)
	else:
		return dest[1] / (max - min)


def brave_rating(board, pos):
	"""
	Board Position -> Number

	Determines how brave the piece can be by 
	comparing how many pieces have a higher or
	equal worth than it

	"""
	max = 18
	min = 0
	piece = board.piece_at(pos)
	rank = piece.get_rank()
	subj_worth = RANK_WORTH[rank]
	lop = board.iterate_pieces(Owner.PLAYER)
	higher_worth_pieces = list(
		filter(lambda p: \
			p.get_rank() != Rank('F') and \
			p.get_rank() != Rank('L') and \
			RANK_WORTH[p.get_rank()] >= subj_worth, lop))
	num_higher_worth_pieces = len(higher_worth_pieces)
	return num_higher_worth_pieces / (max - min)











