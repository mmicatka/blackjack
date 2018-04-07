"""
Put some more info here

For blackjack the suit does not matter so we will ignore it. The cards are


"""

cards_one_suit = [
    'Ace',
    'Two',
    'Three',
    'Four',
    'Five',
    'Six',
    'Seven',
    'Eight',
    'Nine',
    'Ten',
    'Jack',
    'Queen',
    'King'
]


class Blackjack(object):

    def __init__(self, num_decks=1, num_players=1):
        self.deck = cards_one_suit * 4 * num_decks
        self.cards_seen = []
        self.reshuffle_point = 30  # This should be set in shuffle function
        self.hands = {
            'Dealer': []
        }

        for player in range(num_players):
            self.hands['Player ' + str(player)] = []

    def shuffle(self):
        pass

    def reshuffle(self):
        # This should be cleaned up a bit
        return bool(len(self.cards_seen) >= self.reshuffle_point)

    def deal(self):
        # Might be a better way to do this...
        for hands_dealt in range(2):
            for player in self.hands:
                card = self.get_card()
                self.hands[player].append(card)
                self.cards_seen.append(card)    # This needs to take into account the "hidden" dealer card

    def get_card(self):
        return self.deck.pop()

    def set_game_state(self):
        # Set this from a JSON or something
        pass

    def print_deck(self):
        for card in self.deck:
            print(card, end=' ')
        print()

    def print_hands(self):
        for player in self.hands:
            print(player + ':')
            for card in self.hands[player]:
                print(card, end=' ')
            print()

    def print_game_state(self):
        self.print_deck()
        self.print_hands()
