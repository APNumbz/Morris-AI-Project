# MiniMaxOpening.py
# python MiniMaxOpening.py inputBoard outputBoard "seach depth"
# python MiniMaxOpening.py board1.txt board2.txt 2

import sys

inputBoardFile = sys.argv[1]
outputBoardFile = sys.argv[2]
searchDepth = sys.argv[3]

with open(inputBoardFile, "r") as f:
    board = f.read().strip()

numWhitePieces = 9
numBlackPieces = 9

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

def GenerateAdd(boardPosition):
    global board

    if (board[boardPosition] == "x"):
        board = board[:boardPosition] + "W" + board[boardPosition + 1:]
    print(board)
    return

def GenerateHopping():
    return

def GenerateRemove(boardPosition):
    global board

    if (board[boardPosition] == "W"):
        board = board[:boardPosition] + "x" + board[boardPosition + 1:]
    return

def staticEstimation():
    return (numWhitePieces - numBlackPieces)
