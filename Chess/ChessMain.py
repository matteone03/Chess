"""
takes player input and displays the state of the game
"""

import pygame as p
import os
from Chess import ChessEngine, ChessAI

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

def load_images(): #INITIALIZES A GLOBAL DICTIONARY WITH IMAGES OF THE PIECES
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname("bB.png"), 'images'))
    for fileName in os.listdir(DATA_DIR):
        fileName = fileName[:2]
        IMAGES[fileName] = p.transform.scale(p.image.load(f"images/{fileName}.png"), (SQ_SIZE, SQ_SIZE))

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    # creates a gamestate, object of class GameState
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    load_images()
    running = True
    sqSelected = ()  # (x,y) selected location
    playerClicks = []  # tracks player clicks, two tuples: [(x1,y1),(x2,y2)]
    gameOver = False
    playerOne = True # if a human is playing white = True, if AI is playing = False
    playerTwo = False
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()  # (x, y) mouse position
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col):  # check if I clicked the same house
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)  # creates Move object
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                if move.startRow == validMoves[i].startRow and move.startCol == validMoves[i].startCol:
                                    gs.make_move(validMoves[i])
                                    moveMade = True
                                    sqSelected = ()
                                    playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_u:
                    gs.undo_move()
                    moveMade = True
                    gameOver = False
                if e.key == p.K_r:  # reset
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    gameOver = False
        #Ai move finder
        if not gameOver and not humanTurn:
            AIMove = ChessAI.findBestMove(gs, validMoves)
            if AIMove == None:
                AIMove = ChessAI.findRandomMove(validMoves)
            gs.make_move(AIMove)
            moveMade = True
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
        drawGamestate(screen, gs, validMoves, sqSelected)
        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "CHECKMATE, BLACK WINS")
            else:
                drawText(screen, "CHECKMATE, WHITE WINS")
        elif gs.staleMate:
            gameOver = True
            drawText(screen, "STALEMATE")
        clock.tick(MAX_FPS)
        p.display.flip()

"""
highlight square selected and possible moves for the piece selecte
"""

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"):  # sqSelected is a piece that can be moved
            # highlight moves
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # transparancy value
            s.fill(p.Color("blue"))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s.fill(p.Color("yellow"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (SQ_SIZE * move.endCol, SQ_SIZE * move.endRow))

def drawGamestate(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)

def drawBoard(screen):
    colors = [p.Color("white"), p.Color("grey")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row + column) % 2)]
            p.draw.rect(screen, color, p.Rect(column * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board):
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            if board[i][j] != "--":
                screen.blit(IMAGES[board[i][j]], p.Rect(j * SQ_SIZE, i * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color("Black"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2,
                                                    HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)

main()
