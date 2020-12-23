import operator
import numpy as np
import os

# TODO: edit the alpha and beta initialization values for AlphaBeta algorithm.
# instead of 'None', write the real initialization value, learned in class.
# hint: you can use np.inf
ALPHA_VALUE_INIT = -np.inf
BETA_VALUE_INIT = np.inf


def get_directions():
    """Returns all the possible directions of a player in the game as a list of tuples.
    """
    return [(1, 0), (0, 1), (-1, 0), (0, -1)]


def tup_add(t1, t2):
    """
    returns the sum of two tuples as tuple.
    """
    return tuple(map(operator.add, t1, t2))


def get_board_from_csv(board_file_name):
    """Returns the board data that is saved as a csv file in 'boards' folder.
    The board data is a list that contains: 
        [0] size of board
        [1] blocked poses on board
        [2] starts poses of the players
    """
    board_path = os.path.join('boards', board_file_name)
    board = np.loadtxt(open(board_path, "rb"), delimiter=" ")

    # mirror board
    board = np.flipud(board)
    i, j = len(board), len(board[0])
    blocks = np.where(board == -1)
    blocks = [(blocks[0][i], blocks[1][i]) for i in range(len(blocks[0]))]
    start_player_1 = np.where(board == 1)
    start_player_2 = np.where(board == 2)

    if len(start_player_1[0]) != 1 or len(start_player_2[0]) != 1:
        raise Exception('The given board is not legal - too many start locations.')

    start_player_1 = (start_player_1[0][0], start_player_1[1][0])
    start_player_2 = (start_player_2[0][0], start_player_2[1][0])

    return [(i, j), blocks, [start_player_1, start_player_2]]


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

    # finds the manhatan distance between pos1 and pos2
    @staticmethod
    def manhattan(pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    # counts number of possible moves from pos on the board
    @staticmethod
    def opCount(board, pos):
        ops = 0
        for d in get_directions():
            i = pos[0] + d[0]
            j = pos[1] + d[1]
            if 0 <= i < len(board) and 0 <= j < len(board[0]) and (board[i][j] not in [-1, 1, 2]):
                ops += 1
        if ops == 0:
            return -1
        return ops
    # return updated fruit dictionary after moving to direction by given player
    @staticmethod
    def fruitsDictAfterMove(fruits_on_board, pos):
        fruits_pos_val = fruits_on_board.copy()
        fruits_pos_val.pop(pos, 0)  # default value for pop without exception
        return fruits_pos_val
