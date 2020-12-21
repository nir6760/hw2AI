import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from matplotlib.animation import FuncAnimation
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np
import os
import random
import time
import utils

class Game:
    def __init__(self, board, players_positions, max_fruit_score, max_fruit_time,
                fruits_max_part_of_free_spaces = 0.2,
                animated=False, animation_func = None):
        """Initialize the game properties with parameters.
        input:
            - board: 2D np.array. The initial board
            - players_positions: the initial players positions
            - max_fruit_score: max score for a fruit.
            - max_fruit_time: max time for a fruit to be on board.
            - fruits_max_part_of_free_spaces: the max part on board the fruits can take at each timestamp.
            - animated: bool. Animated game (not in terminal) if true.
            - animated_func: the function doing the animation.
        """
        assert len(players_positions) == 2, 'Supporting 2 players only'
        self.map = board
        self.max_fruit_score = max_fruit_score

        self.max_fruit_time = max_fruit_time
        # min fruit time is set by the min dimension of the board
        self.min_fruit_time = min(len(board[0]), len(board))
        # in case that min_fruit_time is greater/equal to max_fruit_time -> change max_fruit_time
        if self.max_fruit_time <= self.min_fruit_time:
            self.max_fruit_time = self.min_fruit_time + 1
        
        self.fruits_max_part_of_free_spaces = fruits_max_part_of_free_spaces
        self.players_positions = players_positions
        self.players_score = [0 ,0] # init scores for each player
        self.directions = utils.get_directions()
        # Fruits:
        fruits_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fruits_imgs')
        self.fruits_paths = [os.path.join(fruits_dir, fruit_file) for fruit_file in os.listdir(fruits_dir)]
        self.fruits_on_board = {}

        self.turn = 0

        self.animated = animated
        self.animation_func = animation_func
        
        if self.animated:
            self.init_animation()
        self.create_fruits()
        self.players_positions = [tuple(reversed(position)) for position in self.players_positions]

    def init_animation(self):
        # Colors:
        self.board_colors = {'free': 'gray', 'stepped on': 'gray'}
        self.players_colors = ['blue', 'red']

        aspect = len(self.map[0]) / len(self.map)
        self.fig = plt.figure(frameon=False, figsize=(4 * aspect, 4))
        self.ax = self.fig.add_subplot(111, aspect='equal')
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=None, hspace=None)

        # create boundary patch
        x_min, y_min = -0.5, -0.5
        x_max = len(self.map[0]) - 0.5
        y_max = len(self.map) - 0.5
        plt.xlim(x_min, x_max)
        plt.ylim(y_min, y_max)
        # patches = board_patch + map_patches + player_patches
        self.board_patch = [Rectangle((x_min, y_min), x_max - x_min, y_max - y_min, facecolor='none', edgecolor='gray')]
        self.map_patches = []
        for i in range(len(self.map)):
            self.map_patches.append([])
            for j in range(len(self.map[0])):
                if self.map[i][j] != 0:
                    face_color = self.board_colors['stepped on']
                    self.map_patches[i].append(
                        Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor=face_color, edgecolor='black', fill=True))
                else:
                    face_color = self.board_colors['free']
                    self.map_patches[i].append(
                        Rectangle((j - 0.5, i - 0.5), 1, 1, facecolor=face_color, edgecolor='black', fill=False))

        # painting the starting positions of the players:
        self.map_patches[self.players_positions[0][0]][self.players_positions[0][1]].fill = True
        self.map_patches[self.players_positions[1][0]][self.players_positions[1][1]].fill = True
        
        # create players:
        self.T = 0
        self.players = []
        self.player_patches = []
        for i in range(len(self.players_positions)):
            self.players.append(Circle(tuple(reversed(self.players_positions[i])), 0.3, facecolor=self.players_colors[i], edgecolor='black'))
            self.players[i].original_face_color = self.players_colors[i]
            self.player_patches.append(self.players[i])
            self.T = max(self.T, len(self.players_positions[i]) - 1)
        
        global animation
        animation = FuncAnimation(self.fig, self.animation_func,
                                                 init_func=self.init_func,
                                                 frames=int(self.T + 1) * 10,
                                                 interval=600,  # change game speed anumation here
                                                 blit=False)

    @staticmethod
    def start_game():
        plt.show()


    def init_func(self):
        for p in self.board_patch + sum(self.map_patches, []) + self.player_patches:
            self.ax.add_patch(p)
        return self.board_patch + sum(self.map_patches, []) + self.players


    def update_map(self, prev_pos, next_pos):
        player_id = self.map[prev_pos[1]][prev_pos[0]]
        self.map[prev_pos[1]][prev_pos[0]] = -1
        self.map[next_pos[1]][next_pos[0]] = player_id


    def choose_fruit_pos(self):
        # get all free places on board
        free_places = np.where(self.map == 0)
        if len(free_places[0]) == 0:
            return -1

        # choose random pos on board that is a free space
        idx = random.randint(0,len(free_places[0])-1)

        pos = (free_places[0][idx], free_places[1][idx])

        return pos #pos on self.map (reversed in animation)
    
    
    def remove_fruit_from_board(self, pos):
        if self.map[pos[0],pos[1]] == self.fruits_on_board[pos]['value']: # don't override a player if exists there. Safety first!
            self.map[pos[0],pos[1]] = 0

        if self.animated:
            fruit_art = self.fruits_on_board[pos]['fruit_art']
            fruit_art.remove()
        del self.fruits_on_board[pos]


    def add_fruit(self, pos):
        if self.animated:
            fruit_idx = random.randint(0, len(self.fruits_paths)-1)
            fruit_path = self.fruits_paths[fruit_idx]
            img = plt.imread(fruit_path)
            off_img = OffsetImage(img, zoom = 0.3)
            bbox = AnnotationBbox(off_img, (pos[1], pos[0]), frameon=False)
            fruit = self.ax.add_artist(bbox)
        else:
            fruit = None

        # choose value of fruit and update the tracking map
        value = random.randint(3, self.max_fruit_score)
        self.map[pos[0],pos[1]] = value

        # update fruits_on_board tracking
        board_time = self.min_fruit_time * 2
        self.fruits_on_board[pos] = {'fruit_art':fruit, 'value': value, 'board_time_left':board_time}

    def create_fruits(self):
        num_free_places = len(np.where(self.map == 0)[0])
        if num_free_places != 0:
            num_fruits = random.randint(0, int(num_free_places * self.fruits_max_part_of_free_spaces))
            # add new fruits in free spaces (not occupied by players, fruits, blocked cells)
            for _ in range(num_fruits):
                pos = self.choose_fruit_pos() # don't cover the players, existing fruits and blocked cells
                if pos != -1:
                    self.add_fruit(pos)

    def update_fruits(self):
        # update fruits timings
        for fruit_key in self.fruits_on_board.keys():
            self.fruits_on_board[fruit_key]['board_time_left'] -= 1
        # remove fruits that finished their time on board
        fruits_to_remove = [fruit_key for (fruit_key, fruit_props_d) in self.fruits_on_board.items() 
                            if fruit_props_d['board_time_left'] <= 0]
        
        for fruit_key in fruits_to_remove:
            self.remove_fruit_from_board(pos = fruit_key)


    def update_player_pos(self, pos):
        prev_pos = self.players_positions[self.turn]

        # update the scores of the player
        if self.map[pos[1]][pos[0]] > 2:
            # update score value for player
            self.players_score[self.turn] += self.map[pos[1]][pos[0]]
            # remove fruit from board
            self.remove_fruit_from_board(tuple(reversed(pos)))

        # update patch/position of player
        self.players_positions[self.turn] = pos

        if self.animated:
            self.players[self.turn].center = pos
            
            i = pos[1]
            j = pos[0]
            self.map_patches[i][j].fill = True
        
        return prev_pos


    def update_staff_with_pos(self, pos):
        pos = tuple(reversed(pos))
        prev_pos = self.update_player_pos(pos)
        self.update_map(prev_pos=prev_pos, next_pos=pos)
        self.update_fruits()

        self.turn = 1 - self.turn
        if self.animated:
            return self.board_patch + sum(self.map_patches, []) + self.players


    def player_cant_move(self, player_id):
        player_pos = self.get_player_position(player_id)
        all_next_positions = [utils.tup_add(player_pos, direction) for direction in self.directions]
        possible_next_positions = [pos for pos in all_next_positions if self.pos_feasible_on_board(pos)]
        return len(possible_next_positions) == 0


    def pos_feasible_on_board(self, pos):
        # on board
        on_board = (0 <= pos[0] < len(self.map) and 0 <= pos[1] < len(self.map[0]))
        if not on_board:
            return False
        
        # free cell
        value_in_pos = self.map[pos[0]][pos[1]]
        free_cell = (value_in_pos not in [-1, 1, 2])
        return free_cell


    def check_move(self, pos):
        if not self.pos_feasible_on_board(pos):
            return False
        
        prev_player_position = self.get_player_position_by_current(current = True)
        if not any(utils.tup_add(prev_player_position, move) == pos for move in self.directions):
            # print('moved from', prev_player_position, 'to', pos)
            return False

        return True


    def print_board_to_terminal(self, player_id):
        board_to_print = np.flipud(self.get_map_for_player_i(player_id))
        print('_' * len(board_to_print[0]) * 4)
        for row in board_to_print:
            row = [str(int(x)) if x != -1 else 'X' for x in row]
            print(' | '.join(row))
            print('_' * len(row) * 4)


    def get_map_for_player_i(self, player_id):
        map_copy = self.map.copy()

        pos_player_id = self.get_player_position(player_id)
        pos_second = self.get_player_position(1 - player_id)

        # flip positions
        map_copy[pos_player_id[0]][pos_player_id[1]] = 1
        map_copy[pos_second[0]][pos_second[1]] = 2
        return map_copy
    

    def get_players_scores(self):
        return self.players_score
    
    def penalize_player(self, player_id, penalty):
        self.players_score[player_id] -= penalty

    def get_starting_state(self):
        return self.board_patch + sum(self.map_patches, []) + self.players

    def get_fruits_on_board(self):
        """ Returns a dictionary of pos:val
            for each fruit on the game board (current state)
        """
        fruits_pos_val = {pos:fruit_params['value'] for (pos, fruit_params) 
                            in self.fruits_on_board.items()}
        
        return fruits_pos_val

    def get_player_position(self, player_id):
        pos = np.where(self.map == player_id + 1)
        pos = tuple([ax[0] for ax in pos])
        return pos


    def get_player_position_by_current(self, current = True):
        player_id = self.turn
        if not current:
            player_id = 1 - self.turn

        return tuple(reversed(self.players_positions[player_id]))
