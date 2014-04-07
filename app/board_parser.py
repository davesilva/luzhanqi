import app.board as board


PATH = "app/template_board"


def parse_board():
    """
    -> Board
    
    Parse "./board" and return a Board instance
    
    """
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
