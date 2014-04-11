"""
A Position is a NamedTuple Position(row, col) where
row is 0 - 11 and col is 0 - 4.

"""
import collections

Position = collections.namedtuple('Position', ['row', 'col'])


def pos_to_str(pos):
    """
    Position -> str

    Convert a Position to a string
    """
    return chr(pos[0] + ord('A')) + str((pos[1] + 1))


def str_to_pos(s):
    """
    str -> Position

    Convert a str to a Position
    """
    return Position(ord(s[0]) - ord('A'), int(s[1:]) - 1)
