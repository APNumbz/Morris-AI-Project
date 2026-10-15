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
# 2. Move Generation
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
# 3. Static Estimation & Minimax Search
# -------------------------------------------------------------

positions_evaluated = 0

def static_estimation_opening(board):
    global positions_evaluated
    positions_evaluated += 1
    return board.count('W') - board.count('B')

def minimax_opening(board, depth, is_white_turn):
    if depth == 0:
        return static_estimation_opening(board), board
    
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
        print("Usage: python3 MiniMaxOpeningBlack.py <input_file> <output_file> <depth>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    depth = int(sys.argv[3])
    
    with open(input_file, 'r') as f:
        board_str = f.read().strip()
        
    global positions_evaluated
    positions_evaluated = 0
    
    # Invert colors so the solver evaluates from Black's perspective
    inverted_initial = invert_board(board_str)
    best_estimate, best_move_inverted = minimax_opening(inverted_initial, depth, is_white_turn=True)
    
    # Invert back to get the actual board representation
    best_move = invert_board(best_move_inverted)
    
    with open(output_file, 'w') as f:
        f.write(best_move + "\n")
        
    print(f"Board Position: {best_move}")
    print(f"Positions evaluated by static estimation: {positions_evaluated}")
    print(f"MINIMAX estimate: {best_estimate}")

if __name__ == '__main__':
    main()