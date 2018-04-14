"""
This is the main driver
"""

import argparse
from blackjack import Blackjack


if __name__ == '__main__':
    print('Welcome to Blackjack Command Line Interface')

    # Add command line args later
    blackjack = Blackjack()

    blackjack.deal()
    blackjack.print_all()

    players = blackjack.get_players()

    while blackjack.get_player_hand_value('dealer') < 22:
        for player in players:
            if player != 'dealer':
                # make this work
                is_blackjack = False
                hit_or_stay = 'h'
                if not is_blackjack:
                    while (blackjack.get_player_hand_value(player) < 21) and (hit_or_stay != 's'):
                        # More options coming soon
                        hit_or_stay = input(player + ' Hit (h) or Stay (s): ')
                        if hit_or_stay == 'h':
                            blackjack.hit(player)

                        blackjack.print_hands()

            else:
                blackjack.hit('dealer')

        blackjack.print()



