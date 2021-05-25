# TODO: Implement TheGame class: start-player, player order, factory filling
# TODO: Align naming conventions with https://www.ultraboardgames.com/azul/game-rules.php
# TODO: Create actual game to check / test how it works
# TODO: Figure out whether to standardise TileCounter, List(TileCounter) and Factories


from shared_resources import Pouch, Factory, TheMiddle
from tiles import TileCounter, Tile
from inner_round_resources import InnerRoundTileArea, InnerRoundMinusPoints
from end_state_tile_area import EndStateTileArea
from typing import List, Optional, Dict


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

        self.inner_round_tile_area = InnerRoundTileArea()
        self.end_state_tile_area = EndStateTileArea()
        self.inner_round_minus_points = InnerRoundMinusPoints()

    def add_tile_count(self, tiles: TileCounter, row_nr: int) -> None:
        """
        Add tile counters to your inner-round area. If there is not enough
        capacity, the surplus tiles will be added to the minus point area
        """
        row = self.inner_round_tile_area.grid[row_nr]

        # handle surplus tiles
        if tiles.count > row.free_spaces:
            surplus_count = tiles.count - row.free_spaces
            surplus_tiles = TileCounter(tile=tiles.tile, count=surplus_count)

            self.inner_round_minus_points += surplus_tiles
            tiles.count = row.free_spaces

        self.inner_round_tile_area.grid[row_nr] += tiles

    def handle_round_end(self) -> List[TileCounter]:
        """
        Move tiles from inner-round area into end-state area,
        score minus points and return leftover tiles.
        """
        leftover_tiles1 = self.score_inner_round_tile_area()
        leftover_tiles2 = self.score_inner_round_minus_points()

        return [*leftover_tiles1, *leftover_tiles2]

    def score_inner_round_tile_area(self) -> List[TileCounter]:
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
                        print("You cannot place your tile there. Try again ..")
                    else:
                        break

                self.point_total += self.end_state_tile_area.count_points_tile(
                    row_nr=row_nr, col_nr=col_nr
                )

        return discarded_tiles_counter_container

    def score_inner_round_minus_points(self) -> List[TileCounter]:
        """
        Score and flush the minus point area. Returns a list with TileCounter
        that represent the discarded tiles.

        The method makes sure that the minus-tile (=Tile(99)) does not end up
        in the discarded tiles. The minus-point tile implicitly returns to
        TheMiddle (actually it is recreated whenever somebody takes a
        'first draw' from TheMiddle)
        """
        self.point_total -= self.inner_round_minus_points.count_minus_points

        discarded_tile_list = self.inner_round_minus_points[:]
        self.inner_round_minus_points = InnerRoundMinusPoints()

        return [
            TileCounter(tile, 1)
            for tile in discarded_tile_list
            if tile != Tile(99)  # Tile(99) is the minus-point tile
        ]

    def __repr__(self) -> str:
        points = f"Total points: {self.point_total}."
        minus = f"This round's minus points: {self.inner_round_minus_points}"
        in_round = f"Round tile area: {self.inner_round_tile_area}"
        end_round = f"End state tile area: {self.end_state_tile_area}"

        return "\n".join([points, minus, in_round, end_round])


class Player:
    def __init__(self, name: str):
        self.name = name
        self.board = PlayerBoard()

    def pick_from_factory(
        self,
        draw_from: Factory,
        tile: Tile,
        the_middle: Factory,
        add_tiles_to_row_nr: Optional[int] = None,
    ) -> TheMiddle:
        """
        Trigger a sequence of actions:
        - take tiles (all of 1 type) from a factory,
        - discard the other tile types to the middle.
        - add the picked up tiles to one of your inner-round-tile-area rows
        """
        # take tiles from a factory
        tile_count = draw_from.pop[tile]
        tile_counter = TileCounter(tile, tile_count)

        # discard the other tiles type to the middle
        the_middle = self.add_leftovers_to_middle(
            factory=draw_from,
            the_middle=the_middle
        )

        # add the picked up tiles to one of the inner-round-tile-area rows
        if add_tiles_to_row_nr is None:
            print(f"Moving {tile_counter} to your board!")
            print(f"Player board looks like {self.board}.")
            add_tiles_to_row_nr = input(f"Where to add {tile_counter}?")

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
            self.board.inner_round_minus_points += TileCounter(x_tile, 1)

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


class TheGame:

    factory_count = {
        2: 5,
        3: 7,
        4: 9
    }

    def __init__(self, player_names: List[str]):
        self.game_will_end = False

        self.players = [Player(name) for name in player_names]
        self.pouch = Pouch()
        self.the_middle = TheMiddle()

        self.factory_count = TheGame.factory_count_mapping(len(player_names))

    def fill_factories(self) -> Dict[int, Factory]:
        """ Fill the factories with 4 tiles """
        pass

    @property
    def game_will_end(self) -> bool:
        """ Check if at least 1 player already has one entire row filled in
        their end-state tile area """
        return any(
            player.board.end_state_tile_area.is_finished
            for player in self.players
        )
