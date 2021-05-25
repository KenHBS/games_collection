# TODO: Handle round ends in TheGame
# TODO: Add logging

from typing import Dict, List
import time
from random import choice
from itertools import cycle

from game_pieces import TheMiddle, Pouch, Factory
from tiles import Tile, TileCounter
from player import Player


class TheGame:

    factory_count_mapping = {
        2: 5,
        3: 7,
        4: 9
    }

    def __init__(
        self,
        player_names: List[str],
    ):
        self.players = {name: Player(name) for name in player_names}
        self.starting_player = choice(player_names)
        self.current_player = self.starting_player

        self.pouch = Pouch()
        self.the_middle = TheMiddle()
        self.factories = self._fill_factories()

        self.player_cycle = cycle(player_names)
        self._move_to_starting_player()

    def play_round(self) -> None:
        while not self.round_has_ended:
            for player_name in self.player_cycle:
                self.current_player = player_name
                self.run_current_player_turn()

    def run_current_player_turn(self) -> None:
        """ Complete a player's turn """
        time.sleep(1)
        self.show_turn_start_message()

        while True:
            from_the_middle = input("Are you picking from the middle? (y/n) ")
            if from_the_middle.lower() == "y":
                self.player_pick_tile_from_middle()
                break
            elif from_the_middle.lower() == "n":
                self.player_pick_tile_from_factory()
                break
            else:
                print("Please use 'n' or 'y' to respond..")

    def player_pick_tile_from_factory(self) -> None:
        factory_nr = int(input("What factory are you choosing from? "))
        style = int(input("What tile type or you picking? (0=black, 1=blue, 2=red, 3=yellow, 4=white) "))

        tile = Tile(style)

        tile_count = self.factories[factory_nr].pop(tile)
        tile_counter = TileCounter(tile, tile_count)

        # Add factory leftovers to the middle
        factory_leftover = self.factories[factory_nr]
        for k, v in factory_leftover.items():
            self.the_middle[k] += v

        # Make sure that the factory is empty
        self.factories[factory_nr] = Factory()

        # Add tiles to player's pattern lines
        self.players[self.current_player].board.add_tile_count(tile_counter)

    def player_pick_tile_from_middle(self) -> None:
        """
        Handle everything if a player choses to draw from the middle.
        This includes taking the starting player marker, but also removing tile
        type from the middle and adding it to the pattern lines
        """
        if self.the_middle.is_untouched:
            self.starting_player = self.current_player
            self.the_middle.is_untouched = False
            minus_counter = TileCounter(Tile(99), 1)
            self.players[self.current_player].board.floor_line += minus_counter

        style = int(input("What tile type or you picking? (0=black, 1=blue, 2=red, 3=yellow, 4=white) "))
        tile = Tile(style)

        tile_count = self.the_middle.pop(tile)
        tile_counter = TileCounter(tile, tile_count)

        self.players[self.current_player].board.add_tile_count(tile_counter)

    def show_turn_start_message(self) -> None:
        """ At the start of each turn this message is shown """
        factories = '\n'.join(f" {k}: {v}" for k, v in self.factories.items())
        print("\n")
        print("-" * 50)
        print("\n")
        print(f"{self.current_player} it's your turn!")
        print(f"Factories:\n{factories}")
        print(f"The middle:\n{self.the_middle}")
        print(f"Your board:\n{self.players[self.current_player].board}")

    def _fill_factories(self) -> Dict[int, Factory]:
        """ Fill all factories with 4 tiles each from the pouch """
        factory_count = TheGame.factory_count_mapping[len(self.players)]
        return {i: self._fill_factory() for i in range(factory_count)}

    def _fill_factory(self) -> Factory:
        """ Fill a factory with 4 tiles from the pouch """
        factory = Factory()
        four_tiles = self.pouch.take_four()
        for tile in four_tiles:
            factory[tile] += 1
        return factory

    def _move_to_starting_player(self) -> None:
        """ Iterate through player cycle until starting player is found """
        for player_name in self.player_cycle:
            if player_name == self.starting_player:
                break

    @property
    def round_has_ended(self) -> bool:
        """Check if all factories and the middle are empty. If so, the current
        round is done. """
        check1 = all(factory.is_empty for factory in self.factories.values())
        check2 = self.the_middle.is_empty

        return check1 & check2

    @property
    def game_will_end(self) -> bool:
        """ Check if at least 1 player already has one entire row filled in
        their end-state tile area """
        return any(
            player.board.wall.is_finished
            for player in self.players
        )
