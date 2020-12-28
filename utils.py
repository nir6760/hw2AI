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


'''
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

    # return a legal move# @staticmethod
    @staticmethod
    def firstLegal(board, pos):
        for d in get_directions():
            i = pos[0] + d[0]
            j = pos[1] + d[1]
            if 0 <= i < len(board) and 0 <= j < len(board[0]) and (board[i][j] not in [-1, 1, 2]):
                return d
        return (1 , 0)  # means we have no option to move

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

    ########## helper functions for MiniMaxPlayer, AlphaBetaPlayer, HeavyABPlayer, LightABPlayer, GlobalTimeABPlayer algorithm ##########
    # TODO: add here the utility, succ, and perform_move functions used in MiniMax algorithm
    # returnes successor of state
    @staticmethod
    def succ(state):
        little_edge = min(np.size(state.board, 0), np.size(state.board, 1))

        player1_play = state.player1_play
        curr_player_pos = state.pos_players[0] if player1_play else state.pos_players[1]
        curr_player_num_of_turns = state.num_of_turns[0] if player1_play else state.num_of_turns[1]
        for d in get_directions():
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
                if curr_player_num_of_turns <= little_edge:
                    succ_fruits_on_board_dict = State.fruitsDictAfterMove(state.fruits_on_board_dict,
                                                                          new_pos)  # copy and update dict

                yield State(succ_board, not player1_play, succ_players_score,
                            succ_num_of_turns, succ_fruits_on_board_dict, succ_pos_players)

    # check if state is in the final states group, means no possible moves for one of the competitors
    @staticmethod
    def goal(state):
        if State.opCount(state.board, state.pos_players[0]) == -1 or \
                State.opCount(state.board, state.pos_players[1]) == -1:
            return True
        return False

    # perform move to given direction by player
    @staticmethod
    def perform_move(state):
        little_edge = min(np.size(state.board, 0), np.size(state.board, 1))

        player1_play = state.player1_play
        curr_player_pos = state.pos_players[0]
        curr_player_num_of_turns = state.num_of_turns[0]
        for d in get_directions():
            i = curr_player_pos[0] + d[0]
            j = curr_player_pos[1] + d[1]

            if 0 <= i < np.size(state.board, 0) and 0 <= j < np.size(state.board, 1) and (
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
                if curr_player_num_of_turns <= little_edge:
                    succ_fruits_on_board_dict = State.fruitsDictAfterMove(state.fruits_on_board_dict, new_pos)

                yield State(succ_board, not player1_play, succ_players_score,
                            succ_num_of_turns, succ_fruits_on_board_dict, succ_pos_players), d

    # bfs to search a fruit near my position, replica of board
    @staticmethod
    def searchForFruit(board, my_pos, depth=0, max_depth=8):
        queue = [my_pos]
        max_fruit =0
        depth += 1
        while queue:
            curr_pos = queue.pop(0)
            for d in get_directions():
                i = curr_pos[0] + d[0]
                j = curr_pos[1] + d[1]
                if 0 <= i < np.size(board, 0) and 0 <= j < np.size(board, 1) and (
                        board[i][j] not in [-1, 1, 2, -3]):  # then move is legal
                    new_pos = (i, j)
                    if board[new_pos] >= 2:
                        max_fruit = max(max_fruit * 10 / depth, board[new_pos])
                    depth += 1
                    if depth > max_depth:
                        return -200
                    queue.append(new_pos)
                    board[new_pos] = -3
        return max_fruit

    # find which square block the player
    @staticmethod
    def searchForBlock(board, pos, depth=0, max_depth=10):
        queue = [pos]
        size = 1
        visited = []
        while queue:
            for it in range(size):
                curr_pos = queue.pop(0)
                visited.append(curr_pos)
                for d in get_directions():
                    i = curr_pos[0] + d[0]
                    j = curr_pos[1] + d[1]
                    if 0 <= i < np.size(board, 0) and 0 <= j < np.size(board, 1) and (
                            board[i][j] not in [-1, 1, 2] and (i,j) not in visited):  # then move is legal
                        new_pos = (i, j)
                        queue.append(new_pos)
            size = len(queue)
            depth += 1
            if depth == max_depth:
                return max_depth
        return depth
'''


