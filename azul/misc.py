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

    def __repr__(self):
        return self.style


class TileCounter:
    def __init__(self, tile: Tile, count: int):
        self.tile = Tile
        self.count = count

    def __repr__(self):
        return f"{self.count} x {self.tile}"


class Pouch(List[Tile]):
    """ The pouch that contains all tiles in the beginning and is used to draw new tiles from """
    def __init__(self):
        super().__init__([Tile(style) for style in range(5) for _ in range(20)])
        shuffle(self)
