import pyaudio, struct
import numpy as np
from scipy import signal
import math
import tkinter as Tk
import wave
# import playsound  # play .wav files
from threading import Thread
import pygame


BLOCKLEN    = 64        # Number of frames per block
WIDTH       = 2         # Bytes per sample
CHANNELS    = 1         # Mono
RATE        = 8000      # Frames per second

MAXVALUE = 2**15-1      # Maximum allowed output signal value (because WIDTH = 2)

output_wf = wave.open('melody.wav', 'w')    # write to wave file
output_wf.setnchannels(CHANNELS)            # one channel (mono)
output_wf.setsampwidth(WIDTH)               # two bytes per sample (16 bits per sample)
output_wf.setframerate(RATE)                # samples per second
output_wf.setnframes(BLOCKLEN)              # number of frames


# Open wave file
rhythm1 = 'rhythm_cut1.wav'
rhythm2 = 'rhythm2_cut2.wav'
input_wf1 = wave.open(rhythm1, 'rb')
input_wf2 = wave.open(rhythm2, 'rb')

# Read wave file properties
RHYTHM_RATE1        = input_wf1.getframerate()     # Frame rate (frames/second)
RHYTHM_WIDTH1       = input_wf1.getsampwidth()     # Number of bytes per sample
RHYTHM_LEN1         = input_wf1.getnframes()       # Signal length
RHYTHM_CHANNELS1    = input_wf1.getnchannels()     # Number of channels

RHYTHM_RATE2        = input_wf2.getframerate()     # Frame rate (frames/second)
RHYTHM_WIDTH2       = input_wf2.getsampwidth()     # Number of bytes per sample
RHYTHM_LEN2         = input_wf2.getnframes()       # Signal length
RHYTHM_CHANNELS2    = input_wf2.getnchannels()     # Number of channels

# print('rhythm1 has %d channel(s).'         % RHYTHM_CHANNELS1)
# print('rhythm1 has %d frames/second.'      % RHYTHM_RATE1)
# print('rhythm1 has %d frames.'             % RHYTHM_LEN1)
# print('rhythm1 has %d bytes per sample.'   % RHYTHM_WIDTH1)

# print('rhythm2 has %d channel(s).'         % RHYTHM_CHANNELS2)
# print('rhythm2 has %d frames/second.'      % RHYTHM_RATE2)
# print('rhythm2 has %d frames.'             % RHYTHM_LEN2)
# print('rhythm2 has %d bytes per sample.'   % RHYTHM_WIDTH2)

# Number of blocks in wave file
# num_blocks = int(math.floor(RHYTHM_LEN/BLOCKLEN))



print ('Start')
# Parameters
Ta = 2
f0 = 523 # C4

# Pole radius and angle
r = 0.02**(1.0/(Ta*RATE))
ORDER = 2   # filter order

k = [0] * 12
f1 = [0.0] * 12
om1 = [0.0] * 12
a = [[0.0] * 3] * 12
b = [[0.0]] * 12
states = [np.zeros(ORDER)] * 12
x = [np.zeros(BLOCKLEN)] * 12
y = [np.zeros(BLOCKLEN)] * 12
KEY = ''
KEYPRESS = [False] * 12
CONTINUE = True
    

# Buffer to store past signal values. Initialize to zero.
BUFFER_LEN =  1024          # Set buffer length.  Must be more than N!
buffer = [BUFFER_LEN * [0]] * 12   # list of zeros

# Initialize buffer indices
kr = [0] * 12     # read index
kw = [0] * 12     # write index

def initFrequency(i):
    f1[i] = pow(2, k[i] / 12.0) * f0
    om1[i] = 2.0 * math.pi * float(f1[i]) / RATE
    a[i] = [1, -2 * r * math.cos(om1[i]), r**2]
    b[i] = [r * math.sin(om1[i])]


for i in range(12):
    k[i] = i
    # print('key ' + event.char + ' is ' + str(k))
    initFrequency(i)
    states[i] = np.zeros(ORDER)
    x[i] = np.zeros(BLOCKLEN)
    buffer[i] = BUFFER_LEN * [0]   # list of zeros
    kr[i] = 0
    kw[i] = 0
    
    KEYPRESS[i] = False


