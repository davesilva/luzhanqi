import unittest
from app.message import *

class TestMessage(unittest.TestCase):

    def test_pos_to_tuple(self):
        t1 = pos_to_tuple("A1")
        t2 = (0, 0)
        t3 = pos_to_tuple("B3")
        self.assertEqual(t1, t2)
        self.assertNotEqual(t1, t3)

    """
    Invalid Board Setup
    """
    def testDeserializeInvalidSetup(self):
        d1 = deserialize("Invalid Board Setup")
        d2 = ErrorMessage("Invalid Board Setup")
        self.assertTrue(d1 == d2)

    """
    Invalid Board Move <moveErrorType>
    <moveErrorType> ::= "Piece not movable" | "No Piece" | "From To Invalid" | "Location Invalid"
    """
    def testDeserializeInvalidMove1(self):
        d1 = deserialize("Invalid Board Move Piece not movable")
        d2 = ErrorMessage("Piece not movable")
        self.assertEqual(d1, d2)

    def testDeserializeInvalidMove2(self):
        d1 = deserialize("Invalid Board Move No Piece")
        d2 = ErrorMessage("No Piece")
        self.assertEqual(d1, d2)

    def testDeserializeInvalidMove3(self):
        d1 = deserialize("Invalid Board Move From To Invalid")
        d2 = ErrorMessage("From To Invalid")
        self.assertEqual(d1, d2)

    def testDeserializeInvalidMove4(self):
        d1 = deserialize("Invalid Board Move Location Invalid")
        d2 = ErrorMessage("Location Invalid")
        self.assertEqual(d1, d2)

    """
    <position 1> <position 2> <player> <movetype>
    <player> ::= "1" | "2"
    <movetype> ::= "move" | "win" | "loss" | "tie"
    """ 

    def testDeserializeReceiveMove1(self):
        d1 = deserialize("A1 A1 1 move")
        d2 = MoveMessage((0,0), (0,0), 1, "move")
        self.assertEqual(d1, d2)

    def testDeserializeReceiveMove2(self):
        d1 = deserialize("A2 E3 2 win")
        d2 = MoveMessage((0,1), (4,2), 2, "win")
        self.assertEqual(d1, d2)

    def testDeserializeReceiveMove3(self):
        self.assertRaises(BadMessageException, deserialize, "Z1 A2 1 move")

    def testDeserializeReceiveMove4(self):
        self.assertRaises(BadMessageException, deserialize, "A1 F2 1 move")

    """
    F <position>
    """

    def testDeserializeFlagMessage1(self):
        d1 = deserialize("F A2")
        d2 = FlagMessage((0, 1))
        self.assertEqual(d1, d2)

    def testDeserializeFlagMessage2(self):
        self.assertRaises(BadMessageException, deserialize, "F E13")

    """
    <winningPlayer> Victory
    <winningPlayer> ::= "1" | "2" | "No"
    """

    def testDeserializeWinningMessage(self):
        d1 = deserialize("1 Victory")
        d2 = WinningMessage("1")
        self.assertEqual(d1, d2)

    def testDeserializeWinningMessage(self):
        d1 = deserialize("No Victory")
        d2 = WinningMessage("No")
        self.assertEqual(d1, d2)


if __name__ == '__main__':
    unittest.main()
