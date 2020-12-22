"""Search Algos: MiniMax, AlphaBeta
"""
from utils import ALPHA_VALUE_INIT, BETA_VALUE_INIT
# TODO: you can import more modules, if needed

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
        self.time_to_finish = 0.05

    def search(self, state, depth, maximizing_player, start, time_limit):
        pass

    # Interruptible algorithem, if time finished return the current best move
    # else go a little bit deepther
    def interruptible(self, state, time_limit):
        start = time.time()
        depth = 1
        try:
            move = self.search(state, depth, state.player1_play, start, time_limit)
        except RuntimeError:
            raise RuntimeError('Not enough time to find a move even for depth 1')
        while True:
            depth = depth + 1
            try:
                result = self.search(state, depth, state.player1_play, start, time_limit)
            except RuntimeError:
                return move
            move = result


class MiniMax(SearchAlgos):

    def search(self, state, depth, maximizing_player, start=time.time(), time_limit=float('inf')):
        """Start the MiniMax algorithm.
        :param state: The state to start from.
        :param depth: The maximum allowed depth for the algorithm.
        :param maximizing_player: Whether this is a max node (True) or a min node (False).
        :return: A tuple: (The min max algorithm value, The direction in case of max node or None in min mode)
        """

        # TODO: erase the following line and implement this function.
        if time.time() - start > time_limit - self.time_to_finish:
            raise RuntimeError('Timeout')

        if self.goal(state) or depth == 0:
            return self.utility(state), None

        children = self.succ(state)
        if maximizing_player:  # player1 turn
            curr_max = -float('inf')
            curr_max_move = None
            for suc_dir in children:
                try:
                    val = self.search(suc_dir[0], depth - 1, not maximizing_player, start, time_limit)
                except RuntimeError:
                    raise RuntimeError('Timeout')
                # curr_max = max(val[0], curr_max)
                if curr_max < val[0]:
                    curr_max = val[0]
                    curr_max_move = suc_dir[1]
            return curr_max, curr_max_move
        else:  # player2 turn
            curr_min = float('inf')
            for suc_dir in children:
                try:
                    val = self.search(suc_dir[0], depth - 1, not maximizing_player, start, time_limit)
                except RuntimeError:
                    raise RuntimeError('Timeout')
                curr_min = min(val[0], curr_min)
            return curr_min, None
#d

class AlphaBeta(SearchAlgos):

    def search(self, state, depth, maximizing_player, alpha=ALPHA_VALUE_INIT, beta=BETA_VALUE_INIT):
        """Start the AlphaBeta algorithm.
        :param state: The state to start from.
        :param depth: The maximum allowed depth for the algorithm.
        :param maximizing_player: Whether this is a max node (True) or a min node (False).
        :param alpha: alpha value
        :param: beta: beta value
        :return: A tuple: (The min max algorithm value, The direction in case of max node or None in min mode)
        """
        # TODO: erase the following line and implement this function.
        raise NotImplementedError
