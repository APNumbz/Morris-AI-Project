# MiniMaxGame.py
# python MiniMaxGame.py inputBoard outputBoard searchDepth
# Example: python MiniMaxGame.py board1.txt board2.txt 2

import sys

inputBoardFile = sys.argv[1]
outputBoardFile = sys.argv[2]
searchDepth = int(sys.argv[3])

with open(inputBoardFile, "r") as f:
    board = f.read().strip()

if len(board) != 23:
    raise ValueError("Board must contain exactly 23 positions.")

for piece in board:
    if piece not in ("W", "B", "x"):
        raise ValueError("Board contains an invalid character.")

# Tracks all adjacent positions on the board
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
    22: [13, 19, 21]
}

# Each tuple represents three positions that form a mill
mills = {
    # Outer square
    (0, 1, 2),
    (0, 3, 6),
    (2, 5, 7),
    (6, 7, 11),

    # Middle square
    (8, 9, 10),
    (8, 17, 20),
    (10, 14, 17),
    (11, 12, 13),

    # Inner square
    (14, 15, 16),
    (16, 18, 19),
    (19, 21, 22),
    (20, 21, 22),

    # Connecting lines
    (1, 4, 5),
    (3, 4, 5),
    (9, 12, 19),
    (15, 18, 21) }

def closeMill(position, board):
    piece = board[position]

    if piece == "x":
        return False

    for mill in mills:
        if position in mill:
            if all(board[i] == piece for i in mill):
                return True

    return False

def GenerateRemove(board, positions):
    removed = False

    for i in range(len(board)):
        if board[i] == "B":
            if not closeMill(i, board):
                newBoard = board[:i] + "x" + board[i + 1:]
                positions.append(newBoard)
                removed = True

    #Following handout when all Black pieces are in mills
    if not removed:
        positions.append(board)

def GenerateMove(board):
    positions = []

    for i in range(len(board)):
        if board[i] == "W":
            for j in neighbors[i]:
                if board[j] == "x":
                    newBoard = board[:i] + "x" + board[i + 1:]
                    newBoard = newBoard[:j] + "W" + newBoard[j + 1:]

                    if closeMill(j, newBoard):
                        GenerateRemove(newBoard, positions)
                    else:
                        positions.append(newBoard)

    return positions

def GenerateHopping(board):
    positions = []

    for i in range(len(board)):
        if board[i] == "W":
            for j in range(len(board)):
                if board[j] == "x":
                    newBoard = board[:i] + "x" + board[i + 1:]
                    newBoard = newBoard[:j] + "W" + newBoard[j + 1:]

                    if closeMill(j, newBoard):
                        GenerateRemove(newBoard, positions)
                    else:
                        positions.append(newBoard)

    return positions

def GenerateMovesMidgameEndgame(board):
    numWhitePieces = board.count("W")

    if numWhitePieces == 3:
        return GenerateHopping(board)
    else:
        return GenerateMove(board)

def swapColors(board):
    newBoard = ""

    for piece in board:
        if piece == "W":
            newBoard += "B"
        elif piece == "B":
            newBoard += "W"
        else:
            newBoard += "x"

    return newBoard

def GenerateBlackMoves(board):
    swappedBoard = swapColors(board)

    whiteMoves = GenerateMovesMidgameEndgame(swappedBoard)

    blackMoves = []

    for position in whiteMoves:
        blackMoves.append(swapColors(position))

    return blackMoves

def staticEstimation(board):
    numWhitePieces = board.count("W")
    numBlackPieces = board.count("B")

    blackMoves = GenerateBlackMoves(board)
    numBlackMoves = len(blackMoves)

    if numBlackPieces <= 2:
        return 10000
    elif numWhitePieces <= 2:
        return -10000
    elif numBlackMoves == 0:
        return 10000
    else:
        return (1000 * (numWhitePieces - numBlackPieces) - numBlackMoves)

positionsEvaluated = 0

def MiniMax(board, depth, maximizing):
    global positionsEvaluated

    if depth == 0:
        positionsEvaluated += 1
        return staticEstimation(board)

    if maximizing:
        possibleMoves = GenerateMovesMidgameEndgame(board)

        if not possibleMoves:
            positionsEvaluated += 1
            return staticEstimation(board)

        bestValue = float("-inf")

        for position in possibleMoves:
            value = MiniMax(position, depth - 1, False)

            if value > bestValue:
                bestValue = value

        return bestValue

    else:
        possibleMoves = GenerateBlackMoves(board)

        if not possibleMoves:
            positionsEvaluated += 1
            return staticEstimation(board)

        bestValue = float("inf")

        for position in possibleMoves:
            value = MiniMax(position, depth - 1, True)

            if value < bestValue:
                bestValue = value

        return bestValue

def main():
    global positionsEvaluated

    possibleMoves = GenerateMovesMidgameEndgame(board)

    bestValue = float("-inf")
    bestBoard = board

    if searchDepth == 0:
        positionsEvaluated += 1
        bestValue = staticEstimation(board)

    else:
        for position in possibleMoves:
            value = MiniMax(position, searchDepth - 1, False)

            if value > bestValue:
                bestValue = value
                bestBoard = position

        if not possibleMoves:
            positionsEvaluated += 1
            bestValue = staticEstimation(board)

    with open(outputBoardFile, "w") as f:
        f.write(bestBoard)

    print("Board Position:", bestBoard)
    print("Positions evaluated by static estimation:", positionsEvaluated)
    print("MINIMAX estimate:", bestValue)

if __name__ == "__main__":
    main()