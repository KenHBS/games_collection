from typing import Union, Literal, List
from tiles import Tile, TileCounter


class InnerRoundTileAreaRows:
    """
    This class describes the rows in the InnerRoundTileArea.

    - The rows have between 1, 2, 3, 4 or 5 spaces that may be occupied by max.
        1 tile type.
    - The predefined number of spaces can never be exceeded.
    - Tiles can only be removed when they're moved into the EndStateTileArea
    """
    def __init__(self, capacity: Literal[1, 2, 3, 4, 5]):
        self.capacity = capacity

        self.spaces = [None] * capacity

    @property
    def row_style(self) -> Union[None, str]:
        """Return the Tile.style of tiles in this row. None if row is empty"""
        if self.spaces[0] is None:
            return None
        else:
            tile = self.spaces[0]
            return tile.style

    @property
    def free_spaces(self) -> int:
        """ Returns how many None spaces are left in the row """
        return sum(1 for x in self.spaces if x is None)

    @property
    def used_spaces(self) -> int:
        """ Returns how many spaces are occupied by tiles """
        return sum(1 for x in self.spaces if x is not None)

    def flush_row(self) -> List[None]:
        """ Flush all tiles from the spaces. That is, fill them with Nones.
        This is only possible when all spaces are occupied. """
        if self.free_spaces > 0:
            msg = f"The row still has free spaces. \
Cannot flush row until it's full: {self}"
            raise ValueError(msg)

        self.spaces = [None] * self.capacity

    def __iadd__(self, other: TileCounter):
        """ Add a TileCounter to this row """
        self._validate_style(incoming_style=other.tile.style)
        self._validate_available_space(incoming_tile_count=other.count)

        fill_start = self.used_spaces
        fill_end = fill_start + other.count

        self.spaces[fill_start:fill_end] = [other.tile] * other.count
        return self

    def __repr__(self) -> str:
        """ Visual representation of this class """
        return str(
            ["-"*8 if v is None else str(v).ljust(8) for v in self.spaces]
        )

    def _validate_style(self, incoming_style: str) -> None:
        """ Raise error when the incoming tile style is incompatible with \
the row """
        if self.row_style is not None:
            if self.row_style != incoming_style:
                msg = f"Can only add same style tiles to a row. \
You tried to add {incoming_style} tile(s) to a row with {self.row_style}."
                raise ValueError(msg)

    def _validate_available_space(self, incoming_tile_count: int) -> None:
        """
        Raise error when the number of incoming tiles exceeds the available
        space in the row
        """
        if incoming_tile_count > self.free_spaces:
            msg = f"Only {self.free_spaces} available in this row. \
You tried to add {incoming_tile_count}."
            raise ValueError(msg)


class InnerRoundTileArea:
    """
    The inner-round title area is located on each player's board.

    This area contains:
    - 5 rows with 1, 2, 3, 4 and 5 spaces to put tiles. This is called grid

    Each row can only contain a single type of tile.

    Tiles are added to this area by picking up tiles from the SharedBoard
    Tiles are removed from this area at the end of a round. This is done by:
    - moving a single tile of the row over to the EndStateTileArea of the
        PlayerBoard.
    - moving the remainder of the tiles (if any) back into the tile pool.
    Note that this action may only happen when the rows in the
        InnerRoundTileArea is completely filled
    """
    def __init__(self):
        self.grid = {i: InnerRoundTileAreaRows(i) for i in range(1, 6)}

    def __repr__(self) -> str:
        return "\n".join(str(self.grid[i]) for i in range(1, 6))


class InnerRoundMinusPoints(List[Tile]):
    """
    Whenever a player takes tiles from the SharedBoard, but is not able
    to place them in their inner-round tile area (there are multiple reasons),
    the player is penalised.

    At the end of each round, the inner-round minus point area is cleared of
    its tiles and the minus point are deducted from the player's round point
    total.

    The penalty for adding tiles to the negative point area increases when
    more tiles are added to the inner-round minus point area. This increasing
    penalty is captured by `negative_point_mapping`.
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
        """ Returns list with minus-point area tiles plus new tiles """
        add_this = [other.tile] * other.count
        return super().__add__(add_this)

    def __iadd__(self, other: TileCounter) -> None:
        """ Adds new tiles to the minus-point area tiles """
        return InnerRoundMinusPoints(self.__add__(other))

    def count_minus_points(self) -> int:
        """ Returns to number of minus game points """
        x = self.__len__()
        return InnerRoundMinusPoints.negative_point_mapping.get(x, 14)

    def __repr__(self):
        tiles = ", ".join(x.style for x in self)
        return f"{tiles} - ({self.count_minus_points()} minus points)"