# Vibrato parameters
# f_v = 2
W = 0.2   # W = 0 for no effect


# Flanger parameters
# f0 = 2
# W = 0.2   # W = 0 for no effect
g = 0.5
depth = 0.01 * RATE # sweep width: M(w) in samples(5ms to 10ms or more)


TYPE = 0 # original

# Initialize pygame mixer
pygame.mixer.init(frequency = RHYTHM_RATE1, channels = 1)


# Open the audio output stream
p = pyaudio.PyAudio()
PA_FORMAT = pyaudio.paInt16
stream = p.open(
        format      = PA_FORMAT,
        channels    = CHANNELS,
        rate        = RATE,
        input       = False,
        output      = True,
        frames_per_buffer = 128)
# specify low frames_per_buffer to reduce latency



def fun_quit():
  global CONTINUE
  print('Good bye')
  CONTINUE = False

def fun_c4():
    # print('C4')
    global KEYPRESS
    KEYPRESS[0] = True

def fun_c40():
    # print('C4#')
    global KEYPRESS
    KEYPRESS[1] = True

def fun_d4():
    # print('D4')
    global KEYPRESS
    KEYPRESS[2] = True
    
def fun_d40():
    # print('D4#')
    global KEYPRESS
    KEYPRESS[3] = True

def fun_e4():
    # print('E4')
    global KEYPRESS
    KEYPRESS[4] = True

def fun_f4():
    # print('F4')
    global KEYPRESS
    KEYPRESS[5] = True

def fun_f40():
    # print('F4#')
    global KEYPRESS
    KEYPRESS[6] = True

def fun_g4():
    # print('G4')
    global KEYPRESS
    KEYPRESS[7] = True

def fun_g40():
    # print('G4#')
    global KEYPRESS
    KEYPRESS[8] = True

def fun_a4():
    # print('A4')
    global KEYPRESS
    KEYPRESS[9] = True

def fun_a40():
    # print('A4#')
    global KEYPRESS
    KEYPRESS[10] = True

def fun_b4():
    # print('B4')
    global KEYPRESS
    KEYPRESS[11] = True
    
def fun_quitkey():
  global CONTINUE
  print('Good bye')
  CONTINUE = False

def fun_c4key(event):
    # print('C4')
    global KEYPRESS
    global KEY
    KEY = event.char
    KEYPRESS[0] = True

def fun_c40key(event):
    # print('C4#')
    global KEYPRESS
    global KEY
    KEY = event.char
    KEYPRESS[1] = True

def fun_d4key(event):
    # print('D4')
    global KEYPRESS
    global KEY
    KEY = event.char
    KEYPRESS[2] = True

def fun_d40key(event):
    # print('D4#')
    global KEYPRESS
    global KEY
    KEY = event.char
    KEYPRESS[3] = True

def fun_e4key(event):
    # print('E4')
    global KEYPRESS
    global KEY
    KEY = event.char
    KEYPRESS[4] = True

def fun_f4key(event):
    # print('F4')
    global KEYPRESS
    global KEY
    KEY = event.char
    KEYPRESS[5] = True

def fun_f40key(event):
    # print('F4#')
    global KEYPRESS
    global KEY
    KEY = event.char
    KEYPRESS[6] = True

def fun_g4key(event):
    # print('G4')
    global KEYPRESS
    global KEY
    KEY = event.char
    KEYPRESS[7] = True

def fun_g40key(event):
    # print('G4#')
    global KEYPRESS
    global KEY
    KEY = event.char
    KEYPRESS[8] = True

def fun_a4key(event):
    # print('A4')
    global KEYPRESS
    global KEY
    KEY = event.char
    KEYPRESS[9] = True

def fun_a40key(event):
    # print('A4#')
    global KEYPRESS
    global KEY
    KEY = event.char
    KEYPRESS[10] = True

def fun_b4key(event):
    # print('B4')
    global KEYPRESS
    global KEY
    KEY = event.char
    KEYPRESS[11] = True



