"""
Look how great this is commented
"""

import random
import sys


class Blackjack(object):
    def __init__(
            self,
            num_decks=1,
            num_players=1,
            min_bet=5,
            seed=2018
    ):

        self.deck = None
        self.card_values = None
        self.cards_seen = None
        self.players = None

        self.min_bet = min_bet
        self.init_deck(num_decks)
        self.init_players(num_players)
        random.seed(seed)

    def init_players(self, num_players):
        self.players = {
            'dealer': {
                # We cannot 'break the bank'
                'bank': sys.float_info.max,
                'bet': None,
                'hand': [],
                'hand_value': 0
            }
        }

        # Humans are 1-based
        for player in range(1, num_players + 1):
            self.players['player_' + str(player)] = {
                'bank': 1000,   # Change this to come from a passed in dictionary
                'bet': self.min_bet,
                'hand': [],
                'hand_value': 0
            }

    def init_deck(self, num_decks):
        self.cards_seen = {}

        self.deck = {
            'Ace': 4 * num_decks,
            '2': 4 * num_decks,
            '3': 4 * num_decks,
            '4': 4 * num_decks,
            '5': 4 * num_decks,
            '6': 4 * num_decks,
            '7': 4 * num_decks,
            '8': 4 * num_decks,
            '9': 4 * num_decks,
            '10': 4 * num_decks,
            'J': 4 * num_decks,
            'Q': 4 * num_decks,
            'K': 4 * num_decks,
        }

        self.card_values = {
            'Ace': 1,
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5,
            '6': 6,
            '7': 7,
            '8': 8,
            '9': 9,
            '10': 10,
            'J': 10,
            'Q': 10,
            'K': 10,
        }

    def deal(self):
        for player in self.players:
            # Not sure the best way to iterate over twice without a separate loop
            # so here we are
            self.players[player]['hand'].append(self.get_card())
            self.players[player]['hand'].append(self.get_card())

        self.calculate_hand_values()

    def print_hand(self, player):
        for card in self.players[player]['hand']:
            print(card, end='\t')

    def print_all(self):
        for player in self.players:
            print(player + ':')
            print('Hand: ', end='\t')
            self.print_hand(player)
            print('\nValue: ' + str(self.players[player]['hand_value']))
            print('Current Bet:\t' + str(self.players[player]['bet']))
            print('Bank:\t' + str(self.players[player]['bank']))

            print()

    def get_players(self):
        return list(self.players.keys())

    def hit(self, player):
        self.players[player]['hand'].append(self.get_card())
        self.update_hand_value(player)

    def get_card(self):
        card = random.choice(list(self.deck.keys()))

        if self.deck[card] == 1:
            self.deck.pop(card)
        else:
            self.deck[card] -= 1

        return card

    def update_hand_value(self, player):
        self.players[player]['hand_value'] = 0
        for card in self.players[player]['hand']:
            self.players[player]['hand_value'] += self.card_values[card]

    def calculate_hand_values(self):
        for player in self.players:
            self.update_hand_value(player)

    def get_player_hand_value(self, player):
        return self.players[player]['hand_value']
