from board_components import PatternLines, FloorLine, Wall
from game_pieces import import Tile, TileCounter
from typing import List


class PlayerBoard:
    """
    The player board is bound to a single player. It contains:
    - the player's point total
    - the inner-round tile area
    - the end state tile area
    - the inner-round minus point area
    """
    def __init__(self):
        self.point_total = 0
        self.is_start_player = False

        self.pattern_lines = PatternLines()
        self.wall = Wall()
        self.floor_line = FloorLine()

    def add_tile_count(self, tiles: TileCounter, row_nr: int) -> None:
        """
        Add tile counters to your inner-round area. If there is not enough
        capacity, the surplus tiles will be added to the minus point area
        """
        row = self.pattern_lines.grid[row_nr]

        # handle surplus tiles
        if tiles.count > row.free_spaces:
            surplus_count = tiles.count - row.free_spaces
            surplus_tiles = TileCounter(tile=tiles.tile, count=surplus_count)

            self.floor_line += surplus_tiles
            tiles.count = row.free_spaces

        self.pattern_lines.grid[row_nr] += tiles

    def handle_round_end(self) -> List[TileCounter]:
        """
        Move tiles from inner-round area into end-state area,
        score minus points and return leftover tiles.
        """
        leftover_tiles1 = self.score_pattern_lines()
        leftover_tiles2 = self.score_floor_line()

        return [*leftover_tiles1, *leftover_tiles2]

    def score_pattern_lines(self) -> List[TileCounter]:
        """
        Move tiles from inner-round tile area to end-state tile area.
        This involves:
        - identifying which rows in the inner-round tile area are full (and can
            be moved)
        - ask for a column to move the tile into (ask until valid input)
        - calculate the points for that tile & add them to point total
        - return all tiles that are left over (as a list of TileCounters)
        """
        discarded_tiles_counter_container = []
        for row_nr in range(1, 6):
            grid_row = self.pattern_lines.grid[row_nr]
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
                print(self.wall)
                while True:
                    col_nr = input("In which column do you place the tile?")
                    try:
                        self.wall.add_tile(
                            tile, row_nr=row_nr, col_nr=col_nr
                        )
                    except ValueError:
                        print("You cannot place your tile there. Try again ..")
                    else:
                        break

                self.point_total += self.wall.count_points_tile(
                    row_nr=row_nr, col_nr=col_nr
                )

        return discarded_tiles_counter_container

    def score_floor_line(self) -> List[TileCounter]:
        """
        Score and flush the minus point area. Returns a list with TileCounter
        that represent the discarded tiles.

        The method makes sure that the minus-tile (=Tile(99)) does not end up
        in the discarded tiles. The minus-point tile implicitly returns to
        TheMiddle (actually it is recreated whenever somebody takes a
        'first draw' from TheMiddle)
        """
        self.point_total -= self.floor_line.count_minus_points

        discarded_tile_list = self.floor_line[:]
        self.floor_line = FloorLine()

        return [
            TileCounter(tile, 1)
            for tile in discarded_tile_list
            if tile != Tile(99)  # Tile(99) is the minus-point tile
        ]

    def __repr__(self) -> str:
        points = f"Total points: {self.point_total}."
        minus = f"This round's minus points (floor line): {self.floor_line}"
        in_round = f"Pattern lines: {self.pattern_lines}"
        end_round = f"Wall: {self.wall}"

        return "\n".join([points, minus, in_round, end_round])
