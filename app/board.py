import copy
import logging
import app.board_layout as board_layout
from fractions import Fraction, gcd

"""
A Position is a tuple of Numbers (row, column)
"""

log = logging.getLogger("board")


class Rank:
    """
    Instance variables:
    Char rank 

    """

    def __init__(self, rank):
        """
        Char -> Rank

        Constructs a Rank with the given rank 

        """
        self.rank = rank

    def __str__(self):
        """
        -> String

        Returns a human readable string of this Rank 

        >>> print(Rank('L'))
        L

        """
        return self.rank

    def __eq__(self, other):
        """
        -> Rank

        Checks if this is equal to the given Rank by comparing
        self.rank for equality. 

        """
        return self.rank == other.rank

    def __hash__(self):
        """
        -> Number

        Hashes this instance. 

        """
        return hash(self.rank)

    def is_soldier(self):
        """
        -> Boolean

        Returns true if this piece is a soldier (rank 1-9).

        """
        return self.rank.isdigit()

    def wins_against(self, other_rank):
        """
        -> Boolean

        Returns true if a piece of this rank can defeat a
        piece of other_rank.

        """
        if self.is_soldier():
            if other_rank.is_soldier():
                return self.rank > other_rank.rank
            elif other_rank.rank == 'B':
                return False
            elif other_rank.rank == 'L':
                return self.rank == '1'
            else:
                return True
        else:
            return False

    def loses_against(self, other_rank):
        """
        -> Boolean

        Returns true if a piece of other_rank can defeat a
        piece of this rank.

        """
        return other_rank.wins_against(self)

    def ties_against(self, other_rank):
        """
        -> Boolean

        Returns true if a piece of this rank will tie with
        a piece of other rank.

        """
        return not (self.wins_against(other_rank) or
                    self.loses_against(other_rank))

    def attack_outcome(self, other_rank):
        """
        -> Result

        where Result is one of "win", "loss", or "tie"

        Returns the result of a piece of this rank attacking a piece
        of other_rank.

        """

        if self.wins_against(other_rank):
            return "win"
        elif self.loses_against(other_rank):
            return "loss"
        else:
            return "tie"

class Owner:

    PLAYER = 0
    OPPONENT = 1

class PieceNotFoundException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