# represents a state of the game
class State:
    def __init__(self, board, player1_play, players_score, num_of_turns, fruits_on_board_dict, pos_players,
                 last_move_fruit_value=(0, 0)):
        """
        state initialization.
        """
        self.board = board
        self.player1_play = player1_play  # bool true if player1 turn, false when player2 turn
        self.players_score = players_score  # tuple [0]-player1 score, [1] -player2 score
        self.num_of_turns = num_of_turns  # tuple [0]-player1 turns, [1] -player2 turns
        self.fruits_on_board_dict = fruits_on_board_dict
        self.pos_players = pos_players  # tuple [0]-player1 pos, [1] -player2 pos

        self.last_move_fruit_value = last_move_fruit_value # if player ate fruit in the last move
        # , tuple tuple [0]-player1 pos, [1] -player2 pos

    # finds the manhatan distance between pos1 and pos2
    @staticmethod
    def manhattan(pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    # return a legal move# @staticmethod
    @staticmethod
    def firstLegal(board, pos):
        for d in get_directions():
            i = pos[0] + d[0]
            j = pos[1] + d[1]
            if 0 <= i < len(board) and 0 <= j < len(board[0]) and (board[i][j] not in [-1, 1, 2]):
                return d
        return (1, 0)  # means we have no option to move

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

    ########## helper functions for MiniMaxPlayer, AlphaBetaPlayer, HeavyABPlayer, LightABPlayer, GlobalTimeABPlayer algorithm ##########
    # TODO: add here the utility, succ, and perform_move functions used in MiniMax algorithm
    # returnes successor of state
    @staticmethod
    def succ(state):
        little_edge = min(np.size(state.board, 0), np.size(state.board, 1))

        player1_play = state.player1_play
        curr_player_pos = state.pos_players[0] if player1_play else state.pos_players[1]
        curr_player_num_of_turns = state.num_of_turns[0] if player1_play else state.num_of_turns[1]
        for d in get_directions():
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
                #succ_board = np.copy(state.board)
                succ_board = state.board

                succ_board[curr_player_pos] = -1  # perform move on succ_state board
                succ_board[new_pos] = 1 if player1_play else 2

                #succ_fruits_on_board_dict = {}
                #if curr_player_num_of_turns <= little_edge:
                #    succ_fruits_on_board_dict = State.fruitsDictAfterMove(state.fruits_on_board_dict,
                #                                                          new_pos)  # copy and update dict
                succ_fruits_on_board_dict = state.fruits_on_board_dict
                #if curr_player_num_of_turns > little_edge:
                #    succ_fruits_on_board_dict = {}

                last_fruit = succ_fruits_on_board_dict.pop(new_pos, 0)
                succ_last_move_fruit_value = (last_fruit, state.last_move_fruit_value[1]) if player1_play else \
                            (state.last_move_fruit_value[0], last_fruit)

                yield State(succ_board, not player1_play, succ_players_score,
                            succ_num_of_turns, succ_fruits_on_board_dict, succ_pos_players, succ_last_move_fruit_value), d

    # retrieve the state before moving in direction dir, help us so we dont have to copy board and save space and time
    # opposite operator
    @staticmethod
    def retriveLast(state, dir):

        move_by_player1 = not state.player1_play #last move was by player1?
        last_player_current_pos = state.pos_players[0] if move_by_player1 else state.pos_players[1]
        last_pos = (last_player_current_pos[0] - dir[0], last_player_current_pos[1] - dir[1])
        if move_by_player1:  # last was state player1 turn
            state.pos_players = (last_pos, state.pos_players[1])
            state.players_score = state.players_score[0] - state.last_move_fruit_value[0], \
                                            state.players_score[1]
            state.num_of_turns = state.num_of_turns[0] - 1, \
                                        state.num_of_turns[1]
            last_fruit = state.last_move_fruit_value[0]
        else:  # last was state player1 turn
            state.pos_players = (state.pos_players[0], last_pos)
            state.players_score = state.players_score[0], \
                                    state.players_score[1] - state.last_move_fruit_value[1]
            state.num_of_turns = state.num_of_turns[0], \
                                state.num_of_turns[1] - 1
            last_fruit = state.last_move_fruit_value[1]

            #retriving board
        state.board[last_player_current_pos] = last_fruit  # un preform move
        state.board[last_pos] = 1 if move_by_player1 else 2

        if last_fruit != 0:
            state.fruits_on_board_dict[last_player_current_pos] = last_fruit #retrive fruit to dictionary

    # check if state is in the final states group, means no possible moves for one of the competitors
    @staticmethod
    def goal(state):
        if (state.player1_play and State.opCount(state.board, state.pos_players[0]) == -1) or \
                (not state.player1_play and State.opCount(state.board, state.pos_players[1]) == -1):
            return True
        return False

    # bfs to search a fruit near my position, replica of board
    @staticmethod
    def searchForFruit(board, my_pos, depth=0, max_depth=8):
        queue = [my_pos]
        max_fruit = 0
        depth += 1
        while queue:
            curr_pos = queue.pop(0)
            for d in get_directions():
                i = curr_pos[0] + d[0]
                j = curr_pos[1] + d[1]
                if 0 <= i < np.size(board, 0) and 0 <= j < np.size(board, 1) and (
                        board[i][j] not in [-1, 1, 2, -3]):  # then move is legal
                    new_pos = (i, j)
                    if board[new_pos] >= 2:
                        max_fruit = max(max_fruit * 10 / depth, board[new_pos])
                    depth += 1
                    if depth > max_depth:
                        return -200
                    queue.append(new_pos)
                    board[new_pos] = -3
        return max_fruit

    # find which square block the player
    @staticmethod
    def searchForBlock(board, pos, depth=0, max_depth=10):
        queue = [pos]
        size = 1
        visited = []
        while queue:
            for it in range(size):
                curr_pos = queue.pop(0)
                visited.append(curr_pos)
                for d in get_directions():
                    i = curr_pos[0] + d[0]
                    j = curr_pos[1] + d[1]
                    if 0 <= i < np.size(board, 0) and 0 <= j < np.size(board, 1) and (
                            board[i][j] not in [-1, 1, 2] and (i, j) not in visited):  # then move is legal
                        new_pos = (i, j)
                        queue.append(new_pos)
            size = len(queue)
            depth += 1
            if depth == max_depth:
                return max_depth
        return depth
