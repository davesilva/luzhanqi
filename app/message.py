import app.board as board

INVALID_SETUP_REGEX = "(Invalid Board Move)"
IM_PIECE_MOVE = "Piece not movable"
IM_NO_PIECE = "No Piece"
IM_FT_INVALID = "From To Invalid"
IM_LOC_INVALID = "Location Invalid"
INVALID_MOVE_REGEX = "(Invalid Board Move)( )(%s|%s|%s|%s)" % (IM_PIECE_MOVE, IM_NO_PIECE, IM_FT_INVALID, IM_LOC_INVALID)




# Message super class
class SendMessage(object):

    def __init__(self):
        pass
    def __str__(self):
        pass
    def serialize(self):
        pass




class InitMessage(SendMessage):
    # -> Message
    # takes a Board, initializes the instance var
    def __init__(self, aboard):
        self.board = aboard
     
    # -> String
    # returns a string representing the serialized board
    def serialize(self):
        return self.board.serialize()

class MoveMessage(SendMessage):
    # -> Message
    # takes two tuples, and initializes the instance vars
    def __init__(self, posfrom, posto):
        self.posfrom = posfrom
        self.posto = posto

    # -> String
    # returns a string representing the serialized board
    def serialize(self):
        p = self.posfrom
        t = self.posto
        base_char = ord('A')
        return "( %c%d %c%d )"%(base_char + p[0], p[1] + 1, base_char + t[0], t[1] + 1)



class ReceiveMessage(object):

    def __init__(self, msgstring):
        self.msgstring = msgstring

    def __str__(self):
        pass

    def deserialize(self):
        rawstring = self.msgstring;
        if(rawstring == ""):
            try()




class Error(Message):
    # -> Message
    def __init__(self, error):
        self.error = error





