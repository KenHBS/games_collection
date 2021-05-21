from collections import defaultdict
from random import shuffle
from typing import List

from tiles import Tile, TileCounter


class Pouch(List[Tile]):
    """
    The pouch that contains all tiles in the beginning of the game.

    Tiles are taken from the pouch to fill up the shared board.
    Discarded tiles are added to the pouch once it's completely empty.
    """
    def __init__(self):
        super().__init__(
            [Tile(style) for style in range(5) for _ in range(20)]
        )
        shuffle(self)

    def __add__(self, other: TileCounter):
        add_this = [other.tile] * other.count
        super().__add__(self, add_this)
        shuffle(self)

    def take_four(self, n: int = 4) -> List[Tile]:
        """ Take last n tiles from pouch """
        take = self[-n:]
        del self[-n:]
        return take


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


class TheMiddle(Factory):
    """ This class represents 'The Middle'.
    All tiles that are not picked up when a player picks up tiles from a
    factory are placed in the middle.

    TheMiddle behaves like a Factory, except:
    - the middle is empty at the beginning of a round,
    - the first player to draw from the middle is penalised with 1 minus point,
    - the first player to draw from the middle is the starting player
        in the next round.
    """
    def __init__(self):
        self.is_untouched = True
        super().__init__()
