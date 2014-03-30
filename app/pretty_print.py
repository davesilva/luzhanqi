# -*-coding: utf8-*-

import app.board as board
import app.logging_config as logconfig
from app.config import Config
import sys, os

# Borders #
VERT_L = "│"
HORZ_L = "─"
CUPLEFT = "┌"
CUPRIGHT = "┐"
CDWNLEFT = "└"
CDWNRIGHT = "┘"
T_UP = "┬"
T_DOWN = "┴"
WRDRIGHT = "├"
WRDLEFT = "┤"
CROSS = "┼"

WIDTH = 4

topline = CUPLEFT + (HORZ_L * WIDTH + T_UP) * 11 + HORZ_L * WIDTH + CUPRIGHT
midline = WRDRIGHT + (HORZ_L * WIDTH + CROSS) * 11 + HORZ_L * WIDTH + WRDLEFT
botline = CDWNLEFT + (HORZ_L * WIDTH + T_DOWN) * 11 + HORZ_L * WIDTH + CDWNRIGHT

config = Config()


def print_for_player(s, player):
    if player == config.turn:
        return "\033[34m%s\033[0m" % s
    else:
        return "\033[31m%s\033[0m" % s


def print_piece(p):
    if p.owner == board.Owner.PLAYER:
        r = next(iter(p.ranks))
        r = "\033[34m%s\033[0m" % (str(r))
    else:
        r = "\033[31mX\033[0m"
    return r


def print_board(aboard):
    drawn = ""

    drawn += "  " + topline + "\n"
    pieces = aboard.pieces_list

    for i in range(5):
        for j in range(12):
            s = " "
            if (j == 0):
                drawn += chr(ord("A") + i) + " "
                drawn += VERT_L
            for p in pieces:
                if p.position == (i, j):
                    s = print_piece(p)
            if(len(s) > WIDTH):
                juster = len(s) + WIDTH - 1
            else:
                juster = WIDTH
            drawn += s.center(juster, " ") + VERT_L
            if (j == 11) and (i != 4):
                drawn += "\n" + "  " + midline + "\n"

    drawn += "\n" + "  " + botline + "\n"
    drawn += "    1    2    3    4    5    6    7    8    9    10   11   12\n"
    return drawn


def draw_message(message):
    if os.path.exists(logconfig.logs_dir):
        fname = "player%d" % (config.turn) + ".draw"
        fp = open(logconfig.logs_dir + "/" + fname, "a")
        message_str = "%s -> %s" % (str(message), message.movetype)
        fp.write(print_for_player(message_str, message.player) + "\n")
        fp.close()


def draw_board(aboard):
    if os.path.exists(logconfig.logs_dir):
        buf = print_board(aboard)
        fname = "player%d" % (config.turn) + ".draw"
        fp = open(logconfig.logs_dir + "/" + fname, "a")
        debug_board = " | ".join([str(p) for p in aboard.pieces_list])
        fp.write(debug_board + "\n" + buf + "\n")
        fp.write("-" * 80 + "\n")
        fp.close()
