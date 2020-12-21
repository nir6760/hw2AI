from players.AbstractPlayer import AbstractPlayer
import numpy as np


class Player(AbstractPlayer):
    def __init__(self, game_time, penalty_score):
        AbstractPlayer.__init__(self, game_time, penalty_score)  # keep the inheritance of the parent's (AbstractPlayer) __init__()
        self.board = None             # and add two more fields to Player
        self.pos = None
        

    def set_game_params(self, board):
        self.board = board
        pos = np.where(board == 1)
        # convert pos to tuple of ints
        self.pos = tuple(ax[0] for ax in pos)


    def state_score(self, board, pos):
        num_steps_available = 0
        for d in self.directions:
            i = pos[0] + d[0]
            j = pos[1] + d[1]

            # check legal move
            if 0 <= i < len(board) and 0 <= j < len(board[0]) and (board[i][j] not in [-1, 1, 2]): 
                num_steps_available += 1

        if num_steps_available == 0:
            return -1
        else:
            return 4 - num_steps_available


    @staticmethod
    def count_ones(board):
        counter = len(np.where(board == 1)[0])
        return counter

    def make_move(self, time_limit, players_score):  # time parameter is not used, we assume we have enough time.

        assert self.count_ones(self.board) == 1

        prev_pos = self.pos
        self.board[prev_pos] = -1

        assert self.count_ones(self.board) == 0

        best_move, best_move_score, best_new_pos = None, float('-inf'), None
        for d in self.directions:
            i = self.pos[0] + d[0]
            j = self.pos[1] + d[1]

            if 0 <= i < len(self.board) and 0 <= j < len(self.board[0]) and (self.board[i][j] not in [-1, 1, 2]):   # then move is legal
                new_pos = (i, j)
                self.board[new_pos] = 1
                assert self.count_ones(self.board) == 1

                score = self.state_score(board=self.board, pos=(i, j))
                if score > best_move_score:
                    best_move, best_move_score, best_new_pos = d, score, new_pos
                self.board[new_pos] = 0
                assert self.count_ones(self.board) == 0


        if best_move is None:
            exit(0)

        self.board[best_new_pos] = 1

        assert self.count_ones(self.board) == 1

        self.pos = best_new_pos
        return best_move


    def set_rival_move(self, pos):
        self.board[pos] = -1


    def update_fruits(self, fruits_on_board_dict):
        pass
