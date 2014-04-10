from app.board import Board, Rank, Owner
from app.board_layout import *

# Note that we are ONLY considering movable pieces i.e. no landmines or flags
# May need to consider the case of a movable piece placed in hq?
RANK_WORTH = {Rank('1'):2, Rank('2'):2, Rank('3'):3, Rank('4'):4, Rank('5'):5, 
	Rank('6'):6, Rank('7'):7, Rank('8'):8, Rank('9'):9, Rank('B'):5}

RANK_INIT_AMT = {Rank('1'):3, Rank('2'):3, Rank('3'):3, Rank('4'):2, 
	Rank('5'):2, Rank('6'):2, Rank('7'):2, Rank('8'):1, Rank('9'):1, 
	Rank('B'):2}

# Factors should all up to 1
# TODO Dictionary: weight to functions 
# TODO Make 2 dictionaries (player 1 and player 2)
WORTH_FACTOR = 0.3
LOSING_PIECE_FACTOR = 0.3
COMMONALITY_FACTOR = 0.05
PROXIMITY_FACTOR = 0.25
BRAVE_FACTOR = 0.1


def action_value(board, src, dest):
	"""
	Board Position Position -> Number
	Returns the value of an attack from 0 - 1

	TODO: VALUE OF MOVES
	"""

	if board.piece_at(dest) == None:
		return 0.5
	else:
		(win, loss, tie) = prob_win_loss_tie(board, src, dest)
		value = \
			WORTH_FACTOR * piece_worth(board, src) + \
			LOSING_PIECE_FACTOR * (loss + tie) + \
			COMMONALITY_FACTOR * piece_commonality_rating(board, src) #+ \
			#PROXIMITY_FACTOR * proximity_rating(board, src, dest) + \
			#BRAVE_FACTOR * brave_rating() 
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
	return RANK_WORTH[rank] / (max - min)

def prob_win_loss_tie(board, src, dest):
	"""
	Board Position Position -> (Number, Number, Number)

	Returns probability of winning, losing and tying

	"""
	player_piece = board.piece_at(src)
	opponent_piece = board.piece_at(dest)
	return player_piece.expected_attack_outcome(opponent_piece)


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
	return rating / (max - min)


def proximity_rating(board, src, dest):
	"""
	Board Position Position -> Number
	Produces a proximity rating of destination to 
	flag and destination to a camp 
	"""
	max = 11
	min = 0
	if is_camp(dest) : 
		return (dest[0] + 1) / (max - min)
	else:
		return dest[0] / (max - min)

def tradeoff_rating(board, pos):
	"""
	Board Position -> Number
	Determines how brave the piece can be by 
	comparing how many pieces have a higher or
	equal worth than it
	"""
	piece = board.piece_at(pos)
	rank = piece.get_rank()
	subj_worth = RANK_WORTH[rank]
	lop = board.iterate_pieces(Owner.PLAYER)
	higher_worth_pieces = filter(lambda p: RANK_WORTH[p.get_rank()] \
		                                   >= subj_worth, lop)
	num_higher_worth_pieces = len(higher_worth_pieces)
	return num_higher_worth_pieces / (max - min)











