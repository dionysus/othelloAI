"""

An AI player for Othello. 
"""

import random
import sys
import time

cache = {} # dictionary for caching
prunes = 0

from othello_shared import find_lines, get_possible_moves, get_score, play_move

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    p1, p2 = get_score(board)
    if color == 1: # color is black
        return p1 - p2
    else:
        return p2 - p1

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional

    board_size = len(board) * len(board)

    CORNERS_MOD = board_size * 10
    CORNER_ADJ_SQUARE_MOD = -CORNERS_MOD / 2
    WIN_MOD = board_size * 100

    score = 0

    #! ------------------------------------------------------------ MOBILITY
    ''' More possible moves allows for more choice and strategy
    '''
    op_moves = get_possible_moves(board, next_color(color))

    score += len(op_moves)

    #! ------------------------------------------------------------ COIN PARITY
    ''' Difference in board color is not too important, but a winning board
    should be prioritized
    '''

    if len(op_moves) == 0 and compute_utility(board, color) > 1:
        score += WIN_MOD

    # coin_parity_mod = compute_utility(board, color)
    # score += coin_parity_mod

    #! ------------------------------------------------------------ CORNER
    ''' Corner spaces are highly desirable
    C 0
    0 0 
    '''
    dim = len(board) - 1
    corners = [(0, 0), (dim, 0), (0, dim), (dim, dim)]

    p_corners = 0
    for corner in corners:
        if get_space_color(board, corner) == color:
            p_corners += 1
        elif get_space_color(board, corner) == next_color(color):
            p_corners -= 1
    
    corners_mod = p_corners * CORNERS_MOD

    score += corners_mod

    #! ------------------------------------------------------------ X SQUARES
    ''' The spots diagonal to the corners are to be avoided, as they allow for
    the corner to be captured
    C 0
    0 X 
    '''
    # corners = [(0, 0), (dim, 0), (0, dim), (dim, dim)]
    x_offsets = [ (1, 1), (-1, 1), (1, -1), (-1, -1)]
    
    p_x_squares = 0

    for corner, x_offset in zip(corners, x_offsets):
        if get_space_color(board, corner) == 0:
            x_square = (corner[0] + x_offset[0], corner[1] + x_offset[1])
            x_square_color = get_space_color(board, x_square)
            if x_square_color == color:
                p_x_squares += 1
            if x_square_color == next_color(color):
                p_x_squares -= 1

    x_squares_mod = p_x_squares * CORNER_ADJ_SQUARE_MOD

    score += x_squares_mod

    #! ------------------------------------------------------- Adjacent Corner
    ''' The spots above/below or left/right of the corners are to be avoided, as 
    they allow for the corner to be captured
    C X
    X 0 
    '''
    # corners = [(0, 0), (dim, 0), (0, dim), (dim, dim)]
    adj_offsets = [ 
        ((0, 1), (1, 0)),
        ((-1, 0), (0, 1)),
        ((1, 0), (0, -1)),
        ((-1, 0), (0, -1))]
    
    p_adj_squares = 0

    for corner, adj_offset in zip(corners, adj_offsets):
        for i in (range(2)):
            if get_space_color(board, corner) == 0:
                adj_square = (
                    corner[0] + adj_offset[i][0], corner[1] + adj_offset[i][1])
                adj_square_color = get_space_color(board, adj_square)
                if adj_square_color == color:
                    p_adj_squares += 1
                if adj_square_color == next_color(color):
                    p_adj_squares -= 1

    adj_squares_mod = p_adj_squares * CORNER_ADJ_SQUARE_MOD

    score += adj_squares_mod

    #! ------------------------------------------------------- Score Calculated
    return score

def get_space_color(board, space):
    ''' return color of the space at space (col, row)
        0 = empty, 1 = dark, 2 = light
    '''
    return board[space[1]][space[0]]

#! --------------------------------------------------------------------- MINIMAX

def next_color(color):
    if color == 1:
        return 2
    else:
        return 1

def minmax_mode(maxi, board, color, limit, caching):
    use_heuristics = False # default FALSE

    # CHECK CACHE
    if (caching and (board, color, maxi) in cache):
        return cache[board, color, maxi]

    test_color = color if maxi else next_color(color)

    # DEPTH LIMIT REACHED
    if limit == 0:
        if use_heuristics:
            return None, compute_heuristic(board, color)
        else:
            return None, compute_utility(board, color)

    moves = get_possible_moves(board, test_color)

    # TERMINAL STATE 
    if len(moves) == 0:
        move_tup = (None, compute_utility(board, color))
        
        if (caching):
            cache[board, color, maxi] = move_tup

        return move_tup

    move_tups = []

    for move in moves:
        next_board = play_move(board, test_color, move[0], move[1])
        if maxi:
            move_util = minimax_min_node(next_board, color, limit - 1, caching)[1]
        else:
            move_util = minimax_max_node(next_board, color, limit - 1, caching)[1]
        move_tups.append((move, move_util))

    if maxi:
        goal_tup = max(move_tups, key = lambda t: t[1])
    else:
        goal_tup = min(move_tups, key = lambda t: t[1])

    if (caching): 
        cache[board, color, maxi] = goal_tup

    return goal_tup

