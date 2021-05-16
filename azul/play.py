from playerboard import PlayerBoard
from misc import TileCounter, Tile


if __name__ == "__main__":
    player_board = PlayerBoard("sinus")
    draw_this = TileCounter(Tile(2), 3)

    player_board.add_tile_count(draw_this, 3)
