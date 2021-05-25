from typing import Union, Literal, List
from tiles import TileCounter


class PatternLines:
    """
    The pattern lines area is located on each player's board.

    This area contains 5 rows (PatternLineRows) with 1 to 5 spots to put tiles.

    Each pattern line row can only contain a single type of tile.

    Tiles are added to this area by picking up tiles from the factories.

    When a pattern line row is completely filled, then the row will be cleared
    at the end of a round. This is done by:
    - moving a single tile of the row over to the Wall
    - moving the remainder of the tiles (if any) back into the Pouch.
    """
    def __init__(self):
        self.grid = {i: PatternLinesRows(i) for i in range(1, 6)}

    def __repr__(self) -> str:
        return "\n".join(str(self.grid[i]) for i in range(1, 6))


class PatternLinesRows:
    """
    This class describes the rows in the PatterLines area.

    - The rows have between 1, 2, 3, 4 or 5 spaces that may be occupied by max.
        1 tile type.
    - The predefined number of spaces can never be exceeded.
    - Tiles can only be removed when they're moved into the Wall area
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
