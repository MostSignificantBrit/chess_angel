from mimetypes import init
from operator import truediv
from shutil import move
import time
import enum

from baseclasses import *

''' import alle the Rapsi IO Stuff
from gpiozero import Button
from gpiozero import DigitalOutputDevice
vibr = DigitalOutputDevice(26)
'''
def vibr():
    x=1

def Button():
    x=1

def readButton():    
    # left click
   x = 1

def setIO(Iotype, signal):
    if(signal):
        'print("Set vibration ON")'
        'vibr.on()'
    else:
        'print("Set vibration OFF")'
        'vibr.off()'

# binary code signals:
# 0 = short high, long low; 1 = long high, short low; frequency = 1 / lengthofhigh+low;

# MODE SETTINGS (is also the start menu)
# 1, 1, 1 -> return to settings
# before Start: 0, 0: set playercolor, then 0 = set playercol White, 1 = set playesrcol Black
# 2x length -> start game

# MODE GAME
# any binary number -> move code
# 2x length -> go into mode break
# a) while making an input: abort and repeat move input
# b) else: go into settings

# MODE BREAK
# 0, 0 + bin(x) -> remove the last x half moves from the move stack (for correcting erronious inputs)
# 1, 0 : switch off IO (for security, only accepts 10s of high to react again)
# 1, 1 : switch off power (last resort)

class MorseInput:
    def __init__(self, actgame):    
        'to prohibit accepting multiple flanks, because of tiny stutters in the tasters any signal must hold longer than a threshhold'
        self.time_lastconfirmedflank =0
        self.time_lastbuttonflank = 0
        self.time_lastbuttonflip = 0

        self.actGame = actgame

        self.time_threshhold = .05
        self.signallength = 0

        'Is the recognized button state pressed = true or !pressed = false'
        self.button_state = False
        self.button_laststate = False

        'Is there a changed button state from the recognized, delayed one right now?'
        self.self.button_changed = False
        'Has the button state changed this cycle?'
        self.button_flank = False

        self.time_now = 0
        self.isListening = True

        self.morsecode = list()   
        self.last_message_ended = time.time()

    def Reset(self):
        self.morsecode = list()   
        self.newMove = Move()

    def Update(self, flankstate, act_game):      

        self.button_flank = False
        self.time_now = time.time()
        self.signallength = 0
        self.actGame = act_game

        'Discard button jitters, under e.g. 50ms'
        'if(there is a buttonchange it will only get accepted as button state and button flank if it is consistent longer than threshhold'
        
        if flankstate and self.button_laststate == False:
            self.button_changed = True
        elif flankstate == False and self.button_laststate:
            self.button_changed = True
        else:
            self.button_changed = False

        if(self.button_changed):
            signallength = self.time_now - self.time_lastbuttonflank

        if(self.time_now - self.time_lastbuttonflank >= self.time_threshhold and self.button_changed):
            self.button_state = flankstate
            self.button_flank = True

        ' not sure if we should invalidate a code after max time'
        ' if self.button_changed and time_now - time_lastbuttonflip < 1.5*morsefrequency:'
             
        'if new Buttonpress has started'
        if self.button_flank and self.button_state == False:
            'Reset everything if pressed long'
            if(signallength >1.5):
                self.morsecode = list()
                act_game.__init__(True, True)

            elif(signallength > 0.4):
                self.morsecode.append(True)          
            else:
                self.morsecode.append(False)

        if(self.button_flank):            
            self.time_lastbuttonflip = self.time_lastbuttonflank
 
        if(self.morsecode.count>=6):
            newMove.fromCode(newMove, self.morsecode, act_game.white_tomove)
            print("Morse input has reached 6 signals, checking....")
            is_move_correct = True; 'stockfish.is_move_correct(newMove.endsquare)'
            print("Is_move_correct:" + is_move_correct)
            if(is_move_correct):
                self.Input_Move_Accepted(self, act_game, newMove)

        elif(self.morsecode.count==15):
            newMove = Move()
            newMove.fromCode(newMove, self.morsecode, act_game.white_tomove)
            self.Input_Move_Accepted(act_game, newMove, time)

    'Checking the input moves is still missing'
    def Input_Move_Accepted(self, act_game, opponent_move):
        print("Input move accepted" + opponent_move)
        act_game.opponentmoveadded(opponent_move)
        self.last_message_ended = time.time()   

 
class MorseOutputLayer:
    def __init__(self):   
        self.inittime = 0              
        self.messagestate = False

    def BeginMessaging(self, int_msg, pct_shortsig, pct_longsig, morsefrequency):

        'convert to Binary and set all needed variables'
        self.bit_count = 0
        self.int_msg = int_msg       
        self.inittime = time.time()
        self.bin_array =list()
        self.messagestate = True
        self.morsefrequency = morsefrequency

        self.pct_shortsig = pct_shortsig/self.morsefrequency
        self.pct_longsig = pct_longsig/self.morsefrequency
        self.array_counter = int(0)

        while (int_msg >0):
            self.bit_count +=1

            next_bit = int_msg % 2
            self.bin_array.append(next_bit)
            int_msg = int_msg // 2

        'I believe it has to be reversed'
        self.bin_array.reverse()

        self.total_sigtime = float(self.bit_count) / float(self.morsefrequency)

    def UpdateMessaging(self, setIO, time_now):
        if(self.messagestate == False):
            return
    
        self.actualtime = time.time() - self.inittime

        if(self.actualtime>self.total_sigtime):
            self.messagestate=False

        if(self.messagestate == False):
            time_lastengineupdate = time_now
            ai_Action = GameState.Precalculating
            last_message_ended = time_now
            print("player finished receiving instructions and makes his move")           

            return
                     
        self.time_between_signal = (self.actualtime / self.morsefrequency) % 1 
        'timebewteen signal = how far from 0 to 1 time has progressed from the beginning of this up to the next up'
        '1 => high -> pct_longsig.time -> low'
        '0 => high -> pct_shortsig.time -> low'
        if((self.bin_array[self.array_counter]==True) and (self.time_between_signal<=self.pct_longsig)):
            setIO(True, 1)
        elif((self.bin_array[self.array_counter]==False) and (self.time_between_signal<=self.pct_shortsig)):  
            setIO(True, 1)
        else:
            setIO(False, 1)

