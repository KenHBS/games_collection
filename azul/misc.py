from random import shuffle
from typing import List, Literal


class Tile:
    style_mapping = {
        0: "black \U0000203B",
        1: "blue \U00002021",
        2: "red \U00002051",
        3: "yellow \U00002050",
        4: "white \U000020AA"
    }

    def __init__(self, style: Literal[0, 1, 2, 3, 4]):
        self.style = Tile.style_mapping[style]

    def __repr__(self) -> str:
        return self.style

    def __eq__(self, other) -> bool:
        if isinstance(other, Tile):
            return self.style == other.style
        else:
            return False


class TileCounter:
    def __init__(self, tile: Tile, count: int):
        self.tile = tile
        self.count = count

    def __repr__(self):
        return f"{self.count} x {self.tile}"


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


class EndStateAreaSequence(list):
    def __init__(self):
        super().__init__([None]*5)

    def count_one_dimension(self, index: Literal[range(1, 6)]) -> int:
        """
        Returns the number of adjacently occupied fields to the tile at 'index'
        """

        anchor_tile_index = index - 1
        if self[anchor_tile_index] is None:
            raise ValueError(f"Cannot count the points of unoccupied space.\
Trying to count element #{index} of {self}")
        point_counter = 1

        # count left-adjacent occupied tiles
        leftmost_spot = anchor_tile_index == 0
        left_tile_index = anchor_tile_index - 1

        # check whether left tile is out of  bounds, i.e. check if
        # left_tile_index is negative:
        if not leftmost_spot:
            while (self[left_tile_index] is not None) and not leftmost_spot:
                point_counter += 1
                left_tile_index -= 1
                leftmost_spot = left_tile_index == 0

        # count right-adjacent occupied tiles
        rightmost_spot = anchor_tile_index == 4
        right_tile_index = anchor_tile_index + 1

        # check whether right tile is not out of bounds
        if not rightmost_spot:
            while (self[right_tile_index] is not None) and not rightmost_spot:
                point_counter += 1
                right_tile_index += 1
                rightmost_spot = right_tile_index == 4

        return point_counter

    def __setitem__(self, index: int, value: Tile) -> None:
        if value in self:
            msg = f"This end-state sequence ({self}) already contains {value}.\
You can only place new tile types in this row"
            raise ValueError(msg)
        super().__setitem__(index, value)

    def __repr__(self) -> str:
        return " | ".join(
            '-'*8 if t is None else str(t).center(8) for t in self
        )
