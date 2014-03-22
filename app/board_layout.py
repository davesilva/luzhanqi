""" 
A Position is a tuple of Numbers (row, column)
"""

from app.position import *

_WIDTH = 5
_HEIGHT = 12
_HEADQUARTERS_LOCATIONS = [(1, 0), (3, 0)]
_CAMP_LOCATIONS = [(1, 2), (1, 4), (2, 3), (3, 2), (3, 4)]
_board_graph = {}
_BOARD_FILE = "app/board_graph"
STATION, CAMP, HEADQUARTERS = range(0, 3)
TYPE_MAP = {"S": STATION,"C": CAMP, "H": HEADQUARTERS, "R": STATION}

class Space:
    """
    Instance variables:
    Integer            space_type
    Boolean            on_railroad
    [Set_of Position]  adjacent

    """

    def __init__(self, on_railroad, space_type, adjacent):
        """
        <Boolean> <Integer> -> Space

        Constructs an instance of Space.

        """
        self.space_type = space_type
        self.on_railroad = on_railroad
        self.adjacent = adjacent

    def __iter__(self):
        """
        -> [Generator_of Position]

        Returns a generator of positions that are adjacent to this space. 

        """
        return iter(self.adjacent)


def is_adjacent(v1, v2):
    """
    Position Position -> Boolean

    Checks if the given 2 positions are adjacent to each other. 

    """
    return (v2 in _board_graph[v1])

def is_camp(p):
    """
    Position -> Boolean 

    Checks if the give position is a camp

    """
    return _board_graph[p].space_type == CAMP

def is_headquarters(p):
    """
    Position -> Boolean

    Checks if the given position is a headquarter

    """
    return _board_graph[p].space_type == HEADQUARTERS


def iterate_adjacent(position):
    """
    Position -> [Generator_of Position]

    Returns a generator of positions that are adjacent to the given position.

    """
    return iter(_board_graph[position])

def generate_board():
    """
    ->

    Generates all positions and their connection for the board. 

    """
    b = open(_BOARD_FILE, "r").readlines()
    for line in b:
        raw = line.strip().split(" ")
        _board_graph[str_to_pos(raw[0])] = Space(                                        \
                                (raw[1] == "R"),                             \
                                TYPE_MAP[raw[1]],                            \
                                {str_to_pos(str_pos) for str_pos in raw[2:]})

generate_board()


