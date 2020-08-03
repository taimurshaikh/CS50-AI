"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None

def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    numX = numO = 0
    for row in board:
        for cell in row:
            if cell == X:
                numX += 1
            elif cell == O:
                numO += 1

    if numX > numO:
        return O
    elif not terminal(board) and numX == numO:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    available = set()
    # Iterate through every cell. If it is empty, add its coordinates to the available set
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell == EMPTY:
                available.add((i, j))

    return available


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    global turn

    # Raises exception if action is invalid
    if terminal(board) or action not in actions(board):
        raise Exception

    else:
        i = action[0]
        j = action[1]
        # Creating new variable so we don't override the state passed in
        res = copy.deepcopy(board)

        if player(board) == O:
            res[i][j] = O
        else:
            res[i][j] = X

    return res


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Iterate through the board, checking for rows columns or diagonals of Xs or Os
    for i, row in enumerate(board):
        for j, cell in enumerate(row):

            # COLUMNS
            # If we are in the first column
            if j == 0:
                # Checking for three in one row
                if cell != EMPTY and cell == row[j+1] and cell == row[j+2]:
                    if cell == X:
                        return X
                    else:
                        return O

            # ROWS
            # If we are in the first row
            if i == 0:
                # Checking for 3 in one column
                if cell != EMPTY and cell == board[i+1][j] and cell == board[i+2][j]:
                    if cell == X:
                        return X
                    else:
                        return O

            # DIAGONALS
            # If we are in the first row and first column (at top left)
            if i == 0 and j == 0:
                if cell != EMPTY and cell == board[i+1][j+1] and cell == board[i+2][j+2]:
                    if cell == X:
                        return X
                    else:
                        return O

            # If we are in the first row and third column (at top right)
            if i == 0 and j == 2:
                if cell != EMPTY and cell == board[i+1][j-1] and cell == board[i+2][j-2]:
                    if cell == X:
                        return X
                    else:
                        return O

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # If the game is won, then it is definitely over
    if winner(board) != None or not actions(board):
        return True

    # Else, if there are still empty cells on the board, then the game is not over
    for row in board:
        for cell in row:
            if cell == EMPTY:
                return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    w = winner(board)
    if w == X:
        return 1
    elif w == O:
        return -1
    else:
        return 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    if board == initial_state():
        return (1,1)

    current_player = player(board)
    bestVal = -math.inf if current_player == X else math.inf

    for action in actions(board):
        newVal = calculate_value(result(board, action), bestVal)

        if current_player == X:
            newVal = max(bestVal, newVal)

        if current_player == O:
            newVal = min(bestVal, newVal)

        if newVal != bestVal:
            bestVal = newVal
            best_action = action

    return best_action

def calculate_value(board, best_value):

    if terminal(board):
        return utility(board)

    current_player = player(board)
    value = -math.inf if current_player == X else math.inf

    for action in actions(board):
        newVal = calculate_value(result(board, action), value)

        if current_player == X:
            if newVal > best_value:
                return newVal
            value = max(value, newVal)

        if current_player == O:
            if newVal < best_value:
                return newVal
            value = min(value, newVal)

    return value
