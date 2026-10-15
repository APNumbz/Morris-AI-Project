import sys

# -------------------------------------------------------------
# 1. Board Graph & Adjacency
# -------------------------------------------------------------

# Adjacency map for the 23 board positions based on board lines
NEIGHBORS = {
    0: [1, 3, 8],          # a0 -> d0, b1, a3
    1: [0, 2, 4],          # d0 -> a0, g0, d1
    2: [1, 5, 13],         # g0 -> d0, f1, g3
    3: [0, 4, 6, 9],       # b1 -> a0, d1, c2, b3
    4: [1, 3, 5],          # d1 -> d0, b1, f1
    5: [2, 4, 7, 12],      # f1 -> g0, d1, e2, f3
    6: [3, 7, 10],         # c2 -> b1, e2, c3
    7: [5, 6, 11],         # e2 -> f1, c2, e3
    8: [0, 9, 20],         # a3 -> a0, b3, a6
    9: [3, 8, 10, 17],     # b3 -> b1, a3, c3, b5
    10: [6, 9, 14],        # c3 -> c2, b3, c4
    11: [7, 12, 16],       # e3 -> e2, f3, e4
    12: [5, 11, 13, 19],   # f3 -> f1, e3, g3, f5
    13: [2, 12, 22],       # g3 -> g0, f3, g6
    14: [10, 15, 17],      # c4 -> c3, d4, b5
    15: [14, 16, 18],      # d4 -> c4, e4, d5
    16: [11, 15, 19],      # e4 -> e3, d4, f5
    17: [9, 14, 18, 20],   # b5 -> b3, c4, d5, a6
    18: [15, 17, 19, 21],  # d5 -> d4, b5, f5, d6
    19: [12, 16, 18, 22],  # f5 -> f3, e4, d5, g6
    20: [8, 17, 21],       # a6 -> a3, b5, d6
    21: [18, 20, 22],      # d6 -> d5, a6, g6
    22: [13, 19, 21]       # g6 -> g3, f5, d6
}

MILL_LINES = [
    # Outer square lines
    [0, 1, 2],
    [0, 8, 20],
    [2, 13, 22],
    [20, 21, 22],
    # Middle square lines
    [3, 4, 5],
    [3, 9, 17],
    [5, 12, 19],
    [17, 18, 19],
    # Inner square lines
    [6, 10, 14],
    [7, 11, 16],
    [14, 15, 16],
    # Cross connectors
    [8, 9, 10],
    [11, 12, 13],
    [15, 18, 21],
    # Diagonal lines
    [0, 3, 6],
    [2, 5, 7],
    [20, 17, 14],
    [22, 19, 16]
]

def closeMill(j, b):
    """Returns True if the piece at index j forms a completed mill."""
    C = b[j]
    if C == 'x':
        return False
    for line in MILL_LINES:
        if j in line:
            if all(b[pos] == C for pos in line):
                return True
    return False

# -------------------------------------------------------------
# 2. Move Generation (Midgame / Endgame)
# -------------------------------------------------------------

def generate_remove(board, L):
    """Removes one black piece not in a mill; otherwise keeps the board unchanged."""    
    b_list = list(board)
    found_isolated = False
    
    for i in range(len(b_list)):
        if b_list[i] == 'B':
            if not closeMill(i, board):
                found_isolated = True
                b_copy = list(b_list)
                b_copy[i] = 'x'
                L.append("".join(b_copy))
                
    if not found_isolated:
        L.append(board)

def generate_move(board):
    """Generates adjacent moves for White."""
    L = []
    for loc in range(len(board)):
        if board[loc] == 'W':
            for j in NEIGHBORS[loc]:
                if board[j] == 'x':
                    b = list(board)
                    b[loc] = 'x'
                    b[j] = 'W'
                    b_str = "".join(b)
                    if closeMill(j, b_str):
                        generate_remove(b_str, L)
                    else:
                        L.append(b_str)
    return L

