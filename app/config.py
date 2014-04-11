from optparse import OptionParser
import sys
import re

# http://rubular.com/r/pyvahYlvvU
TIME_REGEX = "^(\d*\.?\d+)m?s$"

parser = OptionParser()
parser.add_option("-g",
                  "--go",
                  dest="turn",
                  help="specify which player should go first (1 or 2)")

parser.add_option("-t",
                  "--time/move",
                  dest="time",
                  help="specify the time per move")


class Config:
    """
    Instance variables:
    float time
    int player

    """
    def __init__(self):
        """
        -> Config

        Create a new Config module, parsing command line arguments
        
        """
        (options, args) = parser.parse_args()

        match = re.search(TIME_REGEX, options.time or "")

        if (options.turn != "1" and options.turn != "2") or (not match):
            sys.stderr.write(parser.format_help())
            quit(1)

        if (re.search("ms", options.time)):
            self.time = int(float(match.group(1)))
        else:
            self.time = int(1000 * float(match.group(1)))

        self.turn = int(options.turn)

    def get_turn(self):
        """
        -> int
       
        Get this player's turn (1 if the player should go first, 2 if second)
        
        """
        return self.turn

    def get_time(self):
        """
        -> int
        
        Get the time per move in milliseconds
        
        """
        return self.time
