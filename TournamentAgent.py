import sys

# -------------------------------------------------------------
# 1. Board Graph, Neighbors, & Mill Lines
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

# -------------------------------------------------------------
# 2. Successor Move Generators
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

# Unified move routers
def generate_moves_opening_white(board):
    return generate_add(board)

def generate_moves_opening_black(board):
    return [invert_board(m) for m in generate_add(invert_board(board))]

def generate_moves_midgame_endgame_white(board):
    if board.count('W') == 3:
        return generate_hopping(board)
    return generate_move(board)

def generate_moves_midgame_endgame_black(board):
    inv = invert_board(board)
    moves = generate_moves_midgame_endgame_white(inv)
    return [invert_board(m) for m in moves]

# -------------------------------------------------------------
# 3. Static Estimation & Alpha-Beta Engine
# -------------------------------------------------------------

def count_mills(board, color):
    return sum(1 for line in MILL_LINES if all(board[pos] == color for pos in line))

def count_potential_mills(board, color):
    count = 0
    for line in MILL_LINES:
        pieces = [board[pos] for pos in line]
        if pieces.count(color) == 2 and pieces.count('x') == 1:
            count += 1
    return count

def count_blocked_pieces(board, color):
    blocked = 0
    for i in range(len(board)):
        if board[i] == color:
            if not any(board[n] == 'x' for n in NEIGHBORS[i]):
                blocked += 1
    return blocked

def static_estimation(board, phase):
    num_white = board.count('W')
    num_black = board.count('B')
    
    if phase == 'opening':
        return (
            100 * (num_white - num_black) +
            25 * (count_mills(board, 'W') - count_mills(board, 'B')) +
            10 * (count_potential_mills(board, 'W') - count_potential_mills(board, 'B'))
        )
    else:
        if num_black <= 2:
            return 10000
        if num_white <= 2:
            return -10000
            
        w_moves = generate_moves_midgame_endgame_white(board)
        b_moves = generate_moves_midgame_endgame_black(board)
        
        if len(b_moves) == 0:
            return 10000
        if len(w_moves) == 0:
            return -10000
            
        return (
            1000 * (num_white - num_black) +
            20 * (len(w_moves) - len(b_moves)) +
            50 * (count_mills(board, 'W') - count_mills(board, 'B')) +
            30 * (count_potential_mills(board, 'W') - count_potential_mills(board, 'B')) +
            25 * (count_blocked_pieces(board, 'B') - count_blocked_pieces(board, 'W'))
        )

positions_evaluated = 0

def alpha_beta(board, depth, alpha, beta, is_white_turn, phase):
    global positions_evaluated
    
    if depth == 0:
        positions_evaluated += 1
        return static_estimation(board, phase), board
        
    if phase != 'opening' and (board.count('W') <= 2 or board.count('B') <= 2):
        positions_evaluated += 1
        return static_estimation(board, phase), board
        
    if is_white_turn:
        best_val = float('-inf')
        best_board = None
        moves = (generate_moves_opening_white(board) if phase == 'opening' 
                 else generate_moves_midgame_endgame_white(board))
        if not moves:
            positions_evaluated += 1
            return static_estimation(board, phase), board
        for m in moves:
            val, _ = alpha_beta(m, depth - 1, alpha, beta, False, phase)
            if val > best_val:
                best_val = val
                best_board = m
            alpha = max(alpha, best_val)
            if alpha >= beta:
                break
        return best_val, best_board
    else:
        best_val = float('inf')
        best_board = None
        moves = (generate_moves_opening_black(board) if phase == 'opening' 
                 else generate_moves_midgame_endgame_black(board))
        if not moves:
            positions_evaluated += 1
            return static_estimation(board, phase), board
        for m in moves:
            val, _ = alpha_beta(m, depth - 1, alpha, beta, True, phase)
            if val < best_val:
                best_val = val
                best_board = m
            beta = min(beta, best_val)
            if alpha >= beta:
                break
        return best_val, best_board

# -------------------------------------------------------------
# 4. Tournament Decision Driver
# -------------------------------------------------------------

def detect_phase(board):
    """
    Detects whether the game is in opening or midgame/endgame.
    Opening has at most 18 total placements.
    """
    total_pieces = board.count('W') + board.count('B')
    # If the board has fewer than 18 pieces and looks like an early setup, it is opening.
    # Note: If captures happened during the opening, total pieces can be < 18.
    # In official matches, teams can also specify phase or track move numbers.
    return 'midgame' if total_pieces >= 18 else 'opening'

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 TournamentAgent.py <input_file> <output_file> <color: W or B> [depth] [phase: auto/opening/game]")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    color = sys.argv[3].upper()
    depth = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    phase_arg = sys.argv[5].lower() if len(sys.argv) > 5 else "auto"
    
    with open(input_file, 'r') as f:
        board_str = f.read().strip()
        
    # Phase detection
    if phase_arg in ["opening", "game", "midgame"]:
        phase = "opening" if phase_arg == "opening" else "midgame"
    else:
        phase = detect_phase(board_str)
        
    global positions_evaluated
    positions_evaluated = 0
    
    if color == 'W':
        best_score, best_move = alpha_beta(
            board_str, depth, float('-inf'), float('inf'), is_white_turn=True, phase=phase
        )
    else:
        # Invert board so Black uses White's maximization logic
        inv_board = invert_board(board_str)
        best_score, best_move_inv = alpha_beta(
            inv_board, depth, float('-inf'), float('inf'), is_white_turn=True, phase=phase
        )
        best_move = invert_board(best_move_inv) if best_move_inv else board_str
        
    if best_move is None:
        best_move = board_str
        
    with open(output_file, 'w') as f:
        f.write(best_move + "\n")
        
    print(f"Phase: {phase.upper()} | Color: {color} | Depth: {depth}")
    print(f"Board Position: {best_move}")
    print(f"Positions evaluated by static estimation: {positions_evaluated}")
    print(f"Estimate: {best_score}")

if __name__ == '__main__':
    main()