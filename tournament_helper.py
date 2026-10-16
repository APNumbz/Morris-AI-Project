import subprocess
import time
import sys

def print_board(b):
    """Prints the 23-node board matching the official handout (Row 6 top, Row 0 bottom)."""
    print(f"    Row 6:  {b[20]}-----------{b[21]}-----------{b[22]}")
    print(f"            | \\         |         / |")
    print(f"    Row 5:  |   {b[17]}-------{b[18]}-------{b[19]}   |")
    print(f"            |   | \\     |     / |   |")
    print(f"    Row 4:  |   |   {b[14]}---{b[15]}---{b[16]}   |   |")
    print(f"            |   |   |       |   |   |")
    print(f"    Row 3:  {b[8]}---{b[9]}---{b[10]}       {b[11]}--{b[12]}--{b[13]}")
    print(f"            |   |   |       |   |   |")
    print(f"    Row 2:  |   |   {b[6]}-------{b[7]}   |   |")
    print(f"            |   | /     |     \\ |   |")
    print(f"    Row 1:  |   {b[3]}-------{b[4]}-------{b[5]}   |")
    print(f"            | /         |         \\ |")
    print(f"    Row 0:  {b[0]}-----------{b[1]}-----------{b[2]}")

def run_agent(board_str, my_color, depth, phase):
    with open("board.txt", "w") as f:
        f.write(board_str.strip() + "\n")
        
    cmd = [
        sys.executable,
        "TournamentAgent.py",
        "board.txt",
        "move.txt",
        my_color,
        str(depth),
        phase
    ]
    
    start_t = time.time()
    res = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - start_t
    
    if res.returncode != 0:
        print("\n[!] Agent Error:")
        print(res.stderr)
        return None, elapsed
        
    with open("move.txt", "r") as f:
        new_board = f.read().strip()
        
    return new_board, elapsed

def main():
    print("=" * 60)
    print("      NINE MEN'S MORRIS — TOURNAMENT LIVE RUNNER")
    print("=" * 60)
    
    my_color = input("Are you playing as White (W) or Black (B)? ").strip().upper()
    while my_color not in ['W', 'B']:
        my_color = input("Invalid choice. Enter W or B: ").strip().upper()
        
    depth = input("Search Depth [Default 4]: ").strip()
    depth = int(depth) if depth.isdigit() else 4
    
    print(f"\n[OK] Configured: Playing as {my_color} | Depth {depth}")
    print("Type 'exit' at any prompt to quit.\n")
    
    current_board = "x" * 23
    turn = 1
    
    while True:
        phase = "opening" if turn <= 18 else "game"
        is_my_turn = (turn % 2 != 0 and my_color == 'W') or (turn % 2 == 0 and my_color == 'B')
        active_color = 'W' if turn % 2 != 0 else 'B'
        
        print(f"\n{'='*20} TURN {turn} [{active_color}] - {phase.upper()} {'='*20}")
        
        if is_my_turn:
            print(f">>> Calculating your move ({my_color})...")
            my_move, duration = run_agent(current_board, my_color, depth, phase)
            
            if not my_move:
                print("Failed to generate move. Check error above.")
                break
                
            current_board = my_move
            w_cnt = current_board.count('W')
            b_cnt = current_board.count('B')
            
            print(f"Time Taken: {duration:.2f}s | (Pieces: W={w_cnt}, B={b_cnt})")
            print("\n" + "#" * 60)
            print(f"  COPY/PASTE THIS TO TOURNAMENT CHAT:")
            print(f"  {current_board}")
            print("#" * 60 + "\n")
            
            print_board(current_board)
            
        else:
            # Opponent's turn: paste their string
            while True:
                user_in = input(f"Paste Opponent's ({active_color}) Board String: ").strip()
                if user_in.lower() == 'exit':
                    return
                if len(user_in) == 23 and all(c in 'WBx' for c in user_in):
                    current_board = user_in
                    break
                print(f"[!] Invalid string! Must be exactly 23 chars containing only W, B, x. (Length: {len(user_in)})")
                
            w_cnt = current_board.count('W')
            b_cnt = current_board.count('B')
            print(f"Opponent played: {current_board} (W={w_cnt}, B={b_cnt})")
            print_board(current_board)
            
        # Win / Loss checks in game phase
        if phase == "game":
            w_cnt = current_board.count('W')
            b_cnt = current_board.count('B')
            if b_cnt <= 2:
                print("\n" + "=" * 50)
                print("🏆 GAME OVER: WHITE WINS (Black reduced to 2 pieces)!")
                print("=" * 50)
                break
            elif w_cnt <= 2:
                print("\n" + "=" * 50)
                print("🏆 GAME OVER: BLACK WINS (White reduced to 2 pieces)!")
                print("=" * 50)
                break
                
        turn += 1

if __name__ == "__main__":
    main()