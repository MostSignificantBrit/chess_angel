import enum
from operator import xor

class GameState(enum.Enum):
    BeforeStart = 0
    Calculating = 1
    Precalculating = 2
    Idling = 3    

class PieceType(enum.Enum):
    Pawn = 0
    Knight = 1
    Bishop = 2
    Rook = 3
    Queen = 4
    King = 5
    Empty = -1

class Piece :

    def __init__(self):
        pass

    def byproperties(self, my_color, piece_type, pieceindex):        
        self.my_color = my_color
        self.piece_type = piece_type
        self.pieceindex = pieceindex

    def byFen(self, charFen, l_pieces):
        self.charFen = charFen
        self.my_color = charFen.isupper()
        charFen_lower = charFen.lower()
        self.piece_type = PieceType.Empty

        self.pieceindex = 0
        if(charFen_lower == 'r'):
            self.piece_type = PieceType.Rook
        elif(charFen_lower == 'n'):
            self.piece_type = PieceType.Knight
        elif(charFen_lower == 'b'):
            self.piece_type = PieceType.Bishop
        elif(charFen_lower == 'q'):
            self.piece_type = PieceType.Queen
        elif(charFen_lower == 'p'):
            self.piece_type = PieceType.Pawn
        elif(charFen_lower == 'k'):
            self.piece_type = PieceType.King

        for other_piece in l_pieces:
            if((other_piece.piece_type == self.piece_type) & (other_piece.my_color == self.my_color)):
                self.pieceindex +=1

class Square:
    def __init__(self, column, row):
        self.column = column
        self.row = row

    def str_square(self):
        columnletter = chr(self.column+97)
        strret = columnletter.join(self.row)
        return strret
        
class Move:   
    def __init__ (self):
        pass

    def fromInstructions (self, move_color, piece_type, startsquare, endsquare):       
            
        self.move_color = move_color
        self.startsquare = startsquare
        self.endsquare = endsquare
        self.piece_type = piece_type      
        self.move_signature = 0


        if(piece_type ==-1):
            
            raise Exception('We have a move without a piece')

        'Well begin with the end square, because its easier to get a good idea about the move from just one coordinate'
        'Bits 0-2 are describing the horizontal end square'
        self.move_signature += self.endsquare.column

        'Bits 3-5 are describing the vertical end square'
        'Once I have a bit more time we should be able to nearly wipe this out'
        self.move_signature += 8 * self.endsquare.row

        'Bits 6-8 are describing the piece type'
        self.move_signature = 64  * int(self.piece_type.value)
        
        'Bits 9-11 are describing the horizontal start square'
        self.move_signature += 256 * self.startsquare.column

        'Bits 12-14 are describing the vertical start square'
        'Once I have a bit more time we should be able to nearly wipe this out'
        self.move_signature += 2056 * self.startsquare.row
        'total number has 15 bit, from 0 to 2^14, number can go up to 2^15'       

        self.has_ended = False


    def fromCode(self, binArray, movecolor):
        self.move_color = movecolor
        self.move_signature = binArray

        for i in range (4):
            startindex = i*3
            listpart = binArray[i:i+2]
            valuenumber = listpart[0]*4 + listpart[1]*2 + listpart[2]
            if(i == 0):
                endcolumn = valuenumber
            elif(i==1):
                endrow = valuenumber
            elif(i==2):
                piecenumber = valuenumber
            elif(i==3):
                startcolumn = valuenumber
            elif(i==4):
                startrow = valuenumber

        self.piece_type = PieceType(piecenumber)
        self.endsquare = Square(endcolumn, endrow)
        self.startsquare = Square(startcolumn, startrow)

    def move_has_ended(self):
        self.has_ended = True

    def output_code(self, msgLayer):
        msgLayer.BeginMessaging(self.move_signature)

class Game:
    def __init__(self, player_Color, sendAIMoves):
        'True means player is White'
        self.player_Color = player_Color

        'White has next move'
        self.white_tomove = True
        
        'Player has net next move'
        self.nextMovePlayer = self.player_Color
        self.round = 0
        self.moves = list()
        self.sendAIMovoes = sendAIMoves
        self.AiAction = GameState(0)
        self.l_pieces = list()        


    def update(self):
        self.white_tomove = not xor (self.nextMovePlayer, self.player_Color)  

    def addMove(self, newMove):
        self.moves.append(newMove)
        if(not(self.white_tomove)):
            self.round +=1
        self.white_tomove = not self.white_tomove

    def opponentmoveadded(self, opponent_move):
        self.moves.append(opponent_move)
        self.input_zug = True
        self.ai_Action=GameState.Calculating
        self.nextMovePlayer = True       

class MovePair:
    def __init__(self, move_round):
        pass

