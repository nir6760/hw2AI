"""
MiniMax Player with AlphaBeta pruning with heavy heuristic
"""
from players.AbstractPlayer import AbstractPlayer

# TODO: you can import more modules, if needed
import numpy as np
import SearchAlgos as sa
import utils


# from utils import State

class Player(AbstractPlayer):
    def __init__(self, game_time, penalty_score):
        AbstractPlayer.__init__(self, game_time,
                                penalty_score)  # keep the inheritance of the parent's (AbstractPlayer) __init__()
        # TODO: initialize more fields, if needed, and the AlphaBeta algorithm from SearchAlgos.py
        self.board = None  # player1 is my player
        self.pos_players = None  # tuple [0]-player1 pos, [1] -player2 pos
        self.strategy = sa.AlphaBeta(utility=self.utility, succ=utils.State.succ, retriveLast=utils.State.retriveLast,
                                     goal=utils.State.goal)
        self.num_of_turns = (0, 0)  # tuple [0]-player1 turns, [1] -player2 turns
        self.fruits_on_board = None
        self.little_edge = 0

    def set_game_params(self, board):
        """Set the game parameters needed for this player.
        This function is called before the game starts.
        (See GameWrapper.py for more info where it is called)
        input:
            - board: np.array, a 2D matrix of the board.
        No output is expected.
        """
        # TODO: erase the following line and implement this function.
        self.board = board.copy()
        self.little_edge = min(np.size(self.board, 0), np.size(self.board, 1))
        self.pos_players = self.findPos

    def make_move(self, time_limit, players_score):
        """Make move with this Player.
        input:
            - time_limit: float, time limit for a single turn.
        output:
            - direction: tuple, specifing the Player's movement, chosen from self.directions
        """
        # TODO: erase the following line and implement this function.
        depth = 2  # this is changing depand on expriment
        player1_turn = True
        try:
            move_direction = self.strategy.search(
                utils.State(np.copy(self.board), player1_turn, players_score, self.num_of_turns,
                            self.fruits_on_board.copy(),
                            self.pos_players),
                depth, True)[1]
        except RuntimeError:  # if we dont have time even to one step minimax
            move_direction = utils.State.firstLegal(self.board, self.pos_players[0])
        if move_direction is None:
            move_direction = utils.State.firstLegal(self.board, self.pos_players[0])
        # preform move
        my_player_pos = self.pos_players[0]
        my_player_new_pos = (my_player_pos[0] + move_direction[0], my_player_pos[1] + move_direction[1])
        self.perform_move_on_selfPlayer(True, my_player_new_pos)

        return move_direction

    def set_rival_move(self, rival_new_pos):
        """Update your info, given the new position of the rival.
        input:
            - pos: tuple, the new position of the rival.
        No output is expected
        """
        # TODO: erase the following line and implement this function.
        self.perform_move_on_selfPlayer(False, rival_new_pos)

    def update_fruits(self, fruits_on_board_dict):
        """Update your info on the current fruits on board (if needed).
        input:
            - fruits_on_board_dict: dict of {pos: value}
                                    where 'pos' is a tuple describing the fruit's position on board,
                                    'value' is the value of this fruit.
        No output is expected.
        """
        # TODO: erase the following line and implement this function. In case you choose not to use this function,
        # use 'pass' instead of the following line.
        self.fruits_on_board = fruits_on_board_dict

    ########## helper functions in class ##########
    # TODO: add here helper functions in class, if needed
    # find the position of the players in this current state , return tuple
    # tuple [0]- player1 (player which his position represents by 1)
    # tuple [1]- player1 (player which his position represents by 1)
    @property
    def findPos(self):
        pos1, pos2 = None, None
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                if self.board[row][col] == 1:
                    pos1 = row, col
                if self.board[row][col] == 2:
                    pos2 = row, col
        return pos1, pos2

    # perform move to given direction by player
    def perform_move_on_selfPlayer(self, my_turn, new_pos):
        # board
        # pos
        # turnes
        # fruits
        my_pos = self.pos_players[0]
        rival_pos = self.pos_players[1]
        if my_turn:  # This is my turn to perform on self board
            self.board[my_pos] = -1
            self.board[new_pos] = 1
            self.pos_players = (new_pos, rival_pos)
            self.num_of_turns = (self.num_of_turns[0] + 1, self.num_of_turns[1])

        else:  # This is rival turn
            self.board[rival_pos] = -1
            self.board[new_pos] = 2
            self.pos_players = (my_pos, new_pos)
            self.num_of_turns = (self.num_of_turns[0], self.num_of_turns[1] + 1)

        if self.fruits_on_board is not None: self.fruits_on_board.pop(new_pos, 0)

    ########## helper functions for MiniMax algorithm ##########
    # TODO: add here the utility, succ, and perform_move functions used in MiniMax algorithm

    # calculate heuristic function of state as we explained in the dry part
    def utility(self, state):
        option = utils.State.opCount(state.board, state.pos_players[0]), utils.State.opCount(state.board,
                                                                                             state.pos_players[1])
        player = 0 if state.player1_play else 1
        cond = state.num_of_turns[player] <= self.little_edge and state.fruits_on_board_dict != {} #true if there are fruits
        score_diff = (state.players_score[0] - state.players_score[1])
        if utils.State.goal(state):
            if option[0] == 0:  # my player cant move, Im stuck
                score_diff -= self.penalty_score  # I deserve a penalty
            if option[1] == 0: # rival player stuck, he stuck
                    score_diff += self.penalty_score  # we both deserve penalty
            if score_diff == 0:  # tie
                return 0
            if score_diff < 0:  # I lost
                return score_diff
            res = 10000
            return res
        my_option_factor = (4 - option[0]) if option[0] != 0 else 0
        if option[0] == 0:
            score_diff -= self.penalty_score
        score_factor = score_diff
        my_BigOption_factor = utils.State.searchForBlock(state.board, state.pos_players[0], 0, 10) / 100
        if my_BigOption_factor == 0.1:  # no boundary
            my_BigOption_factor = 1
        #rival_BigOption_factor = utils.State.searchForBlock(state.board, state.pos_players[1], 0, 7) / 70
        #if rival_BigOption_factor == 0.1:  # no boundary
        #    rival_BigOption_factor = 1
        #go_to_rival = 2*utils.State.manhattan(state.pos_players[0], state.pos_players[1])/(np.size(self.board, 0)+np.size(self.board, 1))
        fruit_fac = 0
        max_fruit = 1
        if cond:
            fruit_fac = max(value/utils.State.manhattan(state.pos_players[0], key)
                               for key, value in state.fruits_on_board_dict.items())
            max_fruit = max(value for value in state.fruits_on_board_dict.values())
        fruit_factor = 20 * fruit_fac/max_fruit
        return my_option_factor + score_factor + fruit_factor + my_BigOption_factor

