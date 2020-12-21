from Game import Game
import numpy as np
import time
import sys

class GameWrapper:
    def __init__(self, size, block_positions, starts, player_1, player_2, 
                terminal_viz, print_game_in_terminal, 
                time_to_make_a_move=2, game_time=100, 
                penalty_score=300, max_fruit_score=300, max_fruit_time=15):
        """Initialize the game wrapper and the initial board state with parameters.
        input:
            - size: the size of the board.
            - block_positions: positions blocked on the board.
            - starts: the players start positions.
            - player_1, player_2: players objects (such as LivePlayer object).
            - terminal_viz: bool. Show game in terminal only if true.
            - print_game_in_terminal: bool. Show only the winner and final scores if false.
            - time_to_make_a_move: time for a single turn.
            - game_time: total time for each player's game.
            - penalty_score: when a player get stuck or its time is up, it is penalized by this value. 
            - max_fruit_score: max score for a fruit.
            - max_fruit_time: max time for a fruit to be on board.
        """

        # check that each Player implements the following methods:
        self.players = [player_1, player_2]
        for player in self.players:
            assert hasattr(player, 'set_game_params')
            assert hasattr(player, 'make_move')
            assert hasattr(player, 'set_rival_move')
            assert hasattr(player, 'update_fruits')

        self.print_game_in_terminal = print_game_in_terminal
        self.terminal_viz = terminal_viz
        self.time_to_make_a_move = time_to_make_a_move
        self.penalty_score = penalty_score
        self.some_player_cant_move = False
        
        
        self.game_time_left_for_players = [game_time, game_time]

        initial_board = self.set_initial_board(size, block_positions, starts)

        self.game = Game(initial_board, starts, max_fruit_score=max_fruit_score, max_fruit_time=max_fruit_time, 
                        animated=True, animation_func=self.animate_func)

        for i, player in enumerate(self.players):
            player.set_game_params(self.game.get_map_for_player_i(player_id=i))
        

    def start_game(self):
        if self.terminal_viz:
            self.t = 0
            self.run_game()
        else:
            self.game.start_game()

    def check_cant_move_penalize(self, player_index):
        if self.game.player_cant_move(player_index):
            self.game.penalize_player(player_index, self.penalty_score)
            return True
        return False

    def check_cant_move_end_game(self, player_index):

        if player_index and self.some_player_cant_move:
            score_1, score_2 = self.game.get_players_scores()
            if score_1 == score_2:
                messages = ["     It's a Tie!", f'scores: {score_1}, {score_2}']
            else:
                winning_player = int(score_2 > score_1) + 1
                messages = [f'    Player {winning_player} Won!', f'scores: {score_1}, {score_2}']

            self.pretty_print_end_game(messages)

    def play_turn(self, player_index):
        # get fruits on board - we assume each player can see the board at any time
        fruits_on_board_dict = self.game.get_fruits_on_board()
        self.players[player_index].update_fruits(fruits_on_board_dict)
        players_score = self.game.get_players_scores().copy()
        if player_index:
            players_score.reverse()
        start = time.time()
        move = self.players[player_index].make_move(self.time_to_make_a_move, players_score)
        end = time.time()
        time_diff = end - start

        # reduce time from global time
        self.game_time_left_for_players[player_index] -= time_diff

        if time_diff > self.time_to_make_a_move or self.game_time_left_for_players[player_index] <= 0:
            self.game.penalize_player(player_index, self.penalty_score)
            player_index_time_up = player_index+1
            score_1, score_2 = self.game.get_players_scores()
            
            if score_1 == score_2:
                messages = [f'Time Up For Player {player_index_time_up}', 
                            f"     It's a Tie!", f'scores: {score_1}, {score_2}']
            else:
                winning_player = int(score_2 > score_1) + 1
                messages = [f'Time Up For Player {player_index_time_up}', 
                            f'    Player {winning_player} Won!', f'scores: {score_1}, {score_2}']
            self.pretty_print_end_game(messages)
        
        prev_pos = self.game.get_player_position(player_index)
        # print('player is at pos', prev_pos)
        pos = (prev_pos[0] + move[0], prev_pos[1] + move[1])
        # print('Player', player_index + 1, 'moved to', pos)
        assert self.game.check_move(pos), 'illegal move'
        self.players[1 - player_index].set_rival_move(pos)

        return pos

    ###################### animated game ######################

    def animate_func(self, t):
        if t < 2:
          return self.game.get_starting_state()

        player_index = t % 2
        # print('TURN', t, 'player', player_index + 1)
        cant_move = self.check_cant_move_penalize(player_index)
        if cant_move:
            pos = self.game.get_player_position(player_index)
            self.some_player_cant_move = True
        else:
            pos = self.play_turn(player_index)
        updated_position = self.game.update_staff_with_pos(pos)
        self.check_cant_move_end_game(player_index)
        return updated_position

    ################## game in terminal only ##################

    def run_game(self):
        while True:
            if self.t == 0 and self.print_game_in_terminal:
                print('\nInitial board:')
                self.game.print_board_to_terminal(player_id=0)
            player_index = self.t % 2
            # print('TURN', t, 'player', player_index + 1)
            cant_move = self.check_cant_move_penalize(player_index)
            if cant_move:
                pos = self.game.get_player_position(player_index)
                self.some_player_cant_move = True
            else:
                pos = self.play_turn(player_index)
            self.game.update_staff_with_pos(pos)
            self.check_cant_move_end_game(player_index)
            if self.print_game_in_terminal:
                print('\nBoard after player', player_index + 1, 'moved')
                self.game.print_board_to_terminal(player_id=0)
            self.t += 1
    
    
    ################## helper functions ##################
    @staticmethod
    def set_initial_board(size, block_positions, starts):
        board = np.zeros(size)
        for i, j in block_positions:
            board[i][j] = -1

        for player_index, (i, j) in enumerate(starts):
            board[i][j] = player_index + 1
        
        return board
    
    @staticmethod
    def pretty_print_end_game(messages):
        print('####################')
        print('####################')
        for message in messages:
            print(message)
        print('####################')
        print('####################')
        sys.exit(0)