def minimax_min_node(board, color, limit, caching = 0):
    return minmax_mode(False, board, color, limit, caching)

def minimax_max_node(board, color, limit, caching = 0):
    return minmax_mode(True, board, color, limit, caching)

def select_move_minimax(board, color, limit, caching = 0):
    """
    Given a board and a player color, decide on a move. 
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.  

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic 
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.    
    """
    cache.clear()
    space, util = minimax_max_node(board, color, limit, caching)
    cache.clear()
    return space

#! ---------------------------------------------------------- ALPHA-BETA PRUNING

def alphabeta_node(maxi, board, color, alpha, beta, limit, caching, ordering):
    use_heuristics = False # default FALSE

    # CHECK CACHE
    if (caching and (board, color, maxi) in cache):
        return cache[board, color, maxi]
    
    test_color = color if maxi else next_color(color)

    # DEPTH LIMIT REACHED
    if limit == 0:
        if use_heuristics: 
            return None, compute_heuristic(board, color)
        else:
            return None, compute_utility(board, color)

    moves = get_possible_moves(board, test_color)
    
    # TERMINAL STATE 
    if len(moves) == 0:
        move_tup = (None, compute_utility(board, color))

        if (caching):
            cache[board, color, maxi] = move_tup
            
        return move_tup

    next_boards = []
    next_utils = []

    for move in moves:
        next_board = play_move(board, test_color, move[0], move[1])
        next_boards.append(next_board)

        if ordering:
            # Keep track of next_board's utility
            if use_heuristics:
                move_util = compute_heuristic(next_board, color)
            else:
                move_util = compute_utility(next_board, color)
            next_utils.append(move_util)
    
    # sort moves, boards by their utility
    if ordering:
        next_utils, moves, next_boards = zip(
            *sorted(zip(next_utils, moves, next_boards), reverse = not maxi))

    move_tups = []

    for move, next_board in zip(moves, next_boards):    
        if maxi:
            move_util = alphabeta_min_node(
                next_board, color, alpha, beta, limit - 1, caching, ordering)[1]
            if move_util is not None:
                alpha = max(alpha, move_util)
        else:
            move_util = alphabeta_max_node(
                next_board, color, alpha, beta, limit - 1, caching, ordering)[1]
            if move_util is not None:
                beta = min(beta, move_util)

        if move_util is not None: 
            move_tups.append((move, move_util))

        # Pruning
        if alpha >= beta:
            break

    if len(move_tups) == 0:
        return None, None

    if maxi:
        goal_tup = max(move_tups, key = lambda t: t[1]) 
    else:
        goal_tup = min(move_tups, key = lambda t: t[1])

    if caching: 
        cache[board, color, maxi] = goal_tup

    return goal_tup

def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    return alphabeta_node(
        False, board, color, alpha, beta, limit, caching, ordering)

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    return alphabeta_node(
        True, board, color, alpha, beta, limit, caching, ordering)

def select_move_alphabeta(board, color, limit, caching = 0, ordering = 0):
    """
    Given a board and a player color, decide on a move. 
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.  

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic 
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.    
    If ordering is ON (i.e. 1), use node ordering to expedite pruning and reduce the number of state evaluations. 
    If ordering is OFF (i.e. 0), do NOT use node ordering to expedite pruning and reduce the number of state evaluations. 
    """
    cache.clear()
    space, util = alphabeta_max_node(board, color, float('-inf') , float('inf'), limit, caching, ordering)
    cache.clear()
    return space

####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print("IAGO AI") # First line is the name of this AI
    arguments = input().split(",")
    
    color = int(arguments[0]) #Player color: 1 for dark (goes first), 2 for light. 
    limit = int(arguments[1]) #Depth limit
    minimax = int(arguments[2]) #Minimax or alpha beta
    caching = int(arguments[3]) #Caching 
    ordering = int(arguments[4]) #Node-ordering (for alpha-beta only)

    if (minimax == 1): eprint("Running MINIMAX")
    else: eprint("Running ALPHA-BETA")

    if (caching == 1): eprint("State Caching is ON")
    else: eprint("State Caching is OFF")

    if (ordering == 1): eprint("Node Ordering is ON")
    else: eprint("Node Ordering is OFF")

    if (limit == -1): eprint("Depth Limit is OFF")
    else: eprint("Depth Limit is ", limit)

    if (minimax == 1 and ordering == 1): eprint("Node Ordering should have no impact on Minimax")

    while True: # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()
        dark_score = int(dark_score_s)
        light_score = int(light_score_s)

        if status == "FINAL": # Game is over.
            print
        else:
            board = eval(input()) # Read in the input and turn it into a Python
                                  # object. The format is a list of rows. The
                                  # squares in each row are represented by
                                  # 0 : empty square
                                  # 1 : dark disk (player 1)
                                  # 2 : light disk (player 2)

            # Select the move and send it to the manager
            if (minimax == 1): #run this if the minimax flag is given
                movei, movej = select_move_minimax(board, color, limit, caching)
            else: #else run alphabeta
                movei, movej = select_move_alphabeta(board, color, limit, caching, ordering)
            
            print("{} {}".format(movei, movej))

if __name__ == "__main__":
    run_ai()
