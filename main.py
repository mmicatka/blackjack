"""
Look how great this is commented
"""

import argparse

from src.blackjack import Blackjack

if __name__ == '__main__':
    print('Welcome to the command line interface of <Code Name Here>')

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--num_decks', type=int, default=1, help='number of decks')
    parser.add_argument('--num_players', type=int, default=1, help='number of players')

    args = parser.parse_args()

    game = Blackjack(args.num_decks)

    user_input = input('Deal (d)/Print Game State(p)/Quit (q):')

    while not game.reshuffle() and user_input != 'q':

        if user_input == 'p':
            print('Game state is as follows:')
            game.print_game_state()

        if user_input == 'd':
            game.deal()
            game.print_hands()

        user_input = input('Deal (d)/Print Game State(p)/Quit (q):')

    print('Game over.')

    # Display final statistics for player/bank

