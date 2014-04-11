class Rank:
    """
    Instance variables:
    str rank

    """

    def __init__(self, rank):
        """
        str -> Rank

        Constructs a Rank with the given rank

        """
        self.rank = rank

    def __str__(self):
        """
        -> str

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
        -> int

        Hashes this instance.

        """
        return hash(self.rank)

    def is_soldier(self):
        """
        -> bool

        Returns true if this piece is a soldier (rank 1-9).

        """
        return self.rank.isdigit()

    def wins_against(self, other_rank):
        """
        -> bool

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
        -> bool

        Returns true if a piece of other_rank can defeat a
        piece of this rank.

        """
        return other_rank.wins_against(self)

    def ties_against(self, other_rank):
        """
        -> bool

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
