import re
import sys
from subprocess import PIPE, Popen
from threading  import Thread

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

def get_channels():
    channels = []
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

def send_command(cmd)
    pianobar.stdin.write(cmd)
    pianobar.stdin.flush()

def start_channel(channel_index):
    cmd = bytearray(repr(channel_index)+'\n', 'utf-8')
    send_command(cmd)

def switch_channel(channel_index):
    cmd = bytearray('s'+repr(channel_index)+'\n', 'utf-8')
    send_command(cmd)
    
def volume_up():
    cmd = bytearray('+', 'utf-8')
    send_command(cmd)

def volume_down():
    cmd = bytearray('-', 'utf-8')
    send_command(cmd)

def next_song():
    cmd = bytearray('n', 'utf-8')
    send_command(cmd)

def like_song():
    cmd = bytearray('TODO', 'utf-8')
    send_command(cmd)

def update_screen(level):
    if level == 'song':
        # Get the song name and current progress
        # Update the screen accordingly
    elif level == 'menu':
        # Get the channel name
        # Update the screen
    else:
        print('Invalid display level')
    return None

if __name__ == "__main__":
    # Give pianobar a few seconds to make contact and login
    sleep(5)
    # Load up the last settings
    current_channel = 0
    # Get the channel list
    channels = get_channels()
    nch = len(channels)
    start_channel(current_channel)
    level = 'song'
    # Loop for user input
    while True:
        try:
            if level == 'menu':
                if button == UP:
                    current_channel = mod(current_channel+1, nch)
                elif button == DOWN:
                    current_channel = mod(current_channel-1, nch)
                elif button == RIGHT:
                    level = 'song'
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
            update_display(level)
        except: #ctrl-c
            break
    print('Shutting down.')

