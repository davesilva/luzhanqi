from optparse import OptionParser
import sys
import re

# http://rubular.com/r/pyvahYlvvU
TIME_REGEX = "^(\d*\.?\d+)m?s$"

parser = OptionParser()
parser.add_option("-g", "--go", dest="turn", help="specify which player should go first (1 or 2)")
parser.add_option("-t", "--time/move", dest="time", help="specify the time per move")

class Config:
    def __init__(self):
        (options, args) = parser.parse_args()

        match = re.search(TIME_REGEX, options.time or "")

        if (options.turn != "1" and options.turn != "2") or (not match):
            sys.stderr.write(parser.format_help())
            quit()

        self.turn = options.turn
        self.time = match.group(1)

    def get_turn(self):
        return self.turn

    def get_time(self):
        return self.time
