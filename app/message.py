import app.board as board
import re

# Regex of ref->player messages
INVALID_SETUP_RE = "(Invalid Board Setup)$"
IM_PIECE_MOVE_RE = "Piece not movable"
IM_NO_PIECE_RE = "No Piece"
IM_FT_INVALID_RE = "From To Invalid"
IM_LOC_INVALID_RE = "Location Invalid"
INVALID_MOVE_RE = "(Invalid Board Move) (%s|%s|%s|%s)$" % \
                   (IM_PIECE_MOVE_RE, IM_NO_PIECE_RE,     \
                    IM_FT_INVALID_RE, IM_LOC_INVALID_RE)
POSITION_RE = "([A-E]1[0-2]|[A-E][1-9])"
PLAYER_RE = "(1|2)"
RCV_MOVE_RE = "%s %s %s (move|win|loss|tie)$" % \
              (POSITION_RE, POSITION_RE, PLAYER_RE)
FLAG_RE = "F %s$" % (POSITION_RE)
WINNING_RE = "(1|2|No) Victory$"

""" 
Mappings of regex of ref->player messages to their thunked Message 
subclass instances. 
"""
RE_MAP ={
         INVALID_SETUP_RE: (lambda match: ErrorMessage(match.group(1))),
         INVALID_MOVE_RE: (lambda match: ErrorMessage(match.group(2))),
         RCV_MOVE_RE: (lambda match: MoveMessage(pos_to_tuple(match.group(1)), \
                                                 pos_to_tuple(match.group(2)), \
                                                 int(match.group(3)),          \
                                                 match.group(4))),
         FLAG_RE: (lambda match: FlagMessage(pos_to_tuple(match.group(1)))),
         WINNING_RE: (lambda match: WinningMessage(match.group(1)))
        }


def pos_to_tuple(pos):
    """
    String -> Tuple 
    
    Converts a position on the board to a tuple.

    >>> pos_to_tuple("A1")
    (0,0)
    
    """
    return (ord(pos[0]) - ord('A'), int(pos[1:]) - 1)


def deserialize(packet):
    """
    String -> [Subclass_of Message]

    Finds a matching of the given message to a regex in RE_MAP and 
    returns the corresponding instance of a subclass of Message.

    Raises a BadMessageException if the given message does not match 
    any regexes in RE_MAP. 

    >>> deserialize("A6 B6 1 win")
    MoveMessage((0,5) (1,5) 1 "win")

    """
    for rx in RE_MAP:
        match = re.search(rx, packet)
        if match:
           return RE_MAP[rx](match)

    raise BadMessageException("Invalid Message from the Ref: %s"%(packet))



class BadMessageException(Exception):

    def __init__(self, s):
        """
        String -> BadMessageException

        Constructs that initializes instance variable self.value with
        the given board 

        Precondition: A message is sent from the ref to the player
        that does not match any regexes in RE_MAP

        """
        self.value = s


    def __str__(self):
        """
        . -> String

        Produce a readable official string representation of the instance's 
        value. 

        >>>> print(BadMessageException("Invalid Message from the Ref"))
        Invalid Message from Ref

        Note: it is same as print("'Invalid Message from the Ref'")

        """
        return repr(self.value)



# Message super class
class Message(object):

    def __init__(self):
        """
        . -> .

        Function does nothing

        """
        pass


    def __str__(self):
        """
        . -> .

        Function does nothing

        """
        pass


    def serialize(self):
        """
        . -> .

        Function does nothing

        """
        pass


class InitMessage(Message):
    
    def __init__(self, aboard):
        """
        Board -> InitMessage

        Constructor that initializes instance variable self.board with
        the given board. 

        """
        self.board = aboard


    def serialize(self):
        """
        . -> String

        Returns a string representing the board

        """
        return self.board.serialize()


