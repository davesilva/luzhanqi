import logging

DEBUGGING = True


def assert_all_probabilities_sum_to_one(board):
    """
    Board ->

    Asserts that assert_piece_probabilities_sum_to_one holds
    for all pieces on the given board.

    """

    if not DEBUGGING:
        return

    for piece in board.pieces_list:
        assert_piece_probabilities_sum_to_one(piece)


def assert_piece_probabilities_sum_to_one(piece):
    """
    Piece ->

    Asserts that the sum of all rank probabilities for the
    given piece is 1.

    """

    if not DEBUGGING:
        return

    prob_sum = sum(piece.probability(rank) for rank in piece.ranks())
    if not prob_sum == 1:
        log = logging.getLogger("probability")
        log.error("Probability sum for %s is %s" % (str(piece), str(prob_sum)))
        assert(False)
