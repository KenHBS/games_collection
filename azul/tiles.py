from dataclasses import dataclass
from typing import Literal


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
        return NotImplemented

    def __hash__(self):
        return hash(self.style)


@dataclass
class TileCounter:
    tile: Tile
    count: int = 0

    def __repr__(self):
        return f"{self.count} x {self.tile}"
