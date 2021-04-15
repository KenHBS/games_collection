# TODO: implement __add__ in InnerRoundTileAreaRows

from misc import Tile, Pouch, TileCounter
from typing import Union, Literal


class PlayerBoard:
    """
    The player board is bound to a single player. It contains:
    - the player's point total
    - the inner-round tile area
    - the end state tile area
    - the inner-round minus point area
    """
    def __init__(self, player: str):
        self.player = player
        self.point_total = 0

        self.inner_round_tile_area = InnerRoundTileArea()
        self.end_state_tile_area = EndStateTileArea()
        self.inner_round_minus_points = InnerRoundMinusPoints()


class InnerRoundTileAreaRows:
    def __init__(self, capacity: Literal[1, 2, 3, 4, 5]):
        self.capacity = capacity

        self.row_tile_style = None
        self.spaces = [None] * capacity

    def __add__(self, other: TileCounter) -> None:
        """ Add a TileCounter to this row """
        self._validate_style(incoming_style=other.tile.style)
        self._validate_available_space(incoming_tile_count=other.count)

    def _validate_style(incoming_style: str) -> None:
        """ Raise error when the incoming tile style is incompatible with the row """
        if self.row_style is not None:
            if row_style != incoming_style:
                msg = f"Can only add same style tiles to a row. You are trying to add {incoming_style} tile(s) to a row with {row_style}."
                raise ValueError(msg)

    def _validate_available_space(incoming_tile_count: int) -> None:
        """ Raise error when the number of incoming tiles exceeds the available space in the row """
        if incoming_tile_count > self.free_spaces:
            msg = f"Only {self.free_spaces} available in this row. You tried to add {incoming_tile_count}."
            raise ValueError(msg)

    @property
    def row_style(self) -> Union[None, Tile.style]:
        """ Returns the Tile.style of the tiles in this row. Return None if row is empty """
        if self.spaces[0] is None:
            return None
        else:
            tile = self.spaces[0]
            return tile.style

    @property
    def free_spaces(self) -> int:
        """ Returns how many None spaces are left in the row """
        return sum(1 for x  in self.spaces if x is None)

    def flush_row(self) -> List[None]:
        """ Flush all tiles from the spaces. That is, fill them with Nones """
        self.row_tile_style = None
        self.spaces = [None] * self.capacity


class InnerRoundTileArea:
    """
    The inner-round title area is located on each player's board.

    This area contains:
    - 5 rows with 1, 2, 3, 4 and 5 spaces to put tiles. This is called grid

    Each row can only contain a single type of tile.

    Tiles are added to this area by picking up tiles from the SharedBoard
    Tiles are removed from this area at the end of a round. This is done by:
    - moving a single tile of the row over to the EndStateTileArea of the PlayerBoard.
    - moving the remainder of the tiles (if any) back into the tile pool.
    Note that this action may only happen when the rows in the InnerRoundTileArea is completely filled
    """
    def __init__(self):
        self.grid = {i: [None]*i for i in range(1, 6)}

    def add(self, tile_counter: TileCounter, grid_row: Literal[1, 2, 3, 4, 5]) -> None:
        """ add tile_counter to your plate """
        self._validate_grid_type()
        self.grid[grid_row] += tile_counter





class EndStateTileArea:
    """
    The end-state tile area is located on each player's board.

    This area contains:
    - 5x5 grid with spaces to put tiles

    Tiles are added to this area by moving.
    Tiles are never removed from this area.

    Note that:
    - no tile type can occur more than once in any row / column in the grid.
    - when moving tiles into the end-state tile area from the inner-round tile area,
        the 'eligible' row in the end-state tile area is determined by the row in the
        inner-round tile area.
    - when moving tiles into this area, the owner of the board is rewarded points. The
        number of points is based on the number of tiles in the end-state tile area that
        are directly adjacent to the newly added tile.
    """


class InnerRoundMinusPoints(List[Tile]):
    """
    Whenever a player takes tiles from the SharedBoard, but isn't able to place them
    in their inner-round tile area (there are multiple reasons), the player is penalised.

    At the end of each round, the inner-round minus point
    area is cleared of its tiles and the minus point are deducted from the player's round point total.

    The penalty for adding tiles to the negative point area increases when more tiles are added to the
    inner-round minus point area. This increasing penalty is captured by `negative_point_mapping`
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

    def count_minus_points(self) -> int:
        """ Returns to number of minus game points """
        x = self.__len__()
        return InnerRoundMinusPoints.negative_point_mapping.get(x, 14)

    def __repr__(self):
        tiles = ", ".join(x.style for x in self)
        return f"{tiles} - ({self.count_minus_points()} minus points)"