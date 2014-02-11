
import board


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
