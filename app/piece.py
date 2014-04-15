import app.board_layout as board_layout
from app.rank import Rank
from fractions import Fraction

SOLDIER_RANKS = {Rank(str(r)) for r in range(1, 10)}
ALL_RANKS = SOLDIER_RANKS.union({Rank('F'), Rank('L'), Rank('B')})


class Owner:
    """
    An enumeration indicating the owner of any piece 
    - either Owner.PLAYER or Owner.OPPONENT

    """
    PLAYER = 0
    OPPONENT = 1


class Piece:
    """
    Instance variables:
    Position                    position
    Owner                       owner
    dict(Rank, Fraction)  numerators
    dict(Rank, Fraction)  denominators

    The numerators and denominators dictionaries map a rank
    to a probability (numerators[rank]/denominators[rank]).

    """

    def __init__(self, position, owner,
                 rank_or_prob_numerators, prob_denominators={}):
        """
        Position Owner Rank -> Piece
           --or--
        Position Owner
           dict(Rank, Number) dict(Rank, Number) -> Piece

        Constructs an instance of Piece initialized with its position,
        owner and a dictionary that maps all possible ranks to the
        probability of this piece having that rank. Alternatively,
        ranks can be a single rank, in which case the probability
        of that rank will be 1 and all others will be 0.
        owner and set of all possible ranks.

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

    def is_stationary(self):
        """
        -> bool

        Returns true if this piece cannot be moved i.e. if it is a flag
        or a landmine or positioned at a headquarter.

        """
        return (board_layout.is_headquarters(self.position) or
                self.probability(Rank('L')) + self.probability(Rank('F')) == 1)

    def exclude_ranks(self, ranks):
        """
        set(Rank) -> Piece

        Removes each rank in the given set from this Piece's set of
        possible ranks, and returns the modified Piece.

        """
        ranks_to_remove = set(self.ranks()).intersection(set(ranks))
        ranks_to_keep = set(self.ranks()).difference(ranks_to_remove)
        soldiers_to_keep = ranks_to_keep.intersection(SOLDIER_RANKS)
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

        if len(soldiers_to_keep) == 0:
            if Rank('B') in new_numerators:
                new_numerators[Rank('B')] = Fraction(1)
                new_denominators[Rank('B')] = Fraction(1)
            else:
                if Rank('L') in new_numerators:
                    new_numerators[Rank('L')] = Fraction(1)
                    new_denominators[Rank('L')] = Fraction(1)
                else:
                    new_numerators[Rank('F')] = Fraction(1)
                    new_denominators[Rank('F')] = Fraction(1)

        return Piece(self.position, self.owner,
                     new_numerators, new_denominators)

    def probability(self, rank):
        """
        Rank -> Fraction

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

    def expected_attack_outcome(self, other_piece):
        """
        Piece -> (Fraction, Fraction, Fraction)

        Returns the expected outcome of an attack made by this piece
        against other_piece. The expected outcome is returned as a tuple
        of probabilities: (P(win), P(tie), P(loss)).

        """
        p_win = 0
        p_tie = 0
        p_loss = 0

        for rank_a in self.prob_numerators:
            for rank_b in other_piece.prob_numerators:
                p = (self.probability(rank_a) *
                     other_piece.probability(rank_b))

                if rank_a.wins_against(rank_b):
                    p_win += p
                elif rank_a.loses_against(rank_b):
                    p_loss += p
                else:
                    p_tie += p

        return (p_win, p_tie, p_loss)

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
        -> iter(Rank)

        Returns an iterator which will iterate over all of this
        piece's possible ranks.

        """
        return iter(self.prob_numerators.keys())

    def __eq__(self, piece):
        """
        object -> bool

        Checks if the given Piece is the same as this instance
        """
        return (isinstance(piece, Piece) and
                self.prob_numerators == piece.prob_numerators and
                self.prob_denominators == piece.prob_denominators and
                self.position == piece.position and
                self.owner == piece.owner)

    def __str__(self):
        """
        -> str

        Returns a string describing this piece
        """
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
        -> str

        Serialize this Piece.
        Precondition: The piece must have an owner of Owner.PLAYER

        """
        assert(self.owner == Owner.PLAYER)
        (x, y) = self.position
        rank = str(self.get_rank())
        return "( %c%d %c )" % (ord('A') + x, y + 1, rank)
