from collections import Counter
from dataclasses import dataclass, field
import logging
import random
from typing import Any, List, NamedTuple, Tuple


logging.basicConfig(level=10, format="%(message)s")
handler = logging.FileHandler(filename="quartet_clever.log", mode="w")
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
    decision_policy: str = "random"
    # Also semi-random and pretty-smart

    def __hash__(self):
        return hash(name) * hash(decision_policy)

    @property
    def is_finished(self) -> bool:
        return len(self.hand) == 0

    @property
    def eligible_cards(self) -> List[Card]:
        return [
            card
            for card in FULL_DECK
            if card not in self.hand
            if card.group in self.hand.group_counter.keys()
        ]

    @property
    def eligible_cards_ranked(self):
        # to avoid getting the same cards in case of tie
        shuffled_cards = random.sample(self.eligible_cards, len(self.eligible_cards))

        return sorted(
            (card for card in shuffled_cards),
            key=lambda card: self.hand.group_counter[card.group],
            reverse=True,
        )

    def choose_card(self, knowledge: Any = None) -> Card:
        """ Pick a card to ask for """
        LOGGER.info(f"{self.name} can ask for {len(self.eligible_cards)} cards")
        if self.decision_policy == "random":
            return random.choice(self.eligible_cards)

        elif self.decision_policy == "semi-random":
            return self.eligible_cards_ranked[0]

        elif self.decision_policy == "pretty-smart":
            # Check for the best card we know the location of
            candidate = next(
                (
                    card
                    for card in self.eligible_cards_ranked
                    if knowledge[card].get("owned_by") is not None
                ),
                None,
            )
            # If not working, check for best card, we know is not owned by
            if candidate is None:
                candidate = next(
                    (
                        card
                        for card in self.eligible_cards_ranked
                        if knowledge[card].get("not_owned_by") is not None
                    ),
                    None,
                )
            # If not working, pick the self-focused best card
            if candidate is None:
                candidate = self.eligible_cards_ranked[0]

            return candidate
        else:
            msg = f""" decision policy "{self.decision_policy}" does not exists.
            Use 'random', 'semi-random' or 'pretty-smart' instead"""
            raise NotImplementedError(msg)

    def choose_player(
        self, card: Card, players: List["Player"], knowledge: Any = None
    ) -> "Player":
        """ Choose which player to ask for <card> """
        if self.decision_policy in ("random", "semi-random"):
            return random.choice([p for p in players if p != self])

        elif self.decision_policy == "pretty-smart":
            try:
                return knowledge[card]["owned_by"]
            except KeyError:
                try:
                    not_ = knowledge[card]["not_owned_by"]
                    return random.choice([p for p in players if p not in (self, not_)])
                except KeyError:
                    return random.choice([p for p in players if p != self])

        else:
            msg = f""" decision policy "{self.decision_policy}" does not exists.
            Use 'random', 'semi-random' or 'pretty-smart' instead"""
            raise NotImplementedError(msg)


class QuartetGame:
    def __init__(self, players: List[Player]):
        self.players = players
        self.deck = random.sample(FULL_DECK, len(FULL_DECK))

        self.round_nr = 1
        self._current_player = self.players[0]
        self.public_knowledge = {card: {"not_owned_by": []} for card in FULL_DECK}

    def simulate_game(self) -> None:
        """ Simulate the game of quartet """
        player_names = ", ".join(p.name for p in self.players)
        LOGGER.info(f"Players at the table: {player_names}")
        LOGGER.info(
            "\n".join(f"{p.name}'s policy: {p.decision_policy}" for p in self.players)
        )
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
                self.public_knowledge[asked_card]["owned_by"] = current_player
                self.public_knowledge[asked_card]["not_owned_by"] = []

            elif not success_request:
                LOGGER.info(f"{asked_player.name} does not have {asked_card}")
                self.public_knowledge[asked_card]["not_owned_by"].append(asked_player)
                self.public_knowledge[asked_card]["not_owned_by"].append(current_player)

            # Clean up full quartets and finished players:
            self.handle_players_quartet()

            # Update public knowledge (not implemented)
            # Determine next round's starting player:
            _next = self.who_is_next(success_request, current_player, asked_player)
            self._current_player = _next

            self.round_nr += 1

        # Finish up the game
        LOGGER.info(f"\nThe game finished after {self.round_nr-1} rounds!")
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
        knowledge = self.public_knowledge

        asked_card = player.choose_card(knowledge=knowledge)
        asked_player = player.choose_player(
            card=asked_card, players=self.in_game_players, knowledge=knowledge
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

    def update_public_knowledge(self):
        """ Not implemented. Could keep record of location of cards """
        pass

    @property
    def in_game_players(self) -> List[Player]:
        """ Returns list of players who still have cards in their hand """
        return [p for p in self.players if not p.is_finished]


if __name__ == "__main__":

    names = ["Pieter", "David", "Shawn", "Sebastian"]
    policies = ["pretty-smart", "pretty-smart", "random", "semi-random"]

    # To make sure I'm not mean to anybody ;-)
    random.shuffle(names)
    random.shuffle(policies)

    players = [Player(name=n, decision_policy=p) for n, p in zip(names, policies)]
    quartet = QuartetGame(players=players)

    quartet.simulate_game()
    print(f"\nFinished the game in {quartet.round_nr} rounds")
