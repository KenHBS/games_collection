# TODO: Implement the PlayerBoard and how the different components interact
# with each other


from misc import Pouch, Tile, TileCounter, EndStateAreaSequence
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
        self.is_start_player = False

        self.inner_round_tile_area = InnerRoundTileArea()
        self.end_state_tile_area = EndStateTileArea()
        self.inner_round_minus_points = InnerRoundMinusPoints()

    def add_tile_count(self, tiles: TileCounter, row_nr: int) -> None:
        """
        Add tile counters from the middle field to your inner-round area.
        If there is not enough capacity, the surplus tiles will be added to
        the minus point area
        """
        row = self.inner_round_tile_area.grid[row_nr]

        # handle surplus tiles
        if tiles.count > row.free_spaces:
            surplus_count = tiles.count - row.free_spaces
            surplus_tiles = TileCounter(tile=tiles.tile, count=surplus_count)

            self.inner_round_minus_points += surplus_tiles
            tiles.count = row.free_spaces

        self.inner_round_tile_area.grid[row_nr] += tiles

    def end_of_round_scoring(self) -> None:
        self.score_inner_round_tile_area()
        self.inner_round_tile_area()

    def score_inner_round_tile_area(self) -> List[TileCounter]:
        discarded_tiles_counter_container = []
        for row_nr in range(1, 6):
            grid_row = self.inner_round_tile_area.grid[row_nr]
            is_full = grid_row.free_spaces == 0
            if is_full:
                tile = grid_row.spaces[0]

                # handle leftover tiles
                surplus_count = grid_row.used_spaces - 1
                surplus_tiles = TileCounter(tile=tile, count=surplus_count)
                discarded_tiles_counter_container.append(surplus_tiles)

                # handle tile placement in end-state area
                print(f"You are moving {tile} into row #{row_nr}!")
                print("Your end-state-tile-area looks like this:")
                print(self.end_state_tile_area)
                while True:
                    col_nr = input("In which column do you place the tile?")
                    try:
                        self.end_state_tile_area.add_tile(
                            tile, row_nr=row_nr, col_nr=col_nr
                        )
                    except ValueError:
                        print("You provided an invalid value. Try again ..")
                    else:
                        break

                self.point_total += self.end_state_tile_area.count_points_tile(
                    row_nr=row_nr, col_nr=col_nr
                )

        return discarded_tiles_counter_container

    def score_inner_round_minus_points(self) -> List[TileCounter]:
        """ Score and flush the minus point area. Return the discarded tiles"""
        self.point_total -= self.inner_round_minus_points.count_minus_points

        discarded_tile_list = self.inner_round_minus_points[:]

        self.inner_round_minus_points = InnerRoundMinusPoints()
        return [TileCounter(tile, 1) for tile in discarded_tile_list]

    def handle_round_end(self, tile_pouch: Pouch) -> Pouch:
        """
        Move tiles from inner-round area into end-state area,
        score minus points and return tiles to pouch
        """
        leftover_tiles1 = self.score_inner_round_tile_area()
        leftover_tiles2 = self.score_inner_round_minus_points()

        for tilecounter in [*leftover_tiles1, *leftover_tiles2]:
            tile_pouch += tilecounter
        return tile_pouch


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

    def __repr__(self) -> str:
        return str(self.rows)


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