def initial():
  global TYPE
  
  TYPE = 0
  

def vibrato():
  global TYPE
  global BUFFER_LEN
  global buffer
  global kr
  global kw
  
  TYPE = 1
  
  for i in range (12):
      buffer[i] = BUFFER_LEN * [0]   # list of zeros
    
      # Buffer (delay line) indices
      kr[i] = 0  # read index
      kw[i] = int(0.5 * BUFFER_LEN)  # write index (initialize to middle of buffer)


def chorus():
  global TYPE
  global BUFFER_LEN
  global buffer
  global kr
  global kw
  
  TYPE = 2
  
  for i in range (12):
      buffer[i] = BUFFER_LEN * [0]   # list of zeros
    
      # Buffer (delay line) indices
      kr[i] = 0  # read index
      kw[i] = int(0.5 * BUFFER_LEN)  # write index (initialize to middle of buffer)


PLAY_RHYTHM1 = False
PLAY_RHYTHM2 = False
def rhythm1():
    global PLAY_RHYTHM1
    if PLAY_RHYTHM1 == False:
        PLAY_RHYTHM1 = True
    elif PLAY_RHYTHM1 == True:
        PLAY_RHYTHM1 = False

def rhythm2():
    global PLAY_RHYTHM2
    if PLAY_RHYTHM2 == False:
        PLAY_RHYTHM2 = True
    elif PLAY_RHYTHM2 == True:
        PLAY_RHYTHM2 = False


is_recording = False
def record():
    global is_recording
    # global output_wf
    is_recording = True
    
    # output_wf = wave.open('melody.wav', 'w')    # write to wave file
    # output_wf.setnchannels(CHANNELS)            # one channel (mono)
    # output_wf.setsampwidth(WIDTH)               # two bytes per sample (16 bits per sample)
    # output_wf.setframerate(RATE)                # samples per second
    # output_wf.setnframes(BLOCKLEN)              # number of frames

def stopRecording():
    global is_recording
    is_recording = False


# PLAY_RECORD = False
# def play():
#     global PLAY_RECORD
#     PLAY_RECORD = True

# def stopPlaying():
#     global PLAY_RECORD
#     PLAY_RECORD = False




# Define TK root
root = Tk.Tk()
root.bind('q', fun_quitkey)
root.bind('a', fun_c4key)
root.bind('w', fun_c40key)
root.bind('s', fun_d4key)
root.bind('e', fun_d40key)
root.bind('d', fun_e4key)
root.bind('f', fun_f4key)
root.bind('t', fun_f40key)
root.bind('g', fun_g4key)
root.bind('y', fun_g40key)
root.bind('h', fun_a4key)
root.bind('u', fun_a40key)
root.bind('j', fun_b4key)

btn_text1 = Tk.StringVar()
btn_text1.set('C4')
btn_text2 = Tk.StringVar()
btn_text2.set('C4#')
btn_text3 = Tk.StringVar()
btn_text3.set('D4')
btn_text4 = Tk.StringVar()
btn_text4.set('D4#')
btn_text5 = Tk.StringVar()
btn_text5.set('E4')
btn_text6 = Tk.StringVar()
btn_text6.set('F4')
btn_text7 = Tk.StringVar()
btn_text7.set('F4#')
btn_text8 = Tk.StringVar()
btn_text8.set('G4')
btn_text9 = Tk.StringVar()
btn_text9.set('G4#')
btn_text10 = Tk.StringVar()
btn_text10.set('A4')
btn_text11 = Tk.StringVar()
btn_text11.set('A4#')
btn_text12 = Tk.StringVar()
btn_text12.set('B4')

# speed = Tk.DoubleVar() # rhythm speed
# speed.set(5.0)

# Define widgets

frame11 = Tk.Frame(root)
frame11.pack(side = Tk.RIGHT)

frame12 = Tk.Frame(root)
frame12.pack(side = Tk.LEFT)