def generate_hopping(board):
    """Generates hopping moves for White when down to 3 pieces."""
    L = []
    for alpha in range(len(board)):
        if board[alpha] == 'W':
            for beta in range(len(board)):
                if board[beta] == 'x':
                    b = list(board)
                    b[alpha] = 'x'
                    b[beta] = 'W'
                    b_str = "".join(b)
                    if closeMill(beta, b_str):
                        generate_remove(b_str, L)
                    else:
                        L.append(b_str)
    return L

def generate_moves_midgame_endgame_white(board):
    """Routes to Hopping if White has 3 pieces, else standard sliding moves."""
    if board.count('W') == 3:
        return generate_hopping(board)
    return generate_move(board)

def invert_board(board):
    res = []
    for ch in board:
        if ch == 'W':
            res.append('B')
        elif ch == 'B':
            res.append('W')
        else:
            res.append('x')
    return "".join(res)

def generate_moves_midgame_endgame_black(board):
    """Generates legal moves for Black by color-swapping."""
    inverted = invert_board(board)
    moves = generate_moves_midgame_endgame_white(inverted)
    return [invert_board(m) for m in moves]

# -------------------------------------------------------------
# 3. Static Estimation & Minimax Search
# -------------------------------------------------------------

positions_evaluated = 0

def static_estimation_game(board):
    """Handout-defined static estimation for Midgame/Endgame."""
    global positions_evaluated
    positions_evaluated += 1
    
    num_white = board.count('W')
    num_black = board.count('B')
    
    # Handout win/loss conditions
    if num_black <= 2:
        return 10000
    elif num_white <= 2:
        return -10000
    
    # Evaluate Black's mobility
    black_moves = generate_moves_midgame_endgame_black(board)
    num_black_moves = len(black_moves)
    
    if num_black_moves == 0:
        return 10000
    else:
        return (1000 * (num_white - num_black)) - num_black_moves

def minimax_game(board, depth, is_white_turn):
    """Standard Minimax search for Midgame/Endgame."""
    if depth == 0:
        return static_estimation_game(board), board
    
    # Terminal check: game ends early if either side has <= 2 pieces
    if board.count('W') <= 2 or board.count('B') <= 2:
        return static_estimation_game(board), board
    
    if is_white_turn:
        best_val = float('-inf')
        best_board = None
        successors = generate_moves_midgame_endgame_white(board)
        if not successors:  # White has no legal moves
            return static_estimation_game(board), board
        for succ in successors:
            val, _ = minimax_game(succ, depth - 1, False)
            if val > best_val:
                best_val = val
                best_board = succ
        return best_val, best_board
    else:
        best_val = float('inf')
        best_board = None
        successors = generate_moves_midgame_endgame_black(board)
        if not successors:  # Black has no legal moves -> White wins
            return static_estimation_game(board), board
        for succ in successors:
            val, _ = minimax_game(succ, depth - 1, True)
            if val < best_val:
                best_val = val
                best_board = succ
        return best_val, best_board

# -------------------------------------------------------------
# 4. Main Program
# -------------------------------------------------------------

def main():
    if len(sys.argv) != 4:
        print("Usage: python MiniMaxGame.py <input_file> <output_file> <depth>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    depth = int(sys.argv[3])
    
    with open(input_file, 'r') as f:
        board_str = f.read().strip()
        
    global positions_evaluated
    positions_evaluated = 0
    
    best_estimate, best_move = minimax_game(board_str, depth, is_white_turn=True)
    
    if best_move is None:
        best_move = board_str
        
    with open(output_file, 'w') as f:
        f.write(best_move + "\n")
        
    print(f"Board Position: {best_move}")
    print(f"Positions evaluated by static estimation: {positions_evaluated}")
    print(f"MINIMAX estimate: {best_estimate}")

if __name__ == '__main__':
    main()