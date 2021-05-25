from typing import Dict, List
from game_pieces import TheMiddle, Pouch, Factory
from player import Player


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
            player.board.wall.is_finished
            for player in self.players
        )
