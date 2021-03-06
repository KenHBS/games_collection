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
