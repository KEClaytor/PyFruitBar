import re
from time import sleep
import sys
from subprocess import PIPE, Popen
from threading  import Thread

# Configure LCD Plate
import Adafruit_CharLCD as LCD
lcd = LCD.Adafruit_CharLCDPlate()
lcd.set_color(1.0, 1.0, 1.0)
lcd.clear()

# This SO question saved my bacon
# http://stackoverflow.com/questions/375427/non-blocking-read-on-a-subprocess-pipe-in-python
# The proc.stdout.readline() is blocking and hangs when it reaches the end
#   of pianobar's output (where it waits for user input)
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

ON_POSIX = 'posix' in sys.builtin_module_names
def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()

pianobar = Popen(['pianobar'], stdin=PIPE, stdout=PIPE, bufsize=1, close_fds=ON_POSIX)
q = Queue()
t = Thread(target=enqueue_output, args=(pianobar.stdout, q))
t.daemon = True # thread dies with the program
t.start()

# Some key definitions
#LEFT = 'a'
#UP = 'w'
#DOWN = 's'
#RIGHT = 'd'
#SELECT = 'e'
UP = LCD.UP
DOWN = LCD.DOWN
LEFT = LCD.LEFT
RIGHT = LCD.RIGHT
SELECT = LCD.SELECT

def get_channels():
    channels = []
    p = re.compile('(\d{1,})\)[\sqS]{5}(.*)')
    while True:
        try:  line = q.get_nowait() # or q.get(timeout=.1)
        except Empty:
            print('No more channels.')
            break
        else: # got line
            test = line.rstrip().decode("utf-8")
            m = p.search(test)
            #print(test)
            if m is not None:
                (index, name) = p.search(test).groups()
                #print("found: {} {}".format(name, index))
                channels.append(name)
    
    return channels

def get_song_name():
    pass

def get_song_progress():
    pass

def send_command(cmd):
    #print('sending command' + cmd)
    cmd = bytearray(cmd, 'utf-8')
    pianobar.stdin.write(cmd)
    pianobar.stdin.flush()

def start_channel(channel_index):
    cmd = repr(channel_index)+'\n'
    send_command(cmd)

def switch_channel(channel_index):
    cmd = 's'
    send_command(cmd)
    cmd = repr(channel_index)+'\n'
    send_command(cmd)
    
def volume_up():
    print('vol +')
    cmd = ')'
    send_command(cmd)

def volume_down():
    print('vol -')
    cmd = '('
    send_command(cmd)

def next_song():
    print('next')
    cmd = 'n'
    send_command(cmd)

def like_song():
    print('thumbs up')
    cmd = '+'
    send_command(cmd)

def update_display(level, channels, select_channel, current_channel):
    lcd.clear()
    if level == 'start':
        print('Initalizing...')
        lcd.message('Initalizing...')
    elif level == 'song':
        # Get the song name and current progress
        # Update the screen accordingly
        print('Playing a song')
        lcd.message('Now playing:')
    elif level == 'menu':
        # Get the channel name
        # Update the screen
        print(channels[select_channel])
        lcd.message(channels[select_channel])
        if select_channel == current_channel:
            print('Now Playing')
            lcd.message('\nNow playing')
    else:
        print('Invalid display level')
    return None

if __name__ == "__main__":
    # Give pianobar a few seconds to make contact and login
    update_display('start', [], 0, 0)
    sleep(5)
    # Load up the last settings
    current_channel = 0
    select_channel = current_channel
    # Get the channel list
    channels = get_channels()
    nch = len(channels)
    print('Found {} channels'.format(nch))
    start_channel(current_channel)
    level = 'song'
    # Loop for user input
    update_display(level, channels, select_channel, current_channel)
    buttons = (LCD.SELECT, LCD.LEFT, LCD.UP, LCD.DOWN, LCD.RIGHT)
    while True:
        try:
            for button in buttons:
                if lcd.is_pressed(button):
                    #button = input('key: ')
                    if level == 'menu':
                        if button == UP:
                            select_channel = (select_channel+1) % nch
                        elif button == DOWN:
                            select_channel = (select_channel-1) % nch
                        elif button == RIGHT or button == SELECT:
                            level = 'song'
                            current_channel = select_channel
                            print('Starting to play: ' + repr(channels[current_channel]))
                            switch_channel(current_channel)
                        elif button == LEFT:
                            # Quit
                            break
                    elif level == 'song':
                        if button == UP:
                            volume_up()
                        elif button == DOWN:
                            volume_down()
                        elif button == RIGHT:
                            next_song()
                        elif button == LEFT:
                            level = 'menu'
                        elif button == SELECT:
                            like_song()
                    else:
                        print('Invalid level.')
                    update_display(level, channels, select_channel, current_channel)
        except (KeyboardInterrupt, SystemExit):
            pianobar.terminate()
            raise
    print('Shutting down.')
    pianobar.terminate()

