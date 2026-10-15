import sys

# -------------------------------------------------------------
# 1. Board Graph & Mill Definitions
# -------------------------------------------------------------

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
# 2. Move Generation (Opening)
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

def generate_add(board):
    L = []
    for loc in range(len(board)):
        if board[loc] == 'x':
            b = list(board)
            b[loc] = 'W'
            b_str = "".join(b)
            if closeMill(loc, b_str):
                generate_remove(b_str, L)
            else:
                L.append(b_str)
    return L

def generate_moves_opening_white(board):
    return generate_add(board)

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

def generate_moves_opening_black(board):
    inv_str = invert_board(board)
    moves = generate_add(inv_str)
    return [invert_board(m) for m in moves]

# -------------------------------------------------------------
# 3. Improved Static Estimation for Opening
# -------------------------------------------------------------

positions_evaluated = 0

def count_mills(board, color):
    count = 0
    for line in MILL_LINES:
        if all(board[pos] == color for pos in line):
            count += 1
    return count

def count_potential_mills(board, color):
    """Counts 2 pieces of 'color' and 1 empty spot on a mill line."""
    count = 0
    for line in MILL_LINES:
        pieces = [board[pos] for pos in line]
        if pieces.count(color) == 2 and pieces.count('x') == 1:
            count += 1
    return count

def static_estimation_opening_improved(board):
    global positions_evaluated
    positions_evaluated += 1
    
    # Feature 1: Material difference
    num_white = board.count('W')
    num_black = board.count('B')
    material_diff = num_white - num_black
    
    # Feature 2: Completed mills difference
    white_mills = count_mills(board, 'W')
    black_mills = count_mills(board, 'B')
    mills_diff = white_mills - black_mills
    
    # Feature 3: Potential 2-in-a-row threats
    white_threats = count_potential_mills(board, 'W')
    black_threats = count_potential_mills(board, 'B')
    threats_diff = white_threats - black_threats
    
    return (100 * material_diff) + (25 * mills_diff) + (10 * threats_diff)

def minimax_opening(board, depth, is_white_turn):
    if depth == 0:
        return static_estimation_opening_improved(board), board
    
    if is_white_turn:
        best_val = float('-inf')
        best_board = None
        successors = generate_moves_opening_white(board)
        for succ in successors:
            val, _ = minimax_opening(succ, depth - 1, False)
            if val > best_val:
                best_val = val
                best_board = succ
        return best_val, best_board
    else:
        best_val = float('inf')
        best_board = None
        successors = generate_moves_opening_black(board)
        for succ in successors:
            val, _ = minimax_opening(succ, depth - 1, True)
            if val < best_val:
                best_val = val
                best_board = succ
        return best_val, best_board

# -------------------------------------------------------------
# 4. Main Program
# -------------------------------------------------------------

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 MiniMaxOpeningImproved.py <input_file> <output_file> <depth>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    depth = int(sys.argv[3])
    
    with open(input_file, 'r') as f:
        board_str = f.read().strip()
        
    global positions_evaluated
    positions_evaluated = 0
    
    best_estimate, best_move = minimax_opening(board_str, depth, is_white_turn=True)
    
    if best_move is None:
        best_move = board_str
        
    with open(output_file, 'w') as f:
        f.write(best_move + "\n")
        
    print(f"Board Position: {best_move}")
    print(f"Positions evaluated by static estimation: {positions_evaluated}")
    print(f"MINIMAX estimate: {best_estimate}")

if __name__ == '__main__':
    main()