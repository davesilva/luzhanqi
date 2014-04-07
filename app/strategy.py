import app.board as board
from app.board_layout import *

# Note that we are ONLY considering movable pieces i.e. no landmines or flags
# May need to consider the case of a movable piece placed in hq?
RANK_WORTH = {1:2, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8, 9:9, 'B':5}

RANK_INIT_AMT = {1:3, 2:3, 3:3, 4:2, 5:2, 6:2, 7:2, 8:1, 9:1, 'B':2}

# Factors should all up to 1
# TODO Dictionary: weight to functions 
# TODO Make 2 dictionaries (player 1 and player 2)
WORTH_FACTOR = 0.3
LOSING_PIECE_FACTOR = 0.3
COMMONALITY_FACTOR = 0.05
PROXIMITY_FACTOR = 0.25
BRAVE_FACTOR = 0.1
 
def get_rank(p):
	return next(iter(piece.ranks))


def action_value(board, src, dest):
	"""
	Board Position Position -> Number
	Returns the value of an action 
	"""

	if board.piece_at(dest) == None:
		(win, loss, tie) = (0, 0, 0)
	else:
		(win, loss, tie) = prob_win_loss_tie(board, src, dest)

	value = \
	WORTH_FACTOR * piece_worth(board, src) + \
	LOSING_PIECE_FACTOR * (loss + tie) + \
	COMMONALITY_FACTOR * piece_commonality_rating(board, src) + \
	PROXIMITY_FACTOR * proximity_rating(board, src, dest) + \
	BRACE_FACTOR * brave_rating() 

	# Consider these in ratios!

def piece_worth(board, pos):
	"""
	Board Position -> Number
	Returns the hard-coded worth of a piece
	"""
	max = 9
	min = 2
	piece = board.piece_at(pos)
	rank = get_rank(p)
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
	num_same_pieces = len(filter(lambda p: p == src, lop))
	rarity_rating = RANK_INIT_AMT[get_rank(p)] / 3
	rating = (num_same_pieces/num_orig) + num_same_pieces
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
	subj_worth = RANK_WORTH[get_rank(pos)]
	lop = board.iterate_pieces(Owner.PLAYER)
	higher_worth_pieces = filter(lambda p: RANK_WORTH[get_rank(p)] \
		                                   >= subj_worth, lop)
	num_higher_worth_pieces = len(higher_worth_pieces)
	return num_higher_worth_pieces / (max - min)











