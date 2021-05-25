# TODO: Create actual game to check / test how it works
# TODO: Figure out whether to standardise TileCounter, List(TileCounter) and
# Factories

from typing import Dict, List
from random import choice
from itertools import cycle

from game_pieces import TheMiddle, Pouch, Factory
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

        self.pouch = Pouch()
        self.the_middle = TheMiddle()
        self.factories = self._fill_factories()

        self.player_cycle = cycle(player_names)

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
        check1 = all(factory.is_empty() for factory in self.factories)
        check2 = self.the_middle.is_empty()

        return check1 & check2

    @property
    def game_will_end(self) -> bool:
        """ Check if at least 1 player already has one entire row filled in
        their end-state tile area """
        return any(
            player.board.wall.is_finished
            for player in self.players
        )
