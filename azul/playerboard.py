# TDOO: Implement the PlayerBoard and how the different components interact
# with each other
from misc import Tile, TileCounter, EndStateAreaSequence
from typing import Union, Literal, List


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
    """
    This class describes the rows in the InnerRoundTileArea.

    - The rows have between 1, 2, 3, 4 or 5 spaces that may be occupied by max.
        1 tile type.
    - The predefined number of spaces can never be exceeded.
    - Tiles can only be removed when they're moved into the EndStateTileArea
    """
    def __init__(self, capacity: Literal[1, 2, 3, 4, 5]):
        self.capacity = capacity

        self.row_tile_style = None
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

        self.row_tile_style = None
        self.spaces = [None] * self.capacity

    def __add__(self, other: TileCounter) -> None:
        """ Add a TileCounter to this row """
        self._validate_style(incoming_style=other.tile.style)
        self._validate_available_space(incoming_tile_count=other.count)

        fill_start = self.used_spaces
        fill_end = fill_start + other.count

        self.spaces[fill_start:fill_end] = [other.tile] * other.count

    def __repr__(self) -> str:
        """ Visual representation of this class """
        return str(["--" if v is None else v for v in self.spaces])

    def _validate_style(self, incoming_style: str) -> None:
        """ Raise error when the incoming tile style is incompatible with \
             the row """
        if self.row_style is not None:
            if self.row_style != incoming_style:
                msg = f"Can only add same style tiles to a row. \
                    You tried to add {incoming_style} tile(s) to a row \
                    with {self.row_style}."
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


class EndStateTileArea:
    """
    The end-state tile area is located on each player's board.

    This area contains:
    - 5x5 grid with spaces to put tiles

    Tiles are added to this area by moving.
    Tiles are never removed from this area.

    Note that:
    - no tile type can occur more than once in any row / column in the grid.
    - when moving tiles into the end-state tile area from the inner-round tile
        area, the 'eligible' row in the end-state tile area is determined by
        the row in the inner-round tile area.
    - when moving tiles into this area, the owner of the board is rewarded
        points. The number of points is based on the number of tiles in the
        end-state tile area that are directly adjacent to the newly added tile.
    """
    def __init__(self):
        self.rows = {i: EndStateAreaSequence() for i in range(5)}
        self.columns = {i: EndStateAreaSequence() for i in range(5)}

    def add_tile(
        self,
        tile: Tile,
        row_nr: Literal[range(5)],
        col_nr: Literal[range(5)]
    ) -> None:
        """ Add tile to the end-state tile area """
        self.rows[row_nr][col_nr] = tile
        self.columns[col_nr][row_nr] = tile

    def count_points_tile(
        self,
        row_nr: Literal[range(5)],
        col_nr: Literal[range(5)]
    ) -> int:
        """
        Returns the number of points awarded for adding tile into the
        end-state tile area
        """
        horizontal = self.rows[row_nr].count_one_dimension(col_nr)
        vertical = self.columns[col_nr].count_one_dimension(row_nr)

        if horizontal > 1 and vertical > 1:
            points = horizontal + vertical
        else:
            points = max([horizontal, vertical])
        return points


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

    def count_minus_points(self) -> int:
        """ Returns to number of minus game points """
        x = self.__len__()
        return InnerRoundMinusPoints.negative_point_mapping.get(x, 14)

    def __repr__(self):
        tiles = ", ".join(x.style for x in self)
        return f"{tiles} - ({self.count_minus_points()} minus points)"
