from collections import defaultdict


class Factory(defaultdict):
    """
    This class represents the factories that are filled with 4 tiles at the
    start of each round.
    """
    def __init__(self):
        super().__init__(lambda: 0)

    @property
    def is_empty(self):
        return sum(self.values()) == 0
