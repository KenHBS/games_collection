from collections import Counter
from dataclasses import dataclass, field
import logging
import random
from typing import Any, List, NamedTuple, Tuple


logging.basicConfig(level=10, format="%(message)s")
handler = logging.FileHandler(filename="quartet_minimal.log", mode="w")
LOGGER = logging.getLogger("quartet_logger")
LOGGER.addHandler(handler)


class Card(NamedTuple):
    # NamedTuple: advantage of automatic implementation of dunder methods.
    # In particular, __hash__ and __eq__ are created automatically, so Card
    # can be used as a dictionary key -> for "knowledge" and "card location"

    group: str
    number: int

    def __repr__(self) -> str:
        return f"{self.group}-{self.number}"


FULL_DECK = [Card(group, int(nr)) for group in "ABCDE" for nr in range(1, 5)]


class Hand(list):
    """Collection of cards, with some added functionality compared to a list"""

    @property
    def quartets(self) -> List[str]:
        """ Return list with card group that have a full quartet """
        return [k for k, v in self.group_counter.items() if v == 4]

    @property
    def group_counter(self) -> Counter:
        """ Returns the number of cards per quartet group """
        return Counter(card.group for card in self)


@dataclass
class Player:
    name: str
    hand: Hand = field(default_factory=Hand)
    points: int = 0

    @property
    def is_finished(self) -> bool:
        return len(self.hand) == 0

    @property
    def eligible_cards(self):
        return [
            card
            for card in FULL_DECK
            if card not in self.hand
            if card.group in self.hand.group_counter.keys()
        ]

    def choose_card(self) -> Card:
        """ Pick a card to ask for """
        LOGGER.info(f"{self.name} can ask for {len(self.eligible_cards)} cards")
        return random.choice(self.eligible_cards)

    def choose_player(self, card: Card, players: List["Player"]) -> "Player":
        """ Choose which player to ask for <card> """
        return random.choice([player for player in players if player != self])


class QuartetGame:
    def __init__(self, players: List[Player]):
        self.players = players
        self.deck = random.sample(FULL_DECK, len(FULL_DECK))

        self.round_nr = 1
        self._current_player = self.players[0]

    def simulate_game(self) -> None:
        """ Simulate the game of quartet """
        player_names = ", ".join(p.name for p in self.players)
        LOGGER.info(f"Players at the table: {player_names}")
        LOGGER.info(f"Let the games begin!")

        # Set up the game:
        self.deal_cards()
        self.handle_players_quartet()

        # Go through the rounds until nobody's in the game
        while len(self.in_game_players) > 1:
            # Round start logging:
            LOGGER.info(f"\nStarting round # {self.round_nr} ...")
            LOGGER.info("\n".join(f"{k.name}: {k.hand}" for k in self.players))

            current_player = self._current_player

            asked_player, asked_card = self.generate_request(current_player)

            # Handle the successful / unsuccesful request:
            success_request = asked_card in asked_player.hand
            if success_request:
                asked_player.hand.remove(asked_card)
                current_player.hand.append(asked_card)

                name1, name2 = current_player.name, asked_player.name
                LOGGER.info(f"{name1} gets {asked_card} from {name2}")

            elif not success_request:
                LOGGER.info(f"{asked_player.name} does not have {asked_card}")

            # Clean up full quartets and finished players:
            self.handle_players_quartet()

            # Update public knowledge (not implemented)
            # Determine next round's starting player:
            _next = self.who_is_next(success_request, current_player, asked_player)
            self._current_player = _next

            self.round_nr += 1

        # Finish up the game
        LOGGER.info(f"\nThe game finished after {self.round_nr} rounds!")
        msg = "\n".join(f"{k.name} has {k.points} quartets" for k in self.players)
        LOGGER.info(msg)

    def who_is_next(self, success: bool, player1: Player, player2: Player) -> Player:
        """ Resolve next starter. randomly draw next player """
        up_next = player1 if success else player2
        if up_next.is_finished:
            try:
                up_next = random.choice(self.in_game_players)
            except IndexError:
                return None
        LOGGER.info(f"Next round it will be {up_next.name}'s turn")
        return up_next

    def deal_cards(self) -> None:
        """ Give each player starting cards """
        random.shuffle(self.deck)
        cards_piles = [self.deck[i::4] for i in range(4)]
        for player, card_pile in zip(self.players, cards_piles):
            player.hand = Hand(card_pile)

    def generate_request(self, player: Player) -> Tuple[Player, Card]:
        """ Let the player decide which card gets asked from whom """

        asked_card = player.choose_card()
        asked_player = player.choose_player(
            card=asked_card, players=self.in_game_players
        )

        LOGGER.info(f"{player.name} asks {asked_player.name}: {asked_card}")
        return (asked_player, asked_card)

    def handle_players_quartet(self) -> None:
        """ Remove quartets from players' hands and credit a point """
        for player in self.players:
            for quartet in player.hand.quartets:
                LOGGER.info(f"{player.name} has a quartet with {quartet}!")

                quartet_cards = [c for c in player.hand if c.group == quartet]
                player.hand = Hand(c for c in player.hand if c not in quartet_cards)
                player.points += 1

                LOGGER.info(f"{player.name} is putting down {quartet_cards}")

    @property
    def in_game_players(self) -> List[Player]:
        """ Returns list of players who still have cards in their hand """
        return [p for p in self.players if not p.is_finished]


if __name__ == "__main__":
    names = ["Pieter", "David", "Shawn", "Sebastian"]
    players = [Player(name=name) for name in names]

    quartet = QuartetGame(players=players)
    quartet.simulate_game()
    print(f"\nFinished the game in {quartet.round_nr} rounds")
