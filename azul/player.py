from game_pieces import Pouch
from board import PlayerBoard


class Player:
    def __init__(self, name: str):
        self.name = name
        self.board = PlayerBoard()

    def handle_round_end(self, pouch: Pouch) -> None:
        """ Trigger PlayerBoard.handle_round_end and return tiles to pouch """
        to_be_discarded_tiles = self.board.handle_round_end()
        for tile_counter in to_be_discarded_tiles:
            pouch += tile_counter

    def __repr__(self) -> str:
        return f"{self.name}: {self.board.point_total} points"
