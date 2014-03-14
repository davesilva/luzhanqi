import app.board as board
import re

INVALID_SETUP_RE = "(Invalid Board Setup)"
IM_PIECE_MOVE_RE = "Piece not movable"
IM_NO_PIECE_RE = "No Piece"
IM_FT_INVALID_RE = "From To Invalid"
IM_LOC_INVALID_RE = "Location Invalid"
INVALID_MOVE_RE = "(Invalid Board Move) (%s|%s|%s|%s)" % (IM_PIECE_MOVE_RE, IM_NO_PIECE_RE, IM_FT_INVALID_RE, IM_LOC_INVALID_RE)
POSITION_RE = "([A-E][0-9][0-9]?)" 
PLAYER_RE = "([1|2])"
RCV_MOVE_RE = "%s %s %s (move|win|loss|tie)$" % (POSITION_RE, POSITION_RE, PLAYER_RE)
FLAG_RE = "F %s" % (POSITION_RE)
WINNING_RE = "([1|2|No]) Victory"

RE_MAP ={
            INVALID_SETUP_RE: (lambda match: Error(match.group(1))),
            INVALID_MOVE_RE: (lambda match: Error(match.group(2))),
            RCV_MOVE_RE: (lambda match: MoveMessage(posToTuple(match.group(1)), \
                                                    posToTuple(match.group(2)), \
                                                    match.group(3), \
                                                    match.group(4))),
            FLAG_RE: (lambda match: FlagMessage(posToTuple(match.group(1)))),
            WINNING_RE: (lambda match: WinningMessage(match.group(1)))
        }

# String -> Tuple
def posToTuple(pos):
    (ord(pos[0]) - ord('A'), int(pos[1:]))

# returns an instance of the subclass 
def deserialize(packet):
    for rx in RE_MAP:
        match = re.search(rx, packet)
        if match:
           return RE_MAP[rx](match)


# Message super class
class Message(object):

    def __init__(self):
        pass
    def __str__(self):
        pass
    def serialize(self):
        pass
        
    
class InitMessage(Message):
    # -> Message
    # takes a Board, initializes the instance var
    def __init__(self, aboard):
        self.board = aboard
     
    # -> String
    # returns a string representing the serialized board
    def serialize(self):
        return self.board.serialize()


class MoveMessage(Message):
    # -> Message
    # takes two tuples, and initializes the instance vars
    def __init__(self, posfrom, posto, player=1, movetype=""):
        self.posfrom = posfrom
        self.posto = posto
        self.player = player
        self.movetype = movetype


    # -> String
    # returns a string representing the serialized board
    def serialize(self):
        p = self.posfrom
        t = self.posto
        base_char = ord('A')
        return "( %c%d %c%d )"%(base_char + p[0], p[1] + 1, base_char + t[0], t[1] + 1)
 

class FlagMessage(Message):
    # Tuple -> Message
    def __init__(self, pos):
        self.pos = pos
    

class WinningMessage(Message):
    # String -> Message
    def __init__(self, result):
        self.result = result


class Error(Message):
    # String -> Message
    def __init__(self, error):
        self.error = error