class Board:
    """
    Instance variables:
    [Listof Piece] pieces_list

    """

    def __init__(self, pieces_list=[]):
        """
        [Listof Piece] -> Board

        Constructs a Board with the specified list of pieces. 

        """
        self.pieces_list = pieces_list

    def place_piece(self, piece):
        """
        Piece -> Board

        Adds the given piece to this Board for initial setup. 

        """
        new_list = copy.copy(self.pieces_list)
        new_list.append(piece)
        return Board(new_list)

    def move_piece(self, src, dest):
        """
        Position Position -> Board 

        Moves the piece at the src position to the dest position. 

        """
        piece = self.piece_at(src)

        if piece is not None:
            # List without piece
            new_list = [p for p in self.pieces_list if p != piece]

            # Add piece to list
            new_list.append(piece.move(dest))

            return Board(new_list)
        else:
            raise PieceNotFoundException("Cannot move piece from ( %c%d )" \
                    %(ord('A') + src[0], src[1] + 1))

    def piece_at(self, position):
        """
        Position -> (Piece | None)

        Returns the piece at the given position. 

        """
        return next(
            (p for p in self.pieces_list if p.position == position), None)

    def is_space_blocked_for(self, position, owner):
        """
        Position Owner -> Boolean 

        Checks if the given position
        - can be moved into by the given player
        - contains an opponent's piece that can be attacked but only if
        the given position is not a camp 

        """

        p = self.piece_at(position)
        if p is None:
            return False
        elif p.owner == owner:
            return True
        else:
            return board_layout.is_camp(position)

    def iterate_pieces(self, owner):
        """
        Owner -> [Generator_of Piece]

        Returns a generator for all pieces owned by the given player

        """
        i = iter(self.pieces_list)
        return filter(lambda p: p.owner == owner, i)

    def iterate_moves_for_piece(self, piece):
        """
        Piece -> [Generator_of Position]

        Returns a generator for all possible moves that can
        be made by the given piece. A move is a position that the given
        piece can consider for relocation or attack.

        """
        # TODO: if given piece is an engineer, also need to consider
        # railway positions i.e. not just adjacent pieces
        # The paths to these positions should also not be blocked by
        # the player/opponent's pieces.

        if piece.is_stationary():
            return iter([])

        i = board_layout.iterate_adjacent(piece.position)
        # Make sure we exclude blocked spaces
        i = filter(lambda m: not self.is_space_blocked_for(m, piece.owner), i)
        return i

    def iterate_all_moves(self, owner):
        """
        Owner -> [Generator_of (Position, Position)] 

        Returns a generator for all possible moves that can be made
        by the given player. A move is a tuple of positions 
        (position_from, position_to). The piece at position_from belongs to
        the given player and is allowed to relocate to position_to or attack
        a piece that is currently present at position_to

        """
        for piece in self.iterate_pieces(owner):
            for move in self.iterate_moves_for_piece(piece):
                yield (piece.position, move)

    def serialize(self):
        """
        -> String

        Serialize this Board. 

        """
        return ("( " +
                " ".join([p.serialize() for p in self.pieces_list]) + " )")

    def dump_debug_board(self):
        log.debug(" | ".join([str(p) for p in self.pieces_list]))

    def remove_piece(self, pos):
        """
        Position -> Board

        Removes the piece at the given position from the Board. 

        """
        piece = self.piece_at(pos)

        if piece is not None:
            # List without piece
            new_list = [p for p in self.pieces_list if p != piece]
            return Board(new_list)
        else:
            raise PieceNotFoundException("Cannot remove piece from ( %c%d )"
                                         % (ord('A') + pos[0], pos[1] + 1))

    def update(self, msg):
        """
        MoveMessage -> Board 

        Move pieces if a "move" or "win" is indicated by the given
        MoveMessage, otherwise if a "loss" or "tie" is indicated, 
        then remove pieces appropriately. 

        """
        move_type = msg.movetype
        if move_type == "move":
            return self.move_piece(msg.posfrom, msg.posto)

        attacking_piece = self.piece_at(msg.posfrom)
        defending_piece = self.piece_at(msg.posto)
        if attacking_piece.owner == Owner.OPPONENT:
            opponent_piece = attacking_piece
            player_piece = defending_piece
            attack_outcome = move_type
        else:
            opponent_piece = defending_piece
            player_piece = attacking_piece
            if move_type == "win":
                attack_outcome = "loss"
            elif move_type == "loss":
                attack_outcome = "win"
            else:
                attack_outcome = "tie"

        updated = self.update_probabilities(opponent_piece,
                                            player_piece, attack_outcome)

        if move_type == "win":
            without_loser = updated.remove_piece(msg.posto)
            return without_loser.move_piece(msg.posfrom, msg.posto)
        if move_type == "loss":
            return updated.remove_piece(msg.posfrom)
        if move_type == "tie":
            return updated.remove_piece(msg.posfrom).remove_piece(msg.posto)

    def update_probabilities(self, opponent_piece,
                             player_piece, attack_result):
        """
        Piece Piece Result -> Board

        where Result is one of: "win", "loss" or "tie"

        Updates all of the opponent_piece probabilities given an opponent
        piece and the result of an attack involving that piece.

        """
        assert(opponent_piece.owner == Owner.OPPONENT)
        assert(player_piece.owner == Owner.PLAYER)
        assert(attack_result in ["win", "loss", "tie"])

        ranks_to_exclude = []
        for rank in opponent_piece.ranks():
            if not (rank.attack_outcome(player_piece.get_rank()) ==
                    attack_result):
                ranks_to_exclude.append(rank)

        return self.exclude_ranks(opponent_piece, ranks_to_exclude)

    def exclude_ranks(self, piece, ranks):
        """
        Piece [Ranks] -> Board

        Excludes the given set of ranks for the given piece, returning
        the updated board.

        """
        new_piece = piece.exclude_ranks(ranks)
        new_list = []

        for p in self.pieces_list:
            if p == piece:
                new_list.append(new_piece)
            #elif p.owner == piece.owner:
            #    new_list.append(p.adjust_probabilities(piece, ranks))
            else:
                new_list.append(p)

        return Board(new_list)

    def initialize_opponent_pieces(self):
        """
        -> Board

        Adds all of the opponent's pieces to the board in their
        initial configuration.

        """
        board = self

        for x in range(0, 5):
            for y in range(6, 12):
                (numerators, denominators) = _initial_probability_for((x, y))
                piece = Piece((x, y), Owner.OPPONENT, numerators, denominators)
                board = board.place_piece(piece)

        return board

SOLDIER_RANKS = {Rank(str(r)) for r in range(1, 10)}


