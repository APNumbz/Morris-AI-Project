import sys

# -------------------------------------------------------------
# 1. Board Graph & Adjacency
# -------------------------------------------------------------

NEIGHBORS = {
    0: [1, 3, 8],
    1: [0, 2, 4],
    2: [1, 5, 13],
    3: [0, 4, 6, 9],
    4: [1, 3, 5],
    5: [2, 4, 7, 12],
    6: [3, 7, 10],
    7: [5, 6, 11],
    8: [0, 9, 20],
    9: [3, 8, 10, 17],
    10: [6, 9, 14],
    11: [7, 12, 16],
    12: [5, 11, 13, 19],
    13: [2, 12, 22],
    14: [10, 15, 17],
    15: [14, 16, 18],
    16: [11, 15, 19],
    17: [9, 14, 18, 20],
    18: [15, 17, 19, 21],
    19: [12, 16, 18, 22],
    20: [8, 17, 21],
    21: [18, 20, 22],
    22: [13, 19, 21]
}

MILL_LINES = [
    [0, 1, 2], [0, 8, 20], [2, 13, 22], [20, 21, 22],
    [3, 4, 5], [3, 9, 17], [5, 12, 19], [17, 18, 19],
    [6, 10, 14], [7, 11, 16], [14, 15, 16],
    [8, 9, 10], [11, 12, 13], [15, 18, 21],
    [0, 3, 6], [2, 5, 7], [20, 17, 14], [22, 19, 16]
]

def closeMill(j, b):
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
    inverted = invert_board(board)
    moves = generate_moves_midgame_endgame_white(inverted)
    return [invert_board(m) for m in moves]

# -------------------------------------------------------------
# 3. Improved Static Estimation for Midgame / Endgame
# -------------------------------------------------------------

positions_evaluated = 0

def count_mills(board, color):
    count = 0
    for line in MILL_LINES:
        if all(board[pos] == color for pos in line):
            count += 1
    return count

def count_potential_mills(board, color):
    count = 0
    for line in MILL_LINES:
        pieces = [board[pos] for pos in line]
        if pieces.count(color) == 2 and pieces.count('x') == 1:
            count += 1
    return count

def count_blocked_pieces(board, color):
    """Counts pieces of 'color' that have no empty adjacent neighbors."""
    blocked = 0
    for i in range(len(board)):
        if board[i] == color:
            if not any(board[n] == 'x' for n in NEIGHBORS[i]):
                blocked += 1
    return blocked

def static_estimation_game_improved(board):
    global positions_evaluated
    positions_evaluated += 1
    
    num_white = board.count('W')
    num_black = board.count('B')
    
    # Terminal game conditions
    if num_black <= 2:
        return 10000
    elif num_white <= 2:
        return -10000
        
    white_moves = generate_moves_midgame_endgame_white(board)
    black_moves = generate_moves_midgame_endgame_black(board)
    
    if len(black_moves) == 0:
        return 10000
    if len(white_moves) == 0:
        return -10000
        
    # Heuristic Components
    material_diff = num_white - num_black
    mobility_diff = len(white_moves) - len(black_moves)
    mills_diff = count_mills(board, 'W') - count_mills(board, 'B')
    threats_diff = count_potential_mills(board, 'W') - count_potential_mills(board, 'B')
    blocked_diff = count_blocked_pieces(board, 'B') - count_blocked_pieces(board, 'W')
    
    score = (
        (1000 * material_diff) +
        (20 * mobility_diff) +
        (50 * mills_diff) +
        (30 * threats_diff) +
        (25 * blocked_diff)
    )
    return score

def minimax_game(board, depth, is_white_turn):
    if depth == 0:
        return static_estimation_game_improved(board), board
    
    if board.count('W') <= 2 or board.count('B') <= 2:
        return static_estimation_game_improved(board), board
    
    if is_white_turn:
        best_val = float('-inf')
        best_board = None
        successors = generate_moves_midgame_endgame_white(board)
        if not successors:
            return static_estimation_game_improved(board), board
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
        if not successors:
            return static_estimation_game_improved(board), board
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
        print("Usage: python3 MiniMaxGameImproved.py <input_file> <output_file> <depth>")
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