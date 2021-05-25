from typing import Literal
from tiles import Tile


class Wall:
    """
    The Wall area is located on each player's board.

    The wall contains a 5x5 grid with spaces to put tiles.

    Tiles are added to this area by moving tiles from the pattern lines area
    onto the wall at the end of a round.

    Tiles are never removed from this area.

    Note that:
    - no tile type can occur more than once in any row / column in the grid.
    - when moving a tile from a pattern line onto the wall, the
        tile has to be added to the same row on the wall as the pattern line.
    - when moving tiles onto the wall, the player is rewarded points. The
        number of points is based on the number of directly adjacent tiles on
        the wall.
    """
    def __init__(self):
        self.rows = {i: WallSequence() for i in range(5)}
        self.columns = {i: WallSequence() for i in range(5)}

    def add_tile(
        self,
        tile: Tile,
        row_nr: Literal[0, 1, 2, 3, 4],
        col_nr: Literal[0, 1, 2, 3, 4]
    ) -> None:
        """ Add tile to the wall """
        not_yet_in_row = tile not in self.rows[row_nr]
        not_yet_in_col = tile not in self.columns[col_nr]

        if not_yet_in_row and not_yet_in_col:
            self.rows[row_nr][col_nr] = tile
            self.columns[col_nr][row_nr] = tile
        else:
            msg = f"Cannot add {tile} to #{col_nr} in row #{row_nr}"
            raise ValueError(msg)

    def count_points_tile(
        self,
        row_nr: Literal[0, 1, 2, 3, 4],
        col_nr: Literal[0, 1, 2, 3, 4]
    ) -> int:
        """Returns the number of points awarded for adding tile on the wall"""
        horizontal = self.rows[row_nr].count_one_dimension(col_nr)
        vertical = self.columns[col_nr].count_one_dimension(row_nr)

        if horizontal > 1 and vertical > 1:
            points = horizontal + vertical
        else:
            points = max([horizontal, vertical])
        return points

    def __repr__(self) -> str:
        return str(self.rows)

    @property
    def is_finished(self) -> bool:
        """ Check if the wall contains a fully completed row, which would mark
        the end of the game. """
        return any(row.is_full for row in self.rows.values())


class WallSequence(list):
    """ This class represents a row or column on the wall area """

    def __init__(self):
        super().__init__([None]*5)

    def count_one_dimension(self, index: Literal[1, 2, 3, 4, 5]) -> int:
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

    @property
    def is_full(self) -> bool:
        """ Check if the sequence is completely filled with tiles """
        return all(val is not None for val in self)
