# TODO: Implement the PlayerBoard and how the different components interact
# with each other
# TODO: Figure out how "Plate" should be a list of tiles, list of TileCounter,
# # or a counter
# TODO: Figure out how Literal[range(5)] is supposed to be implemnented
# TODO: Add "is_start_player" for first draw from the middle
# TODO: Implement the 'middle'


from shared_resources import Pouch
from tiles import TileCounter
from inner_round_resources import InnerRoundTileArea, InnerRoundMinusPoints
from end_state_tile_area import EndStateTileArea
from typing import List


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
