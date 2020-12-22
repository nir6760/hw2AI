"""
MiniMax Player
"""
from players.AbstractPlayer import AbstractPlayer
import numpy as np
import time
import SearchAlgos as sa
import utils


# TODO: you can import more modules, if needed
# represents a state of the game
class State:
    def __init__(self, board, player1_play, players_score, num_of_turns, fruits_on_board_dict, pos_players):
        """
        state initialization.
        """
        self.board = board
        self.player1_play = player1_play  # bool true if player1 turn, false when player2 turn
        self.players_score = players_score  # tuple [0]-player1 score, [1] -player2 score
        self.num_of_turns = num_of_turns  # tuple [0]-player1 turns, [1] -player2 turns
        self.fruits_on_board_dict = fruits_on_board_dict
        self.pos_players = pos_players  # tuple [0]-player1 pos, [1] -player2 pos

    """
    # find the position of the players in this self state , return tuple
    # tuple [0]- player1 (player which his position represents by 1)
    # tuple [1]- player1 (player which his position represents by 1)
    def findPos(self):
        pos1, pos2 = None, None
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                if self.board[row][col] == 1:
                    pos1 = row, col
                if self.board[row][col] == 2:
                    pos2 = row, col
        return pos1, pos2
    """

    # finds the manhatan distance between pos1 and pos2
    @staticmethod
    def manhattan(pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    # counts number of possible moves from pos on the board
    @staticmethod
    def opCount(board, pos):
        ops = 0
        for d in utils.get_directions():
            i = pos[0] + d[0]
            j = pos[1] + d[1]
            if 0 <= i < len(board) and 0 <= j < len(board[0]) and (board[i][j] not in [-1, 1, 2]):
                ops += 1
        return ops


# minimax strategy player class
class Player(AbstractPlayer):
    def __init__(self, game_time, penalty_score):
        AbstractPlayer.__init__(self, game_time,
                                penalty_score)  # keep the inheritance of the parent's (AbstractPlayer) __init__()
        # TODO: initialize more fields, if needed, and the Minimax algorithm from SearchAlgos.py
        self.board = None
        self.pos_players = None  # tuple [0]-player1 pos, [1] -player2 pos
        self.strategy = sa.MiniMax(utility=self.utility, succ=self.succ, perform_move=self.perform_move, goal=self.goal)
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
        # TODO:
        self.board = np.copy(board)
        self.little_edge = min(np.size(self.board, 0), np.size(self.board, 1))
        self.pos_players = self.findPos()

    def make_move(self, time_limit, players_score):
        """Make move with this Player.
        input:
            - time_limit: float, time limit for a single turn.
        output:
            - direction: tuple, specifing the Player's movement, chosen from self.directions
        """
        # TODO:

        move_direction = self.strategy.interruptible(
            State(np.copy(self.board), True, players_score, self.num_of_turns, self.fruits_on_board, self.pos_players),
            time_limit)[1]
        # preform move
        self.perform_move(move_direction)
        self.num_of_turns = (self.num_of_turns[0], self.num_of_turns[1] + 1)
        return move_direction

    def set_rival_move(self, pos):
        """Update your info, given the new position of the rival.
        input:
            - pos: tuple, the new position of the rival.
        No output is expected
        """
        # TODO:
        self.board[pos] = 2
        self.board[self.pos_players[1]] = 2
        self.pos_players = (self.pos_players[0], pos)
        self.num_of_turns = (self.num_of_turns[0], self.num_of_turns[1] + 1)

    def update_fruits(self, fruits_on_board_dict):
        """Update your info on the current fruits on board (if needed).
        input:
            - fruits_on_board_dict: dict of {pos: value}
                                    where 'pos' is a tuple describing the fruit's position on board,
                                    'value' is the value of this fruit.
        No output is expected.
        """
        # TODO:.
        if self.num_of_turns[0] == 0:
            self.fruits_on_board = fruits_on_board_dict
        if self.num_of_turns[0] == self.little_edge:  # we need to update it only once, when they disappear
            self.fruits_on_board = fruits_on_board_dict

    ########## helper functions in class ##########
    # TODO: add here helper functions in class, if needed
    # counts all the ones on board and returns it
    @staticmethod
    def count_ones(board):
        counter = len(np.where(board == 1)[0])
        return counter

    # return updated fruit dictionary after moving to direction by given player
    @staticmethod
    def fruitsDictAfterMove(fruits_on_board, pos):
        fruits_pos_val = fruits_on_board.copy()
        fruits_pos_val.pop(pos, 0)  # default value for pop without exception
        return fruits_pos_val

    # find the position of the players in this current state , return tuple
    # tuple [0]- player1 (player which his position represents by 1)
    # tuple [1]- player1 (player which his position represents by 1)

    def findPos(self):
        pos1, pos2 = None, None
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                if self.board[row][col] == 1:
                    pos1 = row, col
                if self.board[row][col] == 2:
                    pos2 = row, col
        return pos1, pos2

    ########## helper functions for MiniMax algorithm ##########
    # TODO: add here the utility, succ, and perform_move functions used in MiniMax algorithm
    # returnes list of the tuples, successor of state and the direction for this successor
    def succ(self, state):
        player1_play = state.player1_play
        curr_player_pos = state.pos_players[0] if player1_play else state.pos_players[1]
        curr_player_num_of_turns = state.num_of_turns[0] if player1_play else state.num_of_turns[1]
        for d in utils.get_directions():
            i = curr_player_pos[0] + d[0]
            j = curr_player_pos[1] + d[1]

            if 0 <= i < len(state.board) and 0 <= j < len(state.board[0]) and (
                    state.board[i][j] not in [-1, 1, 2]):  # then move is legal
                new_pos = (i, j)
                if player1_play:  # this state is player1 turn
                    succ_pos_players = (new_pos, state.pos_players[1])
                    succ_players_score = state.players_score[0] + state.fruits_on_board_dict.get(new_pos, 0), \
                                         state.players_score[1]
                    succ_num_of_turns = state.num_of_turns[0] + 1, \
                                        state.num_of_turns[1]
                else:  # this state is player2 turn
                    succ_pos_players = (state.pos_players[0], new_pos)
                    succ_players_score = state.players_score[0], \
                                         state.players_score[1] + state.fruits_on_board_dict.get(new_pos, 0)
                    succ_num_of_turns = state.num_of_turns[0], \
                                        state.num_of_turns[1] + 1
                succ_board = np.copy(state.board)

                succ_board[curr_player_pos] = -1  # perform move on succ_state board
                succ_board[new_pos] = 1 if player1_play else 2

                succ_fruits_on_board_dict = {}
                if curr_player_num_of_turns <= self.little_edge:
                    succ_fruits_on_board_dict = self.fruitsDictAfterMove(state.fruits_on_board_dict, new_pos)

                yield State(succ_board, not player1_play, succ_players_score,
                            succ_num_of_turns, succ_fruits_on_board_dict, succ_pos_players), d

    # check if state is in the final states group, means no possible moves for one of the competitors
    def goal(self, state):
        if State.opCount(state.board, state.pos_players[0]) == 0 or \
                State.opCount(state.board, state.pos_players[1]) == 0:
            return True
        return False

    # calculate heuristic function of state as we explained in the dry part
    def utility(self, state):
        score_diff = (state.players_score[0] - state.players_score[1])
        if self.goal(state):
            res = 0 if score_diff == 0 else score_diff * float('inf')
            return res
        """
        # fruits relevant, fruits player1 can reach before they disappear
        fruits_relevant_player1 = dict([(key, value) for key, value in state.fruits_on_board_dict.items() if
                       State.manhattan(state.pos_players[0], key) <= self.little_edge - state.num_of_turns[0]])
        # max val of the relevant fruits , e.g the fruit with biggest value player1 can reach for
        max_val = max(fruits_relevant_player1.values()) if bool(fruits_relevant_player1) else 1
        fruit_factor = max(
            (1 / State.manhattan(state.pos_players[0], key) + val / max_val) for key, val in fruits_relevant.items()) \
            if bool(fruits_relevant_player1) else 0  # if there are no fruits this factor is zero
        score_factor = score_diff / max_val
        option = State.opCount(state.board, state.pos_players[0]), State.opCount(state.board, state.pos_players[0])
        directions_fact = (option[0] - option[1]) * self.penalty_score / max_val
        return fruit_factor + score_factor + directions_fact
        """
        # fruits relevant, fruits player1 can reach before they disappear
        fruits_relevant_player1 = dict([(key, value) for key, value in state.fruits_on_board_dict.items() if
                                        State.manhattan(state.pos_players[0], key) <= self.little_edge -
                                        state.num_of_turns[0]])
        # max val of fruit or 1 if none, normalized factor
        max_val_total = max(state.fruits_on_board_dict.values()) if bool(state.fruits_on_board_dict) else 1
        fruit_factor = max(
            ((1 / State.manhattan(state.pos_players[0], key)) * val / max_val_total) for key, val in
            fruits_relevant_player1.items()) \
            if bool(fruits_relevant_player1) else 0  # if there are no fruits this factor is zero
        score_factor = score_diff / max_val_total
        option = State.opCount(state.board, state.pos_players[0]), State.opCount(state.board, state.pos_players[1])
        # directions_factor = (option[0] - option[1]) * self.penalty_score / max_val_total
        return fruit_factor + score_factor

        # perform move to given direction

    def perform_move(self, direc):
        self.board[self.pos_players[0]] = -1
        player1_new_pos = (self.pos_players[0][0] + direc[0], self.pos_players[0][1] + direc[1])
        self.pos_players = (player1_new_pos, self.pos_players[1])
        self.board[player1_new_pos] = 1