class MoveMessage(Message):

    def __init__(self, posfrom, posto, player=1, movetype=""):
        """
        Tuple Tuple Integer String -> MoveMessage

        Constructor for ref to player message that initializes 
        instance variables self.posfrom, self.posto, self.player and 
        self.movetype with the given input

        Tuple Tuple -> MoveMessage

        Constructor for player to ref message that initializes instance
        variables self.posfrom and self.posto with the given input.

        """
        self.posfrom = posfrom
        self.posto = posto
        self.player = player
        self.movetype = movetype


    def serialize(self):
        """
        . -> String

        Returns a string representing the serialized MoveMessage

        >>> MoveMessage((1,4), (1,5)).serialize()
        "( B5 B6 )"

        >>> MoveMessage((2,2), (2,3), 1, "win")
        "( C3 C4 )"

        """
        p = self.posfrom
        t = self.posto
        base_char = ord('A')
        return "( %c%d %c%d )"%(base_char + p[0], p[1] + 1, \
                                base_char + t[0], t[1] + 1)


    def __str__(self):
        """
        . -> String

        Returns a human readable string representing a MoveMessage

        >>> print(MoveMessage((1,4) (1,5)))
        Move message: ( B5 B6 )

        >>> print(MoveMessage((2,2) (2,3), 1, "lose"))
        Move message: ( C3 C4 )

        """
        return "Move message: %s"%(self.serialize())


    def __eq__(self, obj):
        """
        . -> MoveMessage

        Checks if this message and the given MoveMessage are equal 
        by comparing the fields: posfrom, posto, player and movetype

        >>>> MoveMessage((1,4), (1,5)) == MoveMessage((1,4), (1,5))
        True

        >>>> MoveMessage((1,4), (1,5)) == MoveMessage((1,4), (1,5), 1, "win")
        False

        """
        return                              \
            self.posfrom == obj.posfrom and \
            self.posto == obj.posto and     \
            self.player == obj.player and   \
            self.movetype == obj.movetype



class FlagMessage(Message):
    def __init__(self, pos):
        """
        Tuple -> FlagMessage

        Constructor for a flag message that initializes self.pos with the
        given position that indicates the location of the flag. 

        """
        self.pos = pos


    def __str__(self):
        """
        . -> String 

        Returns a human readable string representing a FlagMessage

        >>> print(FlagMessage((3,0))
        Flag position: ( D1 )

        """
        base_char = ord('A')
        p = self.pos
        return "Flag position: ( %c%d )"%(base_char + p[0], p[1] + 1)


    def __eq__(self, obj):
        """
        . -> FlagMessage

        Checks if this FlagMessage is equal to the given FlagMessage
        by comparing their instance variables for equality.

        """
        return self.pos == obj.pos



class WinningMessage(Message):
    
    def __init__(self, result):
        """
        String -> WinningMessage

        Constructor for a winning message that initializes self.result
        with the given result that indicates the winner of the game. 

        """
        self.result = result


    def __str__(self):
        """
        . -> String

        Returns a human readable string representing WinningMessage

        >>> print(WinningMessage("1"))
        1

        >>> print(WinningMessage("No"))
        No

        """
        return "Player %s"%(result)


    def __eq__(self, obj):
        """
        . -> WinningMessage

        Checks if this WinningMessage is equal to the given WinningMessage
        by comparing their instance variables for equality. 

        """
        return self.result == obj.result



class ErrorMessage(Message):
    def __init__(self, error):
        """
        String -> ErrorMessage

        Constructor for an error message that initializes self.error
        with the given string that indicates the error incurred.

        """
        self.error = error


    def __eq__(self, obj):
        """
        Checks if this ErrorMessage is equal to the given ErrorMessage
        by comparing their instance variables for equality.

        """
        return self.error == obj.error


    def __str__(self):
        """
        Returns a human readable string representing the ErrorMessage

        >>> print(ErrorMessage("Piece not movable"))
        Piece not movable

        """
        return self.error
