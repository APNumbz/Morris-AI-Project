# MiniMaxGame.py
# python MiniMaxGame.py inputBoard outputBoard "seach depth"
# python MiniMaxGame.py board1.txt board2.txt 2

import sys

inputBoard = sys.argv[1]
outputBoard = sys.argv[2]
searchDepth = sys.argv[3]

numWhitePieces = 0
numBlackPieces = 0
numBlackMoves = 0

def staticEstimation():
    if (numBlackPieces <= 2):
        return 10000
    elif (numWhitePieces <= 2):
        return -10000
    elif (numBlackMoves == 0):
        return 10000
    else:
        return (1000 * (numWhitePieces - numBlackPieces) - numBlackMoves)
