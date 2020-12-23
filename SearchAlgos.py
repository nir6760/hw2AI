"""Search Algos: MiniMax, AlphaBeta
"""
from utils import ALPHA_VALUE_INIT, BETA_VALUE_INIT
# TODO: you can import more modules, if needed
import numpy as np

import time


class SearchAlgos:
    def __init__(self, utility, succ, perform_move, goal=None):
        """The constructor for all the search algos.
        You can code these functions as you like to, 
        and use them in MiniMax and AlphaBeta algos as learned in class
        :param utility: The utility function.
        :param succ: The succesor function.
        :param perform_move: The perform move function.
        :param goal: function that check if you are in a goal state.
        """
        self.utility = utility
        self.succ = succ  # should yield list of tuples [(succ1, dir1),...]
        self.perform_move = perform_move
        self.goal = goal
        self.start = time.time()
        self.time_limit = np.inf
        self.time_to_finish = 0.05

    def search(self, state, depth, maximizing_player):
        pass

    # Interruptible algorithem, if time finished return the current best move
    # else go a little bit deepther
    def interruptible(self, state, time_limit):
        self.start = time.time()
        self.time_limit = time_limit
        depth = 1
        try:
            move = self.search(state, depth, True)
        except RuntimeError:
            raise RuntimeError('Not enough time to find a move even for depth 1')
        while True:
            depth = depth + 1
            try:
                result = self.search(state, depth, True)
            except RuntimeError:
                return move
            move = result


class MiniMax(SearchAlgos):

    def search(self, state, depth, maximizing_player):
        """Start the MiniMax algorithm.
        :param state: The state to start from.
        :param depth: The maximum allowed depth for the algorithm.
        :param maximizing_player: Whether this is a max node (True) or a min node (False).
        :return: A tuple: (The min max algorithm value, The direction in case of max node or None in min mode)
        """

        # TODO: erase the following line and implement this function.

        def recursive_minmax(state_r, depth_r, maximizing_player_r):
            if time.time() - self.start > self.time_limit - self.time_to_finish:
                raise RuntimeError('Timeout')
            if self.goal(state_r) or depth_r == 0:
                return self.utility(state_r)
            children = self.succ(state_r)
            if maximizing_player_r:  # player1 turn
                curr_max = -np.inf
                for succ in children:
                    try:
                        val = recursive_minmax(succ, depth_r - 1, False)
                    except RuntimeError:
                        raise RuntimeError('Timeout')
                    curr_max = max(val, curr_max)
                    # if curr_max < val[0]:
                    #    curr_max = val[0]
                    #    curr_max_move = suc_dir[1]
                return curr_max
            else:  # player2 turn
                curr_min = np.inf
                for succ in children:
                    try:
                        val = recursive_minmax(succ, depth_r - 1, True)
                    except RuntimeError:
                        raise RuntimeError('Timeout')
                    curr_min = min(val, curr_min)
                return curr_min

        # start the minimax algo with move
        if time.time() - self.start > self.time_limit - self.time_to_finish:
            raise RuntimeError('Timeout')
        curr_maxx = -np.inf
        best_move = None
        children_move = self.perform_move(state)
        for child in children_move:
            try:
                val = recursive_minmax(child[0], depth - 1, False)
            except RuntimeError:
                raise RuntimeError('Timeout')
            if val > curr_maxx:
                curr_maxx = val
                best_move = child[1]
        return curr_maxx, best_move


class AlphaBeta(SearchAlgos):

    def search(self, state, depth, maximizing_player, start=time.time(), time_limit=np.inf,
               alpha=ALPHA_VALUE_INIT, beta=BETA_VALUE_INIT):
        """Start the AlphaBeta algorithm.
        :param state: The state to start from.
        :param depth: The maximum allowed depth for the algorithm.
        :param maximizing_player: Whether this is a max node (True) or a min node (False).
        :param alpha: alpha value
        :param: beta: beta value
        :return: A tuple: (The min max algorithm value, The direction in case of max node or None in min mode)
        """
        # TODO: erase the following line and implement this function.
        def recursive_AlphaBeta(state_r, depth_r, maximizing_player_r, alpha_r, beta_r):
            if time.time() - self.start > self.time_limit - self.time_to_finish:
                raise RuntimeError('Timeout')
            if self.goal(state_r) or depth_r == 0:
                return self.utility(state_r)
            children = self.succ(state_r)
            if maximizing_player_r:  # player1 turn
                curr_max = -np.inf
                for succ in children:
                    try:
                        val = recursive_AlphaBeta(succ, depth_r - 1, False, alpha_r, beta_r)
                    except RuntimeError:
                        raise RuntimeError('Timeout')
                    curr_max = max(val, curr_max)
                    alpha_r = max(curr_max, alpha_r)
                    if curr_max >= beta_r: return  np.inf
                return curr_max
            else:  # player2 turn
                curr_min = np.inf
                for succ in children:
                    try:
                        val = recursive_AlphaBeta(succ, depth_r - 1, True, alpha_r, beta_r)
                    except RuntimeError:
                        raise RuntimeError('Timeout')
                    curr_min = min(val, curr_min)
                    beta_r = min(curr_min, beta_r)
                    if curr_min <= alpha_r: return  -np.inf
                return curr_min

        # start the minimax algo with move, maximizing first
        if time.time() - self.start > self.time_limit - self.time_to_finish:
            raise RuntimeError('Timeout')
        curr_maxx = -np.inf
        best_move = None
        children_move = self.perform_move(state)
        for child in children_move:
            try:
                val = recursive_AlphaBeta(child[0], depth - 1, False, alpha, beta)
            except RuntimeError:
                raise RuntimeError('Timeout')
            if val > curr_maxx:
                alpha = val
                curr_maxx = val
                best_move = child[1]
        return curr_maxx, best_move