class Piece:
    """
    Instance variables:
    Position                  position
    Owner                     owner
    Dictionary(Rank, Fraction)  ranks

    The ranks Dictionary is a mapping from a Rank to a
    probability. Probabilities are represented as a python
    Fraction.

    """

    def __init__(self, position, owner,
                 rank_or_prob_numerators, prob_denominators={}):
        """
        Position Owner Rank -> Piece
           --or--
        Position Owner
           Dictionary(Rank, Number) Dictionary(Rank, Number) -> Piece

        Constructs an instance of Piece initialized with its position,
        owner and a dictionary that maps all possible ranks to the
        probability of this piece having that rank. Alternatively,
        ranks can be a single rank, in which case the probability
        of that rank will be 1 and all others will be 0.

        """
        # Number tuple (row, column)
        self.position = position
        # Owner object
        self.owner = owner

        # If rank_or_prob_numerator is a single Rank rather than a
        # dictionary, convert it into a dictionary where the
        # probability of this piece having that rank is 1.0
        if isinstance(rank_or_prob_numerators, Rank):
            self.prob_numerators = {rank_or_prob_numerators: 1}
            self.prob_denominators = {rank_or_prob_numerators: 1}
        else:
            self.prob_numerators = rank_or_prob_numerators
            self.prob_denominators = prob_denominators

    def move(self, new_posn):
        """
        Position -> Piece

        Returns a hard copy of this instance with a changed position. 

        """
        return Piece(new_posn, self.owner,
                     self.prob_numerators, self.prob_denominators)

    def exclude_ranks(self, ranks):
        """
        set(Rank) -> Piece

        Removes each rank in the given set from this Piece's set of
        possible ranks, and returns the modified Piece.

        """
        ranks_to_remove = set(ranks)
        ranks_to_keep = set(self.ranks()).difference(ranks_to_remove)
        new_numerators = {}
        new_denominators = {}

        num_soldiers_to_remove = 0
        for rank in ranks_to_remove.intersection(SOLDIER_RANKS):
            num_soldiers_to_remove += self.prob_numerators[rank]

        for rank in ranks_to_keep:
            if rank in SOLDIER_RANKS:
                new_numerators[rank] = self.prob_numerators[rank]
                new_denominators[rank] = (self.prob_denominators[rank]
                                          - num_soldiers_to_remove)
            else:
                new_numerators[rank] = self.prob_numerators[rank]
                new_denominators[rank] = self.prob_denominators[rank]

        return Piece(self.position, self.owner,
                     new_numerators, new_denominators)

    def adjust_probabilities(self, piece, excluded_ranks):
        """
        set(Rank) -> Piece

        After using exclude_ranks to exclude a set of ranks for a
        piece, we must adjust the probabilities for every other
        piece on the board accordingly. This function takes the
        piece that was changed using exclude_ranks, along with
        the set of Ranks that were excluded and updates this
        piece. It should be called for every other piece on the
        board when using exclude_ranks.

        """
        excluded_ranks = set(excluded_ranks)
        ranks_removed = excluded_ranks.difference(set(self.ranks()))
        ranks_kept = excluded_ranks.intersection(set(self.ranks()))
        new_numerators = {}
        new_denominators = {}

        soldier_denominator_diff = 0
        for rank in ranks_kept:
            if rank in SOLDIER_RANKS:
                soldier_denominator_diff = \
                    soldier_denominator_diff + piece.probability(rank)

        for rank in ranks_removed:
            new_numerators[rank] = self.prob_numerators[rank]
            new_denominators[rank] = self.prob_denominators[rank] - 1

        for rank in ranks_kept:
            new_numerators[rank] = \
                self.prob_numerators[rank] - piece.probability(rank)
            if rank in SOLDIER_RANKS:
                new_denominators[rank] = \
                    self.prob_denominators[rank] - soldier_denominator_diff
            else:
                new_denominators[rank] = \
                    self.prob_denominators[rank] - piece.probability(rank)

        return Piece(self.position, self.owner,
                     new_numerators, new_denominators)

    def is_stationary(self):
        """
        -> Boolean 

        Returns true if this piece cannot be moved i.e. if it is a flag
        or a landmine or positioned at a headquarter. 

        """
        return (board_layout.is_headquarters(self.position) or
                self.probability(Rank('L')) + self.probability(Rank('F')) == 1)

    def probability(self, rank):
        """
        -> Fraction

        Returns the probability that this piece has the given Rank.

        """
        if not rank in self.ranks():
            return Fraction(0)

        probability = Fraction(self.prob_numerators[rank],
                               self.prob_denominators[rank])
        if rank == Rank('F'):
            return probability
        elif rank == Rank('L'):
            return (probability * (1 - self.probability(Rank('F'))))
        elif rank == Rank('B'):
            return (probability *
                    (1 - self.probability(Rank('L'))
                       - self.probability(Rank('F'))))
        else:
            return (probability *
                    (1 - self.probability(Rank('B'))
                       - self.probability(Rank('L'))
                       - self.probability(Rank('F'))))

    def attack_outcome(self, other_piece):
        """
        -> (Fraction, Fraction, Fraction)

        Returns the expected outcome of an attack made by this piece
        against other_piece. The expected outcome is returned as a tuple
        of probabilities: (P(win), P(tie), P(loss)).

        """
        p_win = 0
        p_tie = 0
        p_loss = 0

        for rank_a in self.numerators:
            for rank_b in other_piece.numerators:
                p = (self.probability(rank_a) *
                     other_piece.probability(rank_b))

                if rank_a.wins_against(rank_b):
                    p_win += p
                elif rank_a.loses_against(rank_b):
                    p_loss += p
                else:
                    p_tie += p

        return (p_win, p_tie, p_loss)

    def __eq__(self, piece):
        """
        Piece -> Boolean 

        Checks if the given Piece is the same as this instance
        """
        return (isinstance(piece, Piece) and
                self.prob_numerators == piece.prob_numerators and
                self.prob_denominators == piece.prob_denominators and
                self.position == piece.position and
                self.owner == piece.owner)

    def __str__(self):
        (x, y) = self.position

        if self.owner == Owner.PLAYER:
            owner = "P"
        else:
            owner = "O"

        ranks = "[%s]" % ", ".join(
            [str(rank) for rank in self.ranks()])
        return "%c%d %c %s" % (ord('A') + x, y + 1, owner, ranks)

    def serialize(self):
        """
        -> String

        Serialize this Piece.
        Precondition: The piece must have an owner of Owner.PLAYER

        """
        assert(self.owner == Owner.PLAYER)
        (x, y) = self.position
        rank = str(self.get_rank())
        return "( %c%d %c )" % (ord('A') + x, y + 1, rank)

    def get_rank(self):
        """
        -> Rank

        Returns this piece's rank.
        Precondition: The piece must have an owner of Owner.PLAYER

        """
        assert(self.owner == Owner.PLAYER)
        return next(self.ranks())

    def ranks(self):
        """
        -> Generator_of(Rank)

        Returns an iterator which will iterate over all of this
        piece's possible ranks.

        """
        return iter(self.prob_numerators.keys())


