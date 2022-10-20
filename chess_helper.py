from mimetypes import init
from operator import truediv
from shutil import move
import time
import enum

from baseclasses import *
from iolayers import *

'init'
print("Starting programme")
'1 Hz, long signal = 1, short signal = 0, e.g. 0.75s and 0.25s'
morsefrequency = 1 
morseperc_long = .75
morseperc_short = .25

white_to_move = 1
int_predicted_moves = 0
int_predictions_max = 1
int_engine_thinktime = 5

lpredictedmoves = list()
gameState = GameState.BeforeStart
msgLayer = MorseOutputLayer()

calc_time = 0
'new loop'

time_now = time.time()
time_lastengineupdate = time_now
centipawn_score = 0
input_move = False
last_message_ended = time.time()
actgame = Game(True, True)
enginedone = True

def gameLogic():
    if((actgame.nextMovePlayer == True) and (calc_time >=int_engine_thinktime) and gameState == GameState.Calculating):        
        time_lastengineupdate = time_now
        str_move = stockfish.get_best_move().lower()
        startfield = str_move[0:2]
        str_piece = stockfish.get_what_is_on_square(startfield)
        stockfish_piece = Piece
        stockfish_piece.byFen(stockfish_piece, str_piece.value,actgame.l_pieces)
        start_column = str_move[0]
        stcl_number = ord(start_column) - 96
        start_row = int(str_move[1])

        end_column = str_move[2]        
        endcl_number = ord(end_column) - 96
        end_row = int(str_move[3])       

        stockstartsquare = Square(stcl_number, start_row)
        stockendsquare = Square(endcl_number, end_row)

        stockmove = Move()
        stockmove.fromInstructions(actgame.player_Color,PieceType.Empty,stockstartsquare, stockendsquare)      
        actgame.addMove(stockmove)
        actgame.nextMovePlayer = False

        ' Right now: player has to make the best move, stockfish immediately moves on. Todo: give options to decide for a move'
        stockfish.make_moves_from_current_position([str_move])  
        print("Sending the player a move") 
        print(str_move)

        boardVisual = stockfish.get_board_visual()
        print(boardVisual)
        gameState = GameState.Precalculating  
        msgLayer.BeginMessaging(stockmove.move_signature, morseperc_short, morseperc_long, morsefrequency)   

    'Send the player a possible opponents move after a min time of enginethinktime'
    if(not(actgame.nextMovePlayer)and(calc_time>int_engine_thinktime)):
        if(gameState ==GameState.Precalculating and msgLayer.messagestate == False) :
            gameState =GameState.Idling                
            bestmoves = stockfish.get_top_moves(int_predictions_max)

            index = 0
            for str_move in bestmoves:                    
                start_column = str_move[0].lower()
                stcl_number = ord(start_column) - 96
                start_row = int(str_move[1])

                end_column = str_move[2]        
                endcl_number = ord(end_column) - 96
                end_row = int(str_move[3])       

                stockstartsquare = Square(stcl_number, start_row)
                stockendsquare = Square(endcl_number, end_row)

                stockmove = Move()
                stockmove.fromInstructions(actgame.player_Color, PieceType.Empty, stockstartsquare, stockendsquare)      
                lpredictedmoves.append(stockmove)   
                index = index +1

            print("Sending one possible opponent move")
            print(str_move)

from stockfish import Stockfish
stockfish = Stockfish(r'C:\Program Files\stockfish_15_win_x64\stockfish_15_x64.exe')
stockfish.depth = 20

timeof_gamestart = time.time

boardVisual = stockfish.get_board_visual()
print(boardVisual)

act_column = 0
act_row = 0
act_piectype = PieceType.Empty
for char in boardVisual:
    if(char == '/'):
        act_column = 0
        act_row +=1
    elif(char.isnumeric()):
        act_column += int(char)
    elif(char == ' '):
       break
    else:
        fenPiece = Piece()
        fenPiece.byFen(char, actgame.l_pieces)
        actgame.l_pieces.append(fenPiece)

while(True):
    
    time_now = time.time()
    actgame.board_visual = stockfish.get_board_visual();      
    calc_time = time_now- time_lastengineupdate

    actgame.update()

    'If player morses something'
    if(input_move):      
        'If player morses new move of opponent'  
        if(actgame.nextMovePlayer == False):     
            boardVisual = stockfish.get_board_visual()
            actgame.board_visual = stockfish.get_board_visual()     
            print(actgame.board_visual)           
        
    'Ghert in Zukunft nu geändert. Die Message soll rausgeballert werden, wenn die Engine halbwegs sicher is, aber ma sollt ebenfalls des Zeitkonto miteinbeziehen'
    
    if(gameState == GameState.BeforeStart):
        waitforstart = 0

    'Send the player a move'
    if gameState == GameState.Calculating:
        gameLogic()

    msgLayer.UpdateMessaging(setIO, time_now)      

