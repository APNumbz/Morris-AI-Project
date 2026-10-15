import sys

# -------------------------------------------------------------
# 1. Board Graph & Mill Definitions (Morris Variant Layout)
# -------------------------------------------------------------

# All 3-in-a-row mill lines on the 23-node Morris Variant board
MILL_LINES = [
    # Outer square lines
    [0, 1, 2],    # a0 - d0 - g0
    [0, 8, 20],   # a0 - a3 - a6
    [2, 13, 22],  # g0 - g3 - g6
    [20, 21, 22], # a6 - d6 - g6
    # Middle square lines
    [3, 4, 5],    # b1 - d1 - f1
    [3, 9, 17],   # b1 - b3 - b5
    [5, 12, 19],  # f1 - f3 - f5
    [17, 18, 19], # b5 - d5 - f5
    # Inner square lines
    [6, 7],       # Note: c2 - e2 line depends on layout
    [6, 10, 14],  # c2 - c3 - c4
    [7, 11, 16],  # e2 - e3 - e4
    [14, 15, 16], # c4 - d4 - e4
    # Cross connectors
    [1, 4, 15],   # d0 - d1 - d4
    [8, 9, 10],   # a3 - b3 - c3
    [11, 12, 13], # e3 - f3 - g3
    [15, 18, 21], # d4 - d5 - d6
    # Diagonals / Corner lines
    [0, 3, 6],    # a0 - b1 - c2
    [2, 5, 7],    # g0 - f1 - e2
    [20, 17, 14], # a6 - b5 - c4
    [22, 19, 16]  # g6 - f5 - e4
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
# 2. Move Generation for Opening
# -------------------------------------------------------------

def generate_remove(board, L):
    """
    Removes one black piece not in a mill.
    If all black pieces are in mills, any black piece can be removed.
    """
    b_list = list(board)
    found_isolated = False
    
    # Try removing an isolated piece first
    for i in range(len(b_list)):
        if b_list[i] == 'B':
            if not closeMill(i, board):
                found_isolated = True
                b_copy = list(b_list)
                b_copy[i] = 'x'
                L.append("".join(b_copy))
                
    # If every black piece is part of a mill, any can be removed
    if not found_isolated:
        for i in range(len(b_list)):
            if b_list[i] == 'B':
                b_copy = list(b_list)
                b_copy[i] = 'x'
                L.append("".join(b_copy))

def generate_add(board):
    """Generates all legal board positions for White in the opening."""
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

def generate_moves_opening_black(board):
    """Invert colors, run White's move generator, and invert back."""
    # Step 1: Invert colors (W -> B, B -> W)
    inverted = []
    for ch in board:
        if ch == 'W':
            inverted.append('B')
        elif ch == 'B':
            inverted.append('W')
        else:
            inverted.append('x')
    inv_str = "".join(inverted)
    
    # Step 2: Generate moves for White
    moves = generate_add(inv_str)
    
    # Step 3: Invert colors back
    result = []
    for m in moves:
        back = []
        for ch in m:
            if ch == 'W':
                back.append('B')
            elif ch == 'B':
                back.append('W')
            else:
                back.append('x')
        result.append("".join(back))
    return result

# -------------------------------------------------------------
# 3. Static Estimation & Minimax Search
# -------------------------------------------------------------

positions_evaluated = 0

def static_estimation_opening(board):
    """Static estimation for Opening = numWhitePieces - numBlackPieces."""
    global positions_evaluated
    positions_evaluated += 1
    num_white = board.count('W')
    num_black = board.count('B')
    return num_white - num_black

def minimax_opening(board, depth, is_white_turn):
    """
    Standard Minimax search.
    White is maximizing player; Black is minimizing player.
    """
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
        print("Usage: python MiniMaxOpening.py <input_file> <output_file> <depth>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    depth = int(sys.argv[3])
    
    with open(input_file, 'r') as f:
        board_str = f.read().strip()
        
    global positions_evaluated
    positions_evaluated = 0
    
    best_estimate, best_move = minimax_opening(board_str, depth, is_white_turn=True)
    
    # Write chosen board position to output file
    with open(output_file, 'w') as f:
        f.write(best_move + "\n")
        
    # Print required output
    print(f"Board Position: {best_move}")
    print(f"Positions evaluated by static estimation: {positions_evaluated}")
    print(f"MINIMAX estimate: {best_estimate}")

if __name__ == '__main__':
    main()