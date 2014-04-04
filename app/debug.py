def assert_all_probabilities_sum_to_one(board):
    """
    Board ->

    Asserts that assert_piece_probabilities_sum_to_one holds
    for all pieces on the given board.

    """

    for piece in board.pieces_list:
        assert_piece_probabilities_sum_to_one(piece)


def assert_piece_probabilities_sum_to_one(piece):
    """
    Piece ->

    Asserts that the sum of all rank probabilities for the
    given piece is 1.

    """

    assert(sum(piece.probability(rank) for rank in piece.ranks()) == 1)
