import app.board as board


PATH = "app/template_board"


# -> Board
# parse "./board" and return a board
def parse_board():
    b = board.Board()
    fp = open(PATH, "r")

    raw = fp.read()
    raw = raw.split()

    for y, row in enumerate(raw):
        for x, rank in enumerate(row):
            if rank != ".":
                b = b.place_piece(board.Piece((x, y),
                                  board.Owner.PLAYER,
                                  board.Rank(rank)))

    return b
