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
                'shown_card': None,
                'shown_value': None,
                'hand': [],
                'hand_value': 0,
                'winner': None
            }
        }

        # Humans are 1-based
        for player in range(1, num_players + 1):
            self.players['player_' + str(player)] = {
                'bank': 1000,   # Change this to come from a passed in dictionary
                'bet': self.min_bet,
                'hand': [],
                'hand_value': 0,
                'winner': -1
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
            'Ace': 11
        }

    def set_game_state(self):
        # This will be used later to get the data from the camera
        pass

    def get_all_players(self):
        return list(self.players.keys())

    def get_non_dealer_players(self):
        players = self.get_all_players()
        players.remove('dealer')
        return players

    def deal(self):
        # Players
        for player in self.get_non_dealer_players():
            # Not sure the best way to iterate over twice without a separate loop
            # so here we are
            self.players[player]['hand'].clear()
            self.players[player]['hand'].append(self.get_card())
            self.players[player]['hand'].append(self.get_card())

        # Dealer
        shown_card = self.get_card()
        hidden_card = self.get_card()

        self.players['dealer']['hand'].clear()
        self.players['dealer']['hand'].append(shown_card)
        self.players['dealer']['hand'].append(hidden_card)
        self.players['dealer']['shown_card'] = shown_card

        self.calculate_hand_values()

    def check_blackjack(self, player):
        return self.get_player_hand_value(player) == 21

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
        shown_card = self.players['dealer']['shown_card']
        self.players['dealer']['shown_value'] = self.card_values[shown_card]
        for player in self.get_all_players():
            self.update_hand_value(player)

    def get_player_hand_value(self, player):
        return self.players[player]['hand_value']

    def evaluate_hands(self):
        self.set_winners()
        for player in self.get_non_dealer_players():
            winner = self.players[player]['winner']
            self.players[player]['bank'] += winner * self.players[player]['bet']

    def reset_winners(self):
        players = self.get_all_players()
        for player in players:
            self.players[player]['winner'] = None

    def set_winners(self):
        self.reset_winners()
        players = self.get_non_dealer_players()

        # Check for player bust first
        for player in players:
            if self.players[player]['hand_value'] > 21:
                self.players[player]['winner'] = -1

        dealer_value = self.players['dealer']['hand_value']
        # check dealer bust second
        if dealer_value > 21:
            for player in players:
                if not self.players[player]['winner']:
                    self.players[player]['winner'] = 1
        else:
            # compare scores
            for player in players:
                if not self.players[player]['winner']:
                    self.players[player]['winner'] = -1
                    if self.players[player]['hand_value'] == dealer_value:
                        self.players[player]['winner'] = 0
                    if self.players[player]['hand_value'] > dealer_value:
                        self.players[player]['winner'] = 1

    def print_hand(self, player):
        for card in self.players[player]['hand']:
            print(card, end='\t')
        print('\nValue: ' + str(self.players[player]['hand_value']))

    def print_round(self, round_over=False):
        print('------------------------------------')
        print('Dealer:')
        if round_over:
            print('Hand: ', end='\t')
            self.print_hand('dealer')
        else:
            dealer_card = self.players['dealer']['shown_card']
            dealer_value = self.players['dealer']['shown_value']

            print('Shown Card:\t' + dealer_card)
            print('Value:\t' + str(dealer_value))

        players = self.get_non_dealer_players()

        for player in players:
            print('------------------------------------')
            print(player + ':')
            print('Hand: ', end='\t')
            self.print_hand(player)
            if round_over:
                if self.players[player]['winner'] == -1:
                    print('FAIL')
                if self.players[player]['winner'] == 0:
                    print('PUSH')
                if self.players[player]['winner'] == 1:
                    print('WIN')



            print('Current Bet:\t' + str(self.players[player]['bet']))
            print('Bank:\t' + str(self.players[player]['bank']))