frame2 = Tk.Frame(frame11)
frame2.pack(side = Tk.TOP)
B_label1 = Tk.Label(frame2, text = ' ')
B_label1.pack(side = Tk.TOP)
B_effect0 = Tk.Button(frame2, command = initial, text = 'No Effect', height = 2, bd = 2, fg = 'black')
B_effect0.pack(side = Tk.LEFT)
B_effect1 = Tk.Button(frame2, command = vibrato, text = 'Effect 1', height = 2, bd = 2, fg = 'black')
B_effect1.pack(side = Tk.LEFT)
B_effect2 = Tk.Button(frame2, command = chorus, text = 'Effect 2', height = 2, bd = 2, fg = 'black')
B_effect2.pack(side = Tk.LEFT)

frame3 = Tk.Frame(frame11)
frame3.pack(side = Tk.TOP)
B_label2 = Tk.Label(frame3, text = 'Sound effects')
B_label2.pack()
B_label3 = Tk.Label(frame3, text = ' ')
B_label3.pack()

frame4 = Tk.Frame(frame11)
frame4.pack(side = Tk.TOP)
B_rhythm1 = Tk.Button(frame4, command = rhythm1, text = 'Rhythm1', height = 2, bd = 2, fg = 'black')
B_rhythm1.pack(side = Tk.LEFT)
B_rhythm2 = Tk.Button(frame4, command = rhythm2, text = 'Rhythm2', height = 2, bd = 2, fg = 'black')
B_rhythm2.pack(side = Tk.LEFT)

frame5 = Tk.Frame(frame11)
frame5.pack(side = Tk.TOP)
B_label4 = Tk.Label(frame5, text = 'Press once: Play    Press again: Stop')
B_label4.pack()
B_label5 = Tk.Label(frame5, text = ' ')
B_label5.pack()

frame6 = Tk.Frame(frame11)
frame6.pack(side = Tk.TOP)
B_record = Tk.Button(frame6, command = record, text = 'Record', height = 2, bd = 2, fg = 'black')
B_record.pack(side = Tk.LEFT)
B_stop_record = Tk.Button(frame6, command = stopRecording, text = 'Stop Record', height = 2, bd = 2, fg = 'black')
B_stop_record.pack(side = Tk.LEFT)
# B_play = Tk.Button(frame1, command = play, text = 'Play', height = 2, bd = 2, fg = 'black')
# B_play.pack(side = Tk.LEFT)
# B_stop_play = Tk.Button(frame1, command = stopPlaying, text = 'Stop Play', height = 2, bd = 2, fg = 'black')
# B_stop_play.pack(side = Tk.LEFT)
# S_speed = Tk.Scale(root, label = 'rhythm speed', variable = speed, from_ = 0, to = 10, length = 300, width = 20)
# S_speed.pack(side = Tk.LEFT)


frame7 = Tk.Frame(frame11)
frame7.pack(side = Tk.TOP)
B_label6 = Tk.Label(frame7, text = '     Sound of piano keys will be saved in \'melody.wav\'     ')
B_label6.pack()
B_label7 = Tk.Label(frame7, text = ' ')
B_label7.pack()

frame8 = Tk.Frame(frame12)
frame8.pack(side = Tk.TOP)
B_label18 = Tk.Label(frame8, font = 14, text = ' ')
B_label18.pack(side = Tk.TOP)
B_label8 = Tk.Label(frame8, font = 14, text = 'Can be pressed by MOUSE')
B_label8.pack(side = Tk.TOP)
B_label9 = Tk.Label(frame8, font = 14, text = 'or by KEYBOARD \'a, w, s, e, d, f, t, g, y, h\'')
B_label9.pack(side = Tk.TOP)
B_label10 = Tk.Label(frame8, text = '  ')
B_label10.pack(side = Tk.TOP)

