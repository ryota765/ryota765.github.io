import numpy as np
from abc import ABC, abstractmethod
from collections import namedtuple

from random import choice


class Node(ABC):
    """
    A representation of a single board state.
    MCTS works by constructing a tree of these Nodes.
    Could be e.g. a chess or checkers board state.
    """

    @abstractmethod
    def find_children(self):
        "All possible successors of this board state"
        return set()

    @abstractmethod
    def find_random_child(self):
        "Random successor of this board state (for more efficient simulation)"
        return None

    @abstractmethod
    def is_terminal(self):
        "Returns True if the node has no children"
        return True

    @abstractmethod
    def reward(self):
        "Assumes `self` is terminal node. 1=win, 0=loss, .5=tie, etc"
        return 0

    @abstractmethod
    def __hash__(self):
        "Nodes must be hashable"
        return 123456789

    @abstractmethod
    def __eq__(node1, node2):
        "Nodes must be comparable"
        return True


_C4B = namedtuple("Connect4Board", "array turn winner terminal")

class Connect4Board(_C4B, Node):
    
    def find_children(board):
        if board.terminal:  # If the game is finished then no moves can be made
            return set()
        # Otherwise, you can make a move in each of the empty spots
        available_cols = np.unique(np.where(np.array(board.array) == 0)[-1])
        return {
            board.make_move(col) for col in available_cols
        }

    def find_random_child(board):
        if board.terminal:
            return None  # If the game is finished then no moves can be made
        available_cols = np.unique(np.where(np.array(board.array) == 0)[-1])
        return board.make_move(choice(available_cols))

    def reward(board):
        if not board.terminal:
            raise RuntimeError(f"reward called on nonterminal board {board}")
        if board.winner is board.turn:
            # It's your turn and you've already won. Should be impossible.
            raise RuntimeError(f"reward called on unreachable board {board}")
        if board.turn is not board.winner:
            return 0  # Your opponent has just won. Bad.
        if board.winner is None:
            return 0.5  # Board is a tie
        # The winner is neither True, False, nor None
        raise RuntimeError(f"board has unknown winner type {board.winner}")

    def is_terminal(board):
        return board.terminal

    def make_move(board, col_index):
        array = np.array(board.array)
        
        target_col = array[:, col_index]
        row_index = np.max(np.where(target_col == 0))
        array[row_index, col_index] = board.turn
        
        turn = 2 if board.turn==1 else 1
        winner = _find_winner(array)
        is_terminal = (winner is not None) or np.count_nonzero(array==0) == 0

        return Connect4Board(tuple(map(tuple, array)), turn, winner, is_terminal)

# TODO: integrate same function also in cpu_play.py
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