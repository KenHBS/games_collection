from .factory import Factory


class TheMiddle(Factory):
    """ This class represents 'The Middle'.
    All tiles that are not picked up when a player picks up tiles from a
    factory are placed in the middle.

    TheMiddle behaves like a Factory, except:
    - the middle is empty at the beginning of a round,
    - the first player to draw from the middle is penalised with 1 minus point,
    - the first player to draw from the middle is the starting player
        in the next round.
    """
    def __init__(self):
        self.is_untouched = True
        super().__init__()

    def __repr__(self):
        content = super().__repr__()
        starter_marker = f"Contains start player marker: {self.is_untouched}"
        return f"{starter_marker}\n{content}"