def _initial_probability_for(position):
    """
    Position -> Dictionary(Rank, Fraction)

    Returns the initial probability dictionary for a piece placed
    at the given position. Probabilities are calculated as follows:

    P(flag | is_headquarters) = 1/2
    P(flag | ~is_headquarters) = 0
    P(landmine | (y in range(10, 12))) = 1/3 * (1 - P(flag))
    P(landmine | ~(y in range(10, 12))) = 0
    P(bomb | (y in range(7, 12))) = 1/10 * (1 - (P(flag) + P(landmine)))
    P(bomb | ~(y in range(7, 12))) = 0
    P(1) = P(2) = P(3) = 3/19 * (1 - (P(flag) + P(landmine) + P(bomb)))
    P(4) = P(5) = P(6) = P(7) =
    2/19 * (1 - (P(flag) + P(landmine) + P(bomb)))
    P(8) = P(9) = 1/19 * (1 - (P(flag) + P(landmine) + P(bomb)))

    """
    (x, y) = position

    numerators = {}
    denominators = {}

    # Pieces outside the headquarters cannot be the flag
    if board_layout.is_headquarters(position):
        numerators[Rank('F')] = 1
        denominators[Rank('F')] = 2

    # Landmines cannot be outside of the back two rows
    if y in range(10, 12):
        numerators[Rank('L')] = 1
        denominators[Rank('L')] = 3

    # Bombs cannot be in the front row
    if y in range(7, 12):
        numerators[Rank('B')] = 1
        denominators[Rank('B')] = 8

    # Any square can potentially contain a piece 1-9
    for r in range(1, 4):
        numerators[Rank(str(r))] = 3
        denominators[Rank(str(r))] = 19
    for r in range(4, 8):
        numerators[Rank(str(r))] = 2
        denominators[Rank(str(r))] = 19
    for r in range(8, 10):
        numerators[Rank(str(r))] = 1
        denominators[Rank(str(r))] = 19

    return (numerators, denominators)
