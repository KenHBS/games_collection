from random import shuffle
from typing import List, Dict

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


class Plate:
    """A plate contains tiles that can be picked up by players"""
    def __init__(self, plate_id: int):
        self.id = plate_id

    def split_tiles(self, keep: Tile) -> Dict:
        """ Choose one tile type to keep, the rest lands in the middle area """
        pass
        # keepers = [tile for tile in self.tiles if tile.style == keep.style]
        # non_keepers = [
        #   tile for tile in self.tiles if tile.style != keep.style
        # ]

        # non_keepers
        # return {"to_middle": non_keepers, }

    def pick_up(self, tile: Tile) -> TileCounter:
        # split tiles, add some to middle, some to player board
        pass

    def fill_plate(self, pouch: Pouch):
        pass