frame9 = Tk.Frame(frame12)
frame9.pack(side = Tk.TOP)
B_c40 = Tk.Button(frame9, command = fun_c40, textvariable = btn_text2, padx = 8, pady = 8, height = 6, bd = 8, bg = 'black', fg = 'white')
B_c40.pack(side = Tk.LEFT)
B_label11 = Tk.Label(frame9, text = ' ')
B_label11.pack(side = Tk.LEFT)
B_c40 = Tk.Button(frame9, command = fun_d40, textvariable = btn_text4, padx = 8, pady = 8, height = 6, bd = 8, bg = 'black', fg = 'white')
B_c40.pack(side = Tk.LEFT)
B_label12 = Tk.Label(frame9, text = '             ')
B_label12.pack(side = Tk.LEFT)
B_c40 = Tk.Button(frame9, command = fun_f40, textvariable = btn_text7, padx = 8, pady = 8, height = 6, bd = 8, bg = 'black', fg = 'white')
B_c40.pack(side = Tk.LEFT)
B_label13 = Tk.Label(frame9, text = ' ')
B_label13.pack(side = Tk.LEFT)
B_c40 = Tk.Button(frame9, command = fun_g40, textvariable = btn_text9, padx = 8, pady = 8, height = 6, bd = 8, bg = 'black', fg = 'white')
B_c40.pack(side = Tk.LEFT)
B_label14 = Tk.Label(frame9, text = ' ')
B_label14.pack(side = Tk.LEFT)
B_c40 = Tk.Button(frame9, command = fun_a40, textvariable = btn_text11, padx = 8, pady = 8, height = 6, bd = 8, bg = 'black', fg = 'white')
B_c40.pack(side = Tk.LEFT)

frame10 = Tk.Frame(frame12)
frame10.pack(side = Tk.TOP)
B_c4 = Tk.Button(frame10, command = fun_c4, textvariable = btn_text1, padx = 16, pady = 16, height = 8, bd = 8, fg = 'black')
B_c4.pack(side = Tk.LEFT)
B_d4 = Tk.Button(frame10, command = fun_d4, textvariable = btn_text3, padx = 16, pady = 16, height = 8, bd = 8, fg = 'black')
B_d4.pack(side = Tk.LEFT)
B_d4 = Tk.Button(frame10, command = fun_e4, textvariable = btn_text5, padx = 16, pady = 16, height = 8, bd = 8, fg = 'black')
B_d4.pack(side = Tk.LEFT)
B_d4 = Tk.Button(frame10, command = fun_f4, textvariable = btn_text6, padx = 16, pady = 16, height = 8, bd = 8, fg = 'black')
B_d4.pack(side = Tk.LEFT)
B_d4 = Tk.Button(frame10, command = fun_g4, textvariable = btn_text8, padx = 16, pady = 16, height = 8, bd = 8, fg = 'black')
B_d4.pack(side = Tk.LEFT)
B_d4 = Tk.Button(frame10, command = fun_a4, textvariable = btn_text10, padx = 16, pady = 16, height = 8, bd = 8, fg = 'black')
B_d4.pack(side = Tk.LEFT)
B_d4 = Tk.Button(frame10, command = fun_b4, textvariable = btn_text12, padx = 16, pady = 16, height = 8, bd = 8, fg = 'black')
B_d4.pack(side = Tk.LEFT)

key_range = Tk.IntVar()
# range.set(1)
slider = Tk.Scale(frame12, from_ = 0, to = 2, variable = key_range, orient = Tk.HORIZONTAL, showvalue = 0, length = 580, width = 20)
slider.set(1)
slider.pack()
B_label15 = Tk.Label(frame12, text = 'left: C3-B3            center: C4-B4            right: C5-B5')
B_label15.pack()

B_label16 = Tk.Label(frame12, text = ' ')
B_label16.pack()
B_label17 = Tk.Label(frame12, text = ' ')
B_label17.pack()

B_quit = Tk.Button(frame11, command = fun_quit, text = 'Quit', height = 2, bd = 2, fg = 'black', width = 10)
B_quit.pack()


