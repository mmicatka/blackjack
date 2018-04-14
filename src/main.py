"""
This is the main driver
"""

import argparse
from blackjack import Blackjack


if __name__ == '__main__':
    print('Welcome to Blackjack Command Line Interface')

    # Add command line args later
    blackjack = Blackjack()

    play_again = 'Y'

    while play_again == 'Y':
        # Check for reshuffle here
        blackjack.deal()
        blackjack.print_round()

        players = blackjack.get_non_dealer_players()
        # Handle dealer blackjack here
        for player in players:
            print('------------------------------------')
            hit_or_stay = 'h'
            bust = False
            if blackjack.check_blackjack(player):
                print('Blackjack! Sadly this is not implemented yet')
            else:
                while not bust and (hit_or_stay == 'h'):
                    # More options coming soon
                    hit_or_stay = input(player + ' Hit (h) or Stay (s): ')
                    if hit_or_stay == 'h':
                        blackjack.hit(player)

                    blackjack.print_hand(player)
                    bust = bool(blackjack.get_player_hand_value(player) > 21)

        print('------------------------------------')

        blackjack.print_hand('dealer')
        dealer_hand_value = blackjack.get_player_hand_value('dealer')
        # handle soft 17
        while (dealer_hand_value < 17) and (dealer_hand_value <= 21):
            print('------------------------------------')
            blackjack.hit('dealer')
            dealer_hand_value = blackjack.get_player_hand_value('dealer')
            blackjack.print_hand('dealer')

        blackjack.evaluate_hands()
        blackjack.print_round(round_over=True)

        print('------------------------------------')
        print('------------------------------------')

        play_again = input('Play again (Y/n): ')
