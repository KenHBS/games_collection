from tiles import TileCounter, Tile
from game_pieces import Pouch, Factory, TheMiddle
from board import PlayerBoard
from typing import Optional


class Player:
    def __init__(self, name: str):
        self.name = name
        self.board = PlayerBoard()

    def pick_from_factory(
        self,
        draw_from: Factory,
        tile: Tile,
        the_middle: TheMiddle,
        add_tiles_to_row_nr: Optional[int] = None,
    ) -> TheMiddle:
        """
        Trigger a sequence of actions:
        - take tiles (all of 1 type) from a factory,
        - discard the other tile types to the middle.
        - add the picked up tiles to one of your pattern lines
        """
        # take tiles from a factory
        tile_count = draw_from.pop[tile]
        tile_counter = TileCounter(tile, tile_count)

        # discard the other tiles type to the middle
        the_middle = self.add_leftovers_to_middle(
            factory=draw_from,
            the_middle=the_middle
        )

        # add the picked up tiles to one of the pattern lines
        if add_tiles_to_row_nr is None:
            print(f"Moving {tile_counter} to your board!")
            print(f"Player board looks like {self.board}.")
            add_tiles_to_row_nr = int(input(f"Where to add {tile_counter}? "))

        self.board.add_tile_count(
            tiles=tile_counter,
            row_nr=add_tiles_to_row_nr
        )

        return the_middle

    def pick_from_middle(self, tile: Tile, the_middle: TheMiddle):
        """ Take tiles from the middle and add to player board """
        if the_middle.is_untouched:
            x_tile = Tile(99)
            the_middle.is_untouched = False
            self.board.pattern_lines += TileCounter(x_tile, 1)

        tile_count = the_middle.pop[tile]
        tile_counter = TileCounter(tile, tile_count)
        self.board.add_tile_count(tile_counter)

        return the_middle

    def add_leftovers_to_middle(
        self,
        leftovers: Factory,
        the_middle: TheMiddle
    ) -> TheMiddle:
        """ Add the leftover tiles in the factory to the middle """
        for k, v in leftovers.items():
            the_middle[k] += v
        return the_middle

    def handle_round_end(self, pouch: Pouch) -> None:
        """ Trigger PlayerBoard.handle_round_end and return tiles to pouch """
        to_be_discarded_tiles = self.board.handle_round_end()
        for tile_counter in to_be_discarded_tiles:
            pouch += tile_counter

    def __repr__(self) -> str:
        return f"{self.name}: {self.board.point_total} points"
