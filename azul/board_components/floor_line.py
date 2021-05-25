from tiles import Tile, TileCounter
from typing import List


class FloorLine(List[Tile]):
    """
    This is the minus points area of the player board.

    Whenever a player takes tiles from one of the factories or 'the middle',
    but is not able to place them in their PatternLine area (there are
    multiple reasons), the player is penalised.

    Also, whenever a player picks up the starting player's tile, that tile
    is added to the floor line.

    At the end of each round, the floor line is cleared of its tiles and the
    minus point are deducted from the player's round point total.

    The penalty for adding tiles to the floor line area increases when
    more tiles are added to it. This increasing penalty is captured by
    `negative_point_mapping`.
    """
    negative_point_mapping = {
        0: 0,
        1: 1,
        2: 2,
        3: 4,
        4: 6,
        5: 8,
        6: 11,
        7: 14
    }

    def __add__(self, other: TileCounter) -> List[Tile]:
        """ Returns list with floor line tiles plus new tiles """
        add_this = [other.tile] * other.count
        return super().__add__(add_this)

    def __iadd__(self, other: TileCounter) -> None:
        """ Adds new tiles to the floor line tiles """
        return FloorLine(self.__add__(other))

    def count_minus_points(self) -> int:
        """ Returns to number of minus game points """
        x = self.__len__()
        return FloorLine.negative_point_mapping.get(x, 14)

    def __repr__(self):
        tiles = ", ".join(x.style for x in self)
        return f"{tiles} - ({self.count_minus_points()} minus points)"
