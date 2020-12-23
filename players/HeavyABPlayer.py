"""
MiniMax Player with AlphaBeta pruning with heavy heuristic
"""
from players.AbstractPlayer import AbstractPlayer


# TODO: you can import more modules, if needed
import numpy as np
import SearchAlgos as sa
import utils
from utils import State

class Player(AbstractPlayer):
    def __init__(self, game_time, penalty_score):
        AbstractPlayer.__init__(self, game_time, penalty_score)  # keep the inheritance of the parent's (AbstractPlayer) __init__()
        # TODO: initialize more fields, if needed, and the AlphaBeta algorithm from SearchAlgos.py
        self.board = None  # player1 is my player
        self.pos_players = None  # tuple [0]-player1 pos, [1] -player2 pos
        self.strategy = sa.AlphaBeta(utility=self.utility, succ=self.succ, perform_move=self.perform_move, goal=self.goal)
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
        depth = 3 # this is changing depand on expriment
        player1_turn = True
        move_direction = self.strategy.search(
            State(np.copy(self.board), player1_turn, players_score, self.num_of_turns, self.fruits_on_board.copy(),
                  self.pos_players),
            depth, True)[1]
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
        if self.num_of_turns[0] == 0:
            self.fruits_on_board = fruits_on_board_dict
        if self.num_of_turns[0] >= self.little_edge:  # we need to update it only once, when they disappear
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
    # returnes successor of state
    def succ(self, state):
        player1_play = state.player1_play
        curr_player_pos = state.pos_players[0] if player1_play else state.pos_players[1]
        curr_player_num_of_turns = state.num_of_turns[0] if player1_play else state.num_of_turns[1]
        for d in utils.get_directions():
            i = curr_player_pos[0] + d[0]
            j = curr_player_pos[1] + d[1]

            if 0 <= i < np.size(state.board, 0) and 0 <= j < np.size(state.board, 1) and (
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
                    succ_fruits_on_board_dict = State.fruitsDictAfterMove(state.fruits_on_board_dict, new_pos) #copy and update dict

                yield State(succ_board, not player1_play, succ_players_score,
                            succ_num_of_turns, succ_fruits_on_board_dict, succ_pos_players)

    # check if state is in the final states group, means no possible moves for one of the competitors
    def goal(self, state):
        if State.opCount(state.board, state.pos_players[0]) == -1 or \
                State.opCount(state.board, state.pos_players[1]) == -1:
            return True
        return False

    # calculate heuristic function of state as we explained in the dry part
    def utility(self, state): #todo: fix utility
        score_diff = (state.players_score[0] - state.players_score[1])
        if self.goal(state):
            res = 0 if score_diff == 0 else score_diff * 10000
            return res
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
        directions_factor = (option[0] - option[1]) * self.penalty_score / max_val_total
        # fruit_factor2 = 1/min(State.manhattan(state.pos_players[0], key) for key in
        #    fruits_relevant_player1.keys()) if bool(fruits_relevant_player1) else 0
        return 0

    # perform move to given direction by player
    def perform_move(self, state):
        player1_play = state.player1_play
        curr_player_pos = state.pos_players[0]
        curr_player_num_of_turns = state.num_of_turns[0]
        for d in utils.get_directions():
            i = curr_player_pos[0] + d[0]
            j = curr_player_pos[1] + d[1]

            if 0 <= i < np.size(self.board, 0) and 0 <= j < np.size(self.board, 1) and (
                    state.board[i][j] not in [-1, 1, 2]):  # then move is legal
                new_pos = (i, j)

                succ_pos_players = (new_pos, state.pos_players[1])
                succ_players_score = state.players_score[0] + state.fruits_on_board_dict.get(new_pos, 0), \
                                    state.players_score[1]
                succ_num_of_turns = state.num_of_turns[0] + 1, \
                                    state.num_of_turns[1]


                succ_board = np.copy(state.board)
                succ_board[curr_player_pos] = -1  # perform move on succ_state board
                succ_board[new_pos] = 1

                succ_fruits_on_board_dict = {}
                if curr_player_num_of_turns <= self.little_edge:
                    succ_fruits_on_board_dict = State.fruitsDictAfterMove(state.fruits_on_board_dict, new_pos)

                yield State(succ_board, not player1_play, succ_players_score,
                            succ_num_of_turns, succ_fruits_on_board_dict, succ_pos_players), d