def set_key(r):
    global f0
    if r == 0:
        f0 = 523 / 2
        btn_text1.set('C3')
        btn_text2.set('C3#')
        btn_text3.set('D3')
        btn_text4.set('D3#')
        btn_text5.set('E3')
        btn_text6.set('F3')
        btn_text7.set('F3#')
        btn_text8.set('G3')
        btn_text9.set('G3#')
        btn_text10.set('A3')
        btn_text11.set('A3#')
        btn_text12.set('B3')
    elif r == 1:
        f0 = 523
        btn_text1.set('C4')
        btn_text2.set('C4#')
        btn_text3.set('D4')
        btn_text4.set('D4#')
        btn_text5.set('E4')
        btn_text6.set('F4')
        btn_text7.set('F4#')
        btn_text8.set('G4')
        btn_text9.set('G4#')
        btn_text10.set('A4')
        btn_text11.set('A4#')
        btn_text12.set('B4')
    elif r == 2:
        f0 = 523 * 2
        btn_text1.set('C5')
        btn_text2.set('C5#')
        btn_text3.set('D5')
        btn_text4.set('D5#')
        btn_text5.set('E5')
        btn_text6.set('F5')
        btn_text7.set('F5#')
        btn_text8.set('G5')
        btn_text9.set('G5#') 
        btn_text10.set('A5')
        btn_text11.set('A5#')
        btn_text12.set('B5')
    for i in range(12):
        initFrequency(i)


def play_notes():
        
    if TYPE == 0:
        ytotal = np.zeros(BLOCKLEN)
        for i in range(12):
            if KEYPRESS[i] and CONTINUE:
                x[i][0] = 10000.0
                
            [y[i], states[i]] = signal.lfilter(b[i], a[i], x[i], zi = states[i])
            
            x[i][0] = 0.0
            KEYPRESS[i] = False
            
            y[i] = np.clip(y[i].astype(int), -MAXVALUE, MAXVALUE)     # Clipping
            ytotal += y[i]
        
        
    elif TYPE == 1:
        ytotal = np.zeros(BLOCKLEN)
        for i in range(12):
            if KEYPRESS[i] and CONTINUE:
                x[i][0] = 10000.0
            
            [y[i], states[i]] = signal.lfilter(b[i], a[i], x[i], zi = states[i])
            
            x[i][0] = 0.0
            KEYPRESS[i] = False
            
            tmp = np.zeros(BLOCKLEN)
            for j in range(0, BLOCKLEN):
                # Get previous and next buffer values (since kr is fractional)
                kr_prev = int(math.floor(kr[i]))
                frac = kr[i] - kr_prev    # 0 <= frac < 1
                kr_next = kr_prev + 1
                if kr_next == BUFFER_LEN:
                    kr_next = 0
            
                # Compute output value using interpolation
                tmp[j] = (1 - frac) * buffer[i][kr_prev] + frac * buffer[i][kr_next]
            
                # Update buffer
                buffer[i][kw[i]] = y[i][j]
            
                # Increment read index
                kr[i] = kr[i] + 1 + W * math.sin( 2 * math.pi * f0 * j / RATE )
                    # Note: kr is fractional (not integer!)
            
                # Ensure that 0 <= kr < BUFFER_LEN
                if kr[i] >= BUFFER_LEN:
                    # End of buffer. Circle back to front.
                    kr[i] = kr[i] - BUFFER_LEN
            
                # Increment write index    
                kw[i] = kw[i] + 1
                if kw[i] == BUFFER_LEN:
                    # End of buffer. Circle back to front.
                    kw[i] = 0
            
            tmp = np.clip(tmp.astype(int), -MAXVALUE, MAXVALUE)     # Clipping
            ytotal += tmp
        
    elif TYPE == 2:
        ytotal = np.zeros(BLOCKLEN)
        for i in range(12):
            if KEYPRESS[i] and CONTINUE:
                x[i][0] = 10000.0
            
            [y[i], states[i]] = signal.lfilter(b[i], a[i], x[i], zi = states[i])
            
            x[i][0] = 0.0
            KEYPRESS[i] = False
            
            tmp = np.zeros(BLOCKLEN)
            for j in range(0, BLOCKLEN):
                # Get previous and next buffer values (since kr is fractional)
                kr_prev = int(math.floor(kr[i]))
                frac = kr[i] - kr_prev    # 0 <= frac < 1
                kr_next = kr_prev + 1
                if kr_next == BUFFER_LEN:
                    kr_next = 0
            
                # Compute output value using interpolation
                tmp[j] = y[i][j] + 0.5 * ((1-frac) * buffer[i][kr_prev] + frac * buffer[i][kr_next])
                
                # Update buffer
                buffer[i][kw[i]] = y[i][j]
            
                # Increment read index
                kr[i] = kr[i] + 1 + depth / 2.0 / 80 * math.sin(2 * math.pi * 2 * j / RATE)
                    # Note: kr is fractional (not integer!)
            
                # Ensure that 0 <= kr < BUFFER_LEN
                if kr[i] >= BUFFER_LEN:
                    # End of buffer. Circle back to front.
                    kr[i] = kr[i] - BUFFER_LEN
            
                # Increment write index    
                kw[i] = kw[i] + 1
                if kw[i] == BUFFER_LEN:
                    # End of buffer. Circle back to front.
                    kw[i] = 0
                    
            tmp = np.clip(tmp.astype(int), -MAXVALUE, MAXVALUE)     # Clipping
            ytotal += tmp

        
    ytotal = np.clip(ytotal.astype(int), -MAXVALUE, MAXVALUE)     # Clipping

    binary_data = struct.pack('h' * BLOCKLEN, *ytotal);    # Convert to binary binary data
    stream.write(binary_data, BLOCKLEN)
    
    # write signal to wave file
    if is_recording:
        output_wf.writeframes(binary_data)
    


