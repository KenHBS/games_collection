from typing import List


class Tile(str):
    # Union["\U0000203B", "\U00002021", "\U00002051", "\U00002050", "\U000020AA"]
    pass
    

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

        self.inner_round_tile_area = InnerRoundTileArea()
        self.end_state_tile_area = EndStateTileArea()
        self.inner_round_minus_points = InnerRoundMinusPoints()


class InnerRoundTileArea:
    """
    The inner-round title area is located on each player's board.

    This area contains:
    - 5 rows with 1, 2, 3, 4 and 5 spaces to put tiles

    Each row can only contain a single type of tile.

    Tiles are added to this area by picking up tiles from the SharedBoard
    Tiles are removed from this area at the end of a round. This is done by:
    - moving a single tile of the row over to the EndStateTileArea of the PlayerBoard.
    - moving the remainder of the tiles (if any) back into the tile pool.
    Note that this action may only happen when the rows in the InnerRoundTileArea is completely filled
    """
    pass


class EndStateTileArea:
    """
    The end-state tile area is located on each player's board.

    This area contains:
    - 5x5 grid with spaces to put tiles

    Tiles are added to this area by moving.
    Tiles are never removed from this area.

    Note that:
    - no tile type can occur more than once in any row / column in the grid.
    - when moving tiles into the end-state tile area from the inner-round tile area,
        the 'eligible' row in the end-state tile area is determined by the row in the
        inner-round tile area.
    - when moving tiles into this area, the owner of the board is rewarded points. The
        number of points is based on the number of tiles in the end-state tile area that
        are directly adjacent to the newly added tile.
    """


class InnerRoundMinusPoints(List[Tile]):
    """
    Whenever a player takes tiles from the SharedBoard, but isn't able to place them
    in their inner-round tile area (there are multiple reasons), the player is penalised.

    At the end of each round, the inner-round minus point
    area is cleared of its tiles and the minus point are deducted from the player's round point total.

    The penalty for adding tiles to the negative point area increases when more tiles are added to the
    inner-round minus point area. This increasing penalty is captured by `negative_point_mapping`
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

    def count_minus_points(self) -> int:
        x = self.__len__()
        return InnerRoundMinusPoints.negative_point_mapping.get(x, 14)
