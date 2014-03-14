_WIDTH = 5
_HEIGHT = 12
_HEADQUARTERS_LOCATIONS = [(0, 1), (0, 3)]
_CAMP_LOCATIONS = [(1, 2), (1, 4), (2, 3), (3, 2), (3, 4)]
_board_graph = {}


class Space:
    REGULAR, CAMP, HEADQUARTERS = range(0, 3)

    def __init__(self, on_railroad=False, space_type=REGULAR):
        self.space_type = space_type
        self.on_railroad = on_railroad
        self.adjacent = set()

    def __iter__(self):
        return iter(self.adjacent)

    def add(self, v):
        self.adjacent.add(v)


# Position Position -> Boolean
def is_adjacent(v1, v2):
    return (v2 in _board_graph[v1])


# Position -> Boolean
def is_camp(p):
    return _board_graph[p].space_type == Space.CAMP


# Position -> Boolean
def is_headquarters(p):
    return _board_graph[p].space_type == Space.HEADQUARTERS


def iterate_adjacent(position):
    return iter(_board_graph[position])


def _connect(v1, v2):
    (x1, y1) = v1
    (x2, y2) = v2
    if (x1 in range(0, _WIDTH) and x2 in range(0, _WIDTH) and
            y1 in range(0, _HEIGHT) and y2 in range(0, _HEIGHT)):

        _board_graph[v1].add(v2)
        _board_graph[v2].add(v1)


def _connect_mirrored(v1, v2):
    _connect(v1, v2)

    (x1, y1) = v1
    (x2, y2) = v2

    _connect((x1, _HEIGHT - y1 - 1), (x2, _HEIGHT - y2 - 1))


def _connect_cardinals(v1):
    (x, y) = v1
    for v2 in [(x-1, y), (x, y-1), (x+1, y), (x, y+1)]:
        _connect_mirrored(v1, v2)


def _connect_diagonals(v1):
    (x, y) = v1
    for v2 in [(x-1, y-1), (x-1, y+1), (x+1, y-1), (x+1, y+1)]:
        _connect_mirrored(v1, v2)


def _connect_all(v):
    _connect_cardinals(v)
    _connect_diagonals(v)


# Set up the board
for x in range(0, _WIDTH):
    for y in range(0, _HEIGHT):
        if ((x, y) in _CAMP_LOCATIONS or
                (x, _HEIGHT - y) in _CAMP_LOCATIONS):
            _board_graph[(x, y)] = Space(space_type=Space.CAMP)
        elif ((x, y) in _HEADQUARTERS_LOCATIONS or
                (x, _HEIGHT - y) in _HEADQUARTERS_LOCATIONS):
            _board_graph[(x, y)] = Space(space_type=Space.HEADQUARTERS)
        else:
            _board_graph[(x, y)] = Space()

# Connect all of the spaces in the cardinal directions
for y in range(0, 6):
    for x in range(0, _WIDTH):
        # (1, 5) and (3, 5) are not connected
        if y is not 5 or x in [0, 2, 4]:
            _connect_cardinals((x, y))

# Connect the camps to all adjacent spaces
for v in _CAMP_LOCATIONS:
    _connect_all(v)