def play_rhythm():
    global PLAY_RHYTHM1, PLAY_RHYTHM2
    # global rhythm1, rhythm2
    # print('play', wavfile)
    
    # playsound.playsound(wavfile)
    
    
    # pygame.mixer.pre_init(frequency = (int)(RHYTHM_RATE1), channels = 1)
    
    # pygame.mixer.music.load(wavfile)
    # pygame.mixer.music.play()
    my_sound = pygame.mixer.Sound('rhythm_cut1.wav')
    if PLAY_RHYTHM1:
        my_sound = pygame.mixer.Sound('rhythm_cut1.wav')
    elif PLAY_RHYTHM2:
        my_sound = pygame.mixer.Sound('rhythm2_cut2.wav')
    my_sound.set_volume(0.3)
    my_sound.play()
    # time.sleep(2.01)
    # pygame.mixer.quit()


def play_record():
    global PLAY_RECORD

    wav = wave.open('melody.wav', 'rb')
    LEN = wav.getnframes()
    # Number of blocks in wave file
    num_blocks = int(math.floor(LEN/BLOCKLEN))
    
    # Go through wave file 
    for i in range(0, num_blocks):
    
        # Get block of samples from wave file
        input_bytes = wav.readframes(BLOCKLEN)     # BLOCKLEN = number of frames to read
    
        # Write binary data to audio output stream
        stream.write(input_bytes)
    # pygame.mixer.init(frequency = RATE, channels = 1)
    # my_sound = pygame.mixer.Sound('melody.wav')
    # my_sound.play()
    
    

# CONTINUE = True
while CONTINUE:
    root.update()
    
    set_key(key_range.get())
    
    # threads = []

    # if (not pygame.mixer.get_busy()) and (PLAY_RHYTHM1 or PLAY_RHYTHM2):
    #     # pygame.mixer.quit()
    #     thread1 = Thread(target = play_rhythm)
    #     threads.append(thread1)
    #     thread1.start()
    #     thread1.join()
    
    
    # thread2 = Thread(target = play_notes)
    # threads.append(thread2)
    # thread2.start()
    # thread2.join()
    
    # if PLAY_RECORD:
    #     thread3 = Thread(target = play_record)
    #     threads.append(thread3)
    #     thread3.start()
    #     thread3.join()
    
    if ((not PLAY_RHYTHM1) and (not PLAY_RHYTHM2)):
        pygame.mixer.stop()
    if (not pygame.mixer.get_busy()) and (PLAY_RHYTHM1 or PLAY_RHYTHM2):
        play_rhythm()
    
    play_notes()



print('* Finished')

# pygame.mixer.stop()
pygame.mixer.quit()
stream.stop_stream()
stream.close()
p.terminate()
input_wf1.close()
input_wf2.close()
output_wf.close()