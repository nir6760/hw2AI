"""
MiniMax Player with AlphaBeta pruning and global time
"""
from players.AbstractPlayer import AbstractPlayer
# TODO: you can import more modules, if needed
import numpy as np
import SearchAlgos as sa
import utils
from utils import State


class Player(AbstractPlayer):
    global alpha_fact

    def __init__(self, game_time, penalty_score):
        AbstractPlayer.__init__(self, game_time,
                                penalty_score)  # keep the inheritance of the parent's (AbstractPlayer) __init__()
        # TODO: initialize more fields, if needed, and the AlphaBeta algorithm from SearchAlgos.py
        self.board = None  # player1 is my player
        self.pos_players = None  # tuple [0]-player1 pos, [1] -player2 pos
        self.strategy = sa.AlphaBeta(utility=self.utility, succ=self.succ, perform_move=self.perform_move,
                                     goal=self.goal)
        self.num_of_turns = (0, 0)  # tuple [0]-player1 turns, [1] -player2 turns
        self.fruits_on_board = None
        self.little_edge = 0

        self.time = game_time  # niv
        alpha_fact = 10
        self.alpha_fact = alpha_fact
        self.fruit_avaliable = True
        self.extra_time = 0
        self.next_move = None

    def set_game_params(self, board):
        """Set the game parameters needed for this player.
        This function is called before the game starts.
        (See GameWrapper.py for more info where it is called)
        input:
            - board: np.array, a 2D matrix of the board.
        No output is expected.
        """
        # TODO: erase the following line and implement this function.
        self.board = np.copy(board)
        self.little_edge = min(np.size(self.board, 0), np.size(self.board, 1))
        self.pos_players = self.findPos

        self.turn_time = (self.alpha_fact - 1) * self.game_time / (
                min(np.size(self.board, 0), np.size(self.board, 1)) + (np.size(self.board, 0) * np.size(self.board, 1)) / 2 - 1)  # niv

    def make_move(self, time_limit, players_score):
        """Make move with this Player.
        input:
            - time_limit: float, time limit for a single turn.
        output:
            - direction: tuple, specifing the Player's movement, chosen from self.directions
        """
        # TODO: erase the following line and implement this function.
        player1_turn = True
        curr_turn_time_budget = self.get_turn_time()
        if curr_turn_time_budget is None:  # we have only single move, we can save some time
            move_direction = self.next_move
        else:
            move_direction = self.strategy.interruptible(
                State(np.copy(self.board), player1_turn, players_score, self.num_of_turns, self.fruits_on_board.copy(),
                    self.pos_players),
                curr_turn_time_budget)[1]
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
        if bool(fruits_on_board_dict):
            self.no_more_fruit()

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

    # check if there is only single direction available
    def single_direction(self):
        single_dir = False
        dir = None
        my_pos = self.pos_players[0]
        for d in self.directions:
            i = my_pos[0] + d[0]
            j = my_pos[1] + d[1]
            # check legal move
            if 0 <= i < np.size(self.board, 0) and 0 <= j < len(self.board[0]) and (self.board[i][j] not in [-1, 1, 2]):
                if single_dir:
                    return None
                dir = d
                single_dir = True
        return dir

    # find the time_limit for the current turn
    def get_turn_time(self):
        single = self.single_direction()
        if self.fruit_avaliable:
            time = self.alpha_fact * self.turn_time + self.extra_time
            if single is not None:  # we have single direction
                self.next_move = single
                self.extra_time = time
                return None
            self.game_time -= time

        else:
            time = self.turn_time + self.extra_time
            if single is not None:  # we have single direction
                self.next_move = single
                self.extra_time = time
                return None
        self.extra_time = 0
        return time

    # auxiliary function for get_turn_time , when we have no more fruits
    def no_more_fruit(self):
        if not self.fruit_avaliable:
            return
        self.fruit_avaliable = False
        self.turn_time = self.game_time / (np.size(self.board, 0) * np.size(self.board, 1) / 2 - self.num_of_turns[0] - 1)

    ########## helper functions for AlphaBeta algorithm ##########
    # TODO: add here the utility, succ, and perform_move functions used in AlphaBeta algorithm
    # returnes successor of state
    def succ(self, state):
        player1_play = state.player1_play
        curr_player_pos = state.pos_players[0] if player1_play else state.pos_players[1]
        curr_player_num_of_turns = state.num_of_turns[0] if player1_play else state.num_of_turns[1]
        for d in utils.get_directions():
            i = curr_player_pos[0] + d[0]
            j = curr_player_pos[1] + d[1]

            if 0 <= i < np.size(self.board, 0) and 0 <= j < np.size(self.board, 1) and (
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
                    succ_fruits_on_board_dict = State.fruitsDictAfterMove(state.fruits_on_board_dict, new_pos)

                yield State(succ_board, not player1_play, succ_players_score,
                            succ_num_of_turns, succ_fruits_on_board_dict, succ_pos_players)

    # check if state is in the final states group, means no possible moves for one of the competitors
    def goal(self, state):
        if State.opCount(state.board, state.pos_players[0]) == -1 or \
                State.opCount(state.board, state.pos_players[1]) == -1:
            return True
        return False

    # bfs to search a fruit near my position, replica of board
    @staticmethod
    def searchForFruit(board, my_pos, depth=0, max_depth=8):
        queue = [my_pos]
        while queue:
            curr_pos = queue.pop(0)
            for d in utils.get_directions():
                i = curr_pos[0] + d[0]
                j = curr_pos[1] + d[1]
                if 0 <= i < np.size(board, 0) and 0 <= j < np.size(board, 1) and (
                        board[i][j] not in [-1, 1, 2, -3]):  # then move is legal
                    new_pos = (i, j)
                    if board[new_pos] >= 100:
                        return 100
                    if board[new_pos] > 50:
                        return 20
                    depth += 1
                    if depth > max_depth:
                        return -100
                    queue.append(new_pos)
                    board[new_pos] = -3
        return 0

    # calculate heuristic function of state as we explained in the dry part
    def utility(self, state):
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
        fruit_factor3 = 0
        if bool(fruits_relevant_player1):
            fruit_factor3 = self.searchForFruit(state.board.copy(), state.pos_players[0], 0,
                                                self.little_edge - self.num_of_turns[0]) / max_val_total
        return fruit_factor + score_factor  # + directions_factor

        # perform move to given direction

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
