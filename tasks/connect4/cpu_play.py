import numpy as np

from keras.models import Sequential
from keras.layers import Dense, Conv2D, Activation, Dropout, Flatten

from .mcts import MCTS
from .board import *


def play_mcts(board_state, iter_num=100, default_Q=False, default_N=False):
    """
    board_state = ['0000000', '0000000', '0000000', '0000000', '0000000', '0000100']

    returns
        move: col_number or None
        winner: 1 or 2 or None
    """
    board_state = decode_board_state(board_state)
    tree = MCTS()

    # player won?
    status = _find_winner(board_state)
    if status == 1:
        return None, 1

    board = Connect4Board(array=board_state, turn=2, winner=None, terminal=False)
    
    if default_Q and default_N:
        tree.Q = default_Q
        tree.N = default_N

    for _ in range(iter_num):
        tree.do_rollout(board)
    board = tree.choose(board)

    action = np.where((np.array(board.array) == np.array(board_state))==False)[1][0]

    return action, board.winner


def play_rl(board_state, turn=2):
    board_state = decode_board_state(board_state)

    # player won?
    status = _find_winner(board_state)
    if status == 1:
        return None, 1

    board = Connect4Board(array=board_state, turn=turn, winner=None, terminal=False)

    board_input = convert_board(np.array(board_state), turn)

    mainQN = generate_model()
    mainQN.load_weights('tasks/connect4/model_weights/main.hdf5')

    # action = np.argmax(mainQN.predict(board_input)[0])
    action_array = mainQN.predict(board_input)[0]

    available_cols = get_available_cols(board)
    for i in range(len(action_array)):
        if i not in available_cols:
            action_array[i] -= float('Inf')
    action = np.argmax(action_array)
    
    board = board.make_move(action)
    return action, board.winner


def decode_board_state(board_state_str):
    """
    board_state = ['0000000', '0000000', '0000000', '0000000', '0000000', '0000100']
    to
    board_state = ((0, 0, 0, 0, 0, 0, 0),
                (0, 0, 0, 0, 0, 0, 0),
                (0, 0, 0, 0, 0, 0, 0),
                (0, 0, 0, 0, 0, 0, 0),
                (0, 0, 0, 0, 0, 0, 0),
                (0, 0, 0, 0, 1, 0, 0))
    """
    def str_to_numlist(string):
        return tuple([int(num_str) for num_str in string])

    board_state_num = [str_to_numlist(row) for row in board_state_str]
    return tuple(board_state_num)


def _find_winner(array):
    
    status = None
    nrows = 6
    ncols = 7
    connect_num = 4
    
    #horizontal check
    for i in range(nrows):
        for j in range(ncols-connect_num+1):
            if array[i][j] == array[i][j+1] == array[i][j+2] == array[i][j+3] == 2:
                status = 2
            if array[i][j] == array[i][j+1] == array[i][j+2] == array[i][j+3] == 1:
                status = 1
    #vertical check
    for j in range(ncols):
        for i in range(nrows-connect_num+1):
            if array[i][j] == array[i+1][j] == array[i+2][j] == array[i+3][j] == 2:
                status = 2
            if array[i][j] == array[i+1][j] == array[i+2][j] == array[i+3][j] == 1:
                status = 1
    #diagonal check top left to bottom right
    for row in range(nrows-connect_num+1):
        for col in range(ncols-connect_num+1):
            if array[row][col] == array[row + 1][col + 1] == array[row + 2][col + 2] == array[row + 3][col + 3] == 2:
                status = 2
            if array[row][col] == array[row + 1][col + 1] == array[row + 2][col + 2] == array[row + 3][col + 3] == 1:
                status = 1

    #diagonal check bottom left to top right
    for row in range(nrows-1, nrows-connect_num, -1):
        for col in range(ncols-connect_num+1):
            if array[row][col] == array[row - 1][col + 1] == array[row - 2][col + 2] == array[row - 3][col + 3] == 2:
                status = 2
            if array[row][col] == array[row - 1][col + 1] == array[row - 2][col + 2] == array[row - 3][col + 3] == 1:
                status = 1
                
    return status


def convert_board(board_array, turn):
    board_array = np.where(board_array==turn, -1, board_array)
    board_array = np.where((board_array!=-1)&(board_array!=0), 1, board_array)
    board_array = board_array.reshape((1,) + board_array.shape + (1,))
    return board_array


def get_available_cols(board):
    return np.unique(np.where(np.array(board.array) == 0)[-1])


def generate_model(hidden_size=16,kernel_size=3,state_size=(6,7,1),action_size=7):
    model = Sequential()
    model.add(Conv2D(hidden_size, kernel_size, activation='relu', padding='same', input_shape=state_size))
    model.add(Conv2D(hidden_size, kernel_size, activation='relu', padding='same'))
    model.add(Conv2D(hidden_size, kernel_size, activation='relu', padding='same'))
    model.add(Conv2D(hidden_size, kernel_size, activation='relu', padding='same'))
    model.add(Flatten())
    model.add(Dense(action_size, activation='linear'))
    # optimizer = Adam(lr=learning_rate)  # 誤差を減らす学習方法はAdam
    # self.model.compile(loss='mse', optimizer=self.optimizer)
    # model.compile(loss=huberloss, optimizer=self.optimizer)
    return model