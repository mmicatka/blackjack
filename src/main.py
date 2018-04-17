"""
This is the main driver
"""

import argparse
from blackjack import Blackjack


if __name__ == '__main__':
    print('Welcome to Blackjack Command Line Interface')

    min_bet = 10

    # Add command line args later
    blackjack = Blackjack(min_bet=min_bet)

    play_again = 'Y'

    while play_again == 'Y':

        if blackjack.needs_reshuffle():
            print('Reshuffling deck...')
            blackjack.reshuffle()

        players = blackjack.get_non_dealer_players()

        # Get bets
        for player in players:
            bet = int(input('Player: ' + str(player) + ' enter your bet (minimum is ' + str(min_bet) + '): '))
            if bet < 10:
                bet = 10

            blackjack.set_bet(player, bet)

        # Check for reshuffle here
        blackjack.deal()
        blackjack.print_round()

        # Handle dealer blackjack here
        for player in players:
            print('------------------------------------')
            move = 'h'
            bust = False
            if blackjack.check_blackjack(player):
                print('Blackjack! Sadly this is not implemented yet')
            else:
                while not bust and (move == 'h'):
                    # More options coming soon
                    move = input(player + ' Hit (h)/Stay (s)/Double Down (d)/Split (sp): ')
                    if move == 'h':
                        blackjack.hit(player)
                    if move == 'd':
                        blackjack.set_bet(player, blackjack.get_bet(player) * 2)
                        blackjack.hit(player)
                        move = 's'
                    if move == 'sp':
                        blackjack.split(player)

                    blackjack.print_hand(player)
                    bust = bool(blackjack.get_player_hand_value(player) > 21)

        print('------------------------------------')

        blackjack.print_hand('dealer')
        dealer_hand_value = blackjack.get_player_hand_value('dealer')
        # handle soft 17
        while (dealer_hand_value < 17) and (dealer_hand_value <= 21) or blackjack.is_soft_seventeen():
            print('------------------------------------')
            blackjack.hit('dealer')
            dealer_hand_value = blackjack.get_player_hand_value('dealer')
            blackjack.print_hand('dealer')

        blackjack.evaluate_hands()
        blackjack.print_round(round_over=True)

        print('------------------------------------')
        print('------------------------------------')

        play_again = input('Play again (Y/n): ')
