# MiniMaxOpeningBlack.py
# python MiniMaxOpeningBlack.py inputBoard outputBoard "seach depth"
# python MiniMaxOpeningBlack.py board1.txt board2.txt 2

positionsEvaluated = 0
board = ""

# Tracks all node relationships on the board
neighbors = {
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
    22: [13, 19, 21] }

mills = {
    # Outer square
    (0, 1, 2),
    (0, 8, 20),
    (2, 13, 22),
    (20, 21, 22),

    # Middle square
    (3, 4, 5),
    (3, 9, 17),
    (5, 12, 19),
    (17, 18, 19),

    # Inner square
    (6, 10, 14),
    (7, 11, 16),
    (14, 15, 16),

    # Diagonal connecting lines
    (0, 3, 6),
    (2, 5, 7),
    (20, 17, 14),
    (22, 19, 16),

    # Horizontal connecting lines
    (8, 9, 10),
    (11, 12, 13),

    # Vertical connecting lines
    (21, 18, 15) }

def closeMill(location, boardPosition):
    piece = boardPosition[location]
    if piece == "x":
        return False

    for mill in mills:
        if location in mill:
            if all(boardPosition[pos] == piece for pos in mill):
                return True

    return False

def GenerateAdd(boardPosition):
    L = []

    for location in range(len(boardPosition)):
        if boardPosition[location] == "x":
            newBoard = (boardPosition[:location] + "W" + boardPosition[location + 1:])

            if closeMill(location, newBoard):
                GenerateRemove(newBoard, L)
            else:
                L.append(newBoard)
    return L

def GenerateRemove(boardPosition, L):
    originalLength = len(L)
    for location in range(len(boardPosition)):
        if boardPosition[location] == "B":
            if not closeMill(location, boardPosition):
                newBoard = (boardPosition[:location] + "x" + boardPosition[location + 1:])
                L.append(newBoard)

    if len(L) == originalLength:
        for location in range(len(boardPosition)):
            if boardPosition[location] == "B":
                newBoard = (boardPosition[:location] + "x" + boardPosition[location + 1:])
                L.append(newBoard)
    return

def staticEstimation(board):
    return (board.count("W") - board.count("B"))

def ABOpening(boardPosition, depth, alpha = float("-inf"), beta = float("inf")):
    global positionsEvaluated

    if depth == 0:
        positionsEvaluated += 1
        return staticEstimation(boardPosition), boardPosition

    moves = GenerateAdd(boardPosition)

    if not moves:
        positionsEvaluated += 1
        return staticEstimation(boardPosition), boardPosition

    bestEstimate = float("-inf")
    bestBoard = boardPosition

    for move in moves:
        estimate, _ = ABOpening(move, depth - 1, alpha, beta)

        if estimate > bestEstimate:
            bestEstimate = estimate
            bestBoard = move

        alpha = max(alpha, bestEstimate)

        if alpha >= beta:
            break

    return bestEstimate, bestBoard

def main():
    global board, positionsEvaluated

    import sys

    if (len(sys.argv) != 4):
        print("python ABOpening.py inputBoard outputBoard searchDepth")
        return 1
    
    inputBoardFile = sys.argv[1]
    outputBoardFile = sys.argv[2]
    searchDepth = int(sys.argv[3])

    with open(inputBoardFile, "r") as f:
        board = f.read().strip()

    estimate, bestBoard = ABOpening(board, searchDepth)

    print("Board Position:", bestBoard)
    print("Positions evaluated by static estimation:", positionsEvaluated)
    print("MINIMAX estimate", estimate)

    with open(outputBoardFile, "w") as f:
        f.write(bestBoard + "\n")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
