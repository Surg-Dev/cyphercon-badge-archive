# Copyright (C) 2023 tymkrs
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name of tymkrs shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization from tymkrs.

import mode
import buttons
import rgb
import prng
import screen
import network
import logogen

##
# Story Engine Globals
##

# world constants
WORLD_ENTRY                 = 0 # world key: first load, starting position
WORLD_POSITION_INDEX        = 1 # world key: what position the world is on
WORLD_CLOCK_INDEX           = 2 # world key: how many positions the engine has rendered for this world

# user constants
USER_ID_INDEX               = 0
USER_POSITION_INDEX         = 1
USER_NAME_INDEX             = 2

# world globals
warped                      = ''
world_key_len               = 0
world_key_file              = ''
cache_lookup                = []
cache_key                   = []

address_name                = []
address_line                = []

# user globals
user_key                    = []
loaded_id                   = 999

# player globals
player_id                   = 0

# button globals
button_action               = [''] * 6
button_active               = [False] * 6
button_next                 = 0

##
#   Story Engine Functions
##

def initialize():
    global player_id
    #load serial file
    f1 = open('serial', 'rb')
    player_id = int.from_bytes(f1.read(2), 'big')
    f1.close()
    real_or_imaginary(player_id)

def start_badge_adventure(): # mode 3
    mode.ui_mode = mode.BADGE_ADVENTURE_MODE
    print('starting badge adventure mode')

    if warped == '':
        f1 = open('serial', 'rb')
        world_file_name = f1.read()
        world_file_name = world_file_name[2:len(world_file_name)]
        f1.close()
        world_file = world_file_name.decode('utf-8')
        print('serial#' + str(player_id) + ' world|' + world_file + '|')
        load_world('world/' + world_file)
    else:
        world_file = warped + '.static'
        print('serial#' + str(player_id) + ' world|' + world_file + '|')
        load_world('world/' + world_file)

    load_user(player_id)
    screen.set_cursor(0, 0)
    screen.clear_screen()
    screen.render_arttext(render_world())

def warp(world_name):
    global cache_lookup, cache_key, warped
    warped = ''
    cache_lookup = []
    cache_key = []
    mode.ui_mode = mode.BADGE_ADVENTURE_MODE
    print('starting badge adventure mode')
    world_file = world_name + '.static'
    print('serial#' + str(player_id) + ' world|' + world_file + '|')
    load_world('world/' + world_file)
    load_user(player_id)
    screen.set_cursor(0, 0)
    screen.clear_screen()
    screen.render_arttext(render_world())

def silent_warp(world_name):
    global warped, cache_lookup, cache_key
    cache_lookup = []
    cache_key = []
    warped = world_name

def badge_adventure_click(user_input):
    if buttons.button_active[user_input] == True:
        # update the world position key with the value stowed for this button
        print('button action: ' + buttons.button_action[user_input])
        wset('1|' + buttons.button_action[user_input]) # (key,value)

        screen.set_cursor(0, 0)
        screen.clear_screen()
        screen.render_arttext(render_world())

        rgb.setRGBleds((0b000000000000, 0b111111111111, 0b100100100100, 0b110110110110, 0b010010010010, 0b011011011011, 0b001001001001, 0b101101101101)[mode.ui_color])

def render_world():

    # clock the world forward
    world_clock = magicint(get_world_key(WORLD_CLOCK_INDEX))
    world_clock = world_clock + 1
    set_world_key(WORLD_CLOCK_INDEX, str(world_clock))

    # load the world position
    print('getting world posistion')
    world_position = magicint(get_world_key(WORLD_POSITION_INDEX))
    print('world_position: ' + str(world_position))

    # load the key for this position
    print(world_position)
    working_key = get_world_key(world_position)
    print('work: ' + working_key)

    # display the parse of the key for this position
    return parse_key(working_key)

def parse_key(working_key):

    #reset the global button variables back to initial states
    buttons.empty()

    while(True):

        rgb.bump_rgb()

        # evaluate any environment variables
        working_key = parse_environment_variables(working_key)

        # check to see if there are any commands remaining
        if check_command(working_key) == False:
            return working_key

        # check to see if there is a random command
        # if so, evaluate the random()
        if working_key.find('$random(') != -1:
            working_key = parse_random_command(working_key)
            continue

        # check to see if there is a pick command
        # if so, go evaluate the first parameter then the pick()
        if working_key.find('$pick(') != -1:
            working_key = parse_pick_command(working_key)
            continue

        # check to see if there is an if command
        # if so, go evaluate the first two parameters then the equal()
        if working_key.find('$if(') != -1:
            working_key = parse_if_command(working_key)
            continue

        # evaluate a remaining simple command()
        working_key = parse_simple_command(working_key)

def parse_environment_variables(working_key):
    rgb.bump_rgb()

    global player_id, user_key, USER_NAME_INDEX, WORLD_CLOCK_INDEX

    if working_key.find('{player_name}') != -1:
        load_user(player_id)

    # variables
    working_key = working_key.replace('{player_name}', user_key[USER_NAME_INDEX])
    working_key = working_key.replace('{player_id}', convert_base_10_to_base_6(player_id))
    working_key = working_key.replace('{world_clock}', get_world_key(WORLD_CLOCK_INDEX))

    # constants
    working_key = working_key.replace('{USER_NAME_INDEX}', str(USER_NAME_INDEX))

    return working_key

def check_command(working_key): # test a string to discover if there is a command in it, without regex :)
    rgb.bump_rgb()

    # fail if there is no (
    if '(' in working_key:
        pass
    else:
        return False

    # fail if there is no )
    if ')' in working_key:
        pass
    else:
        return False

    # fail if there is no $
    if '$' in working_key:
        pass
    else:
        return False

    # fail if the (open falls after the )close
    if working_key.find('(') > working_key.find(')'):
        return False

    # fail if the $head falls after the (open
    if working_key.find('$') > working_key.find('('):
        return False

    # fail if there is not a character or more between $head and (open
    if (working_key.find('(') - working_key.find('$')) < 2:
        return False

    # fail if there is not a character or more between (open and )close
    if (working_key.find(')') - working_key.find('(')) < 2:
        return False

    # if we have not failed by here then we pass
    return True

def parse_random_command(working_key):
    rgb.bump_rgb()

    command_head            = working_key.find('$random(')
    command_open            = command_head + 7

    open_count              = 0
    last_close              = working_key.rfind(')')

    # check to make sure there is a command close
    if last_close == -1:
        return 'random: there is no command close! '

    # walk forward, looking for the command close to our command open
    for i in range(command_open + 1, last_close + 1):

        # check if this position is a sub-command open
        if working_key[i:i+1] == '(':
            open_count = open_count + 1

        # check if this position is a command close
        if working_key[i:i+1] == ')':
            # check if the command close is for our command or for a sub-command
            if open_count == 0:
                # this is the close of our command
                command_close = i
                command_params          = working_key[command_open + 1:command_close]
                command_type            = working_key[command_head + 1:command_open]
                command_whole           = working_key[command_head:command_close + 1]

                working_key = working_key.replace(command_whole, command_params.split('|')[prng.step(rgb.rgb_prng, 0, len(command_params.split('|')))], 1)
                # all done, send the results back up to parse_key()
                return working_key
            else:
                # this is the close of a sub-command
                open_count = open_count - 1

def parse_pick_command(working_key):
    rgb.bump_rgb()

    command_head            = working_key.find('$pick(')
    command_open            = command_head + 5

    open_count              = 0
    last_close              = working_key.rfind(')')

    # check to make sure there is a command close
    if last_close == -1:
        return 'pick: there is no command close! '

    # walk forward, looking for the command close to our command open
    for i in range(command_open + 1, last_close + 1):

        # check if this position is a sub-command open
        if working_key[i:i+1] == '(':
            open_count = open_count + 1

        # check if this position is a command close
        if working_key[i:i+1] == ')':
            # check if the command close is for our command or for a sub-command
            if open_count == 0:
                # this is the close of our command
                command_close = i
                command_params = working_key[command_open + 1:command_close]
                command_type = working_key[command_head + 1:command_open]
                command_whole = working_key[command_head:command_close + 1]

                # fully evaluate the first param, this is recursive :/
                first_param = parse_key(command_params.split('|')[0])

                # replace the pre-evaluated first param with the post-evaluated first param
                command_params = command_params.replace(command_params.split('|')[0], first_param, 1)

                # do the actual pick
                working_key = working_key.replace(command_whole, pick(command_params), 1)

                # all done, send the results back up to the parse_key()
                return working_key

            else:
                # this is the close of a sub-command
                open_count = open_count - 1

    return 'pick parse faceplant'

def pick(command_params): #$pick(index,option0,option1,etc)
    rgb.bump_rgb()
    if magicint(command_params.split('|')[0]) + 1 > 0 and magicint(command_params.split('|')[0]) + 1 < len(command_params.split('|')):
        return command_params.split('|')[magicint(command_params.split('|')[0]) + 1]
    else:
        return ''

def parse_if_command(working_key):
    rgb.bump_rgb()

    command_head            = working_key.find('$if(')
    command_open            = command_head + 3

    open_count              = 0
    last_close              = working_key.rfind(')')

    # check to make sure there is a command close
    if last_close == -1:
        return 'if: there is no command close'

    # walk forward, looking for the command close to our command open
    for i in range(command_open + 1, last_close + 1):

        # check if this position is a sub-command open
        if working_key[i:i+1] == '(':
            open_count = open_count + 1

        # check if this position is a command closeequal
        if working_key[i:i+1] == ')':
            # check if the command close is for our command or for a sub-command
            if open_count == 0:
                # this is the close of our command
                command_close = i
                command_params          = working_key[command_open + 1:command_close]
                command_type            = working_key[command_head + 1:command_open]
                command_whole           = working_key[command_head:command_close + 1]

                # fully evaluate the first param, this is recursive :/
                first_param             = parse_key(command_params.split('|')[0])

                # fully evaluate the second param, this is recursive :/
                second_param            = parse_key(command_params.split('|')[1])

                # replace the pre-evaluated first param with the post-evaluated first param
                command_params = command_params.replace(command_params.split('|')[0], first_param, 1)

                # replace the pre-evaluated second param with the post-evaluated second param
                command_params = command_params.replace(command_params.split('|')[1], second_param, 1)

                # do the actual pick
                working_key = working_key.replace(command_whole, eval_if(command_params), 1)

                # all done, send the results back up to the parse_key()
                return working_key

            else:
                # this is the close of a sub-command
                open_count = open_count - 1

    return 'if parse faceplant'

def eval_if(command_params): # $if(value0|value1|action0|action1) if value0 == value1 then action0 else action1
    rgb.bump_rgb()
    if command_params.split('|')[0] == command_params.split('|')[1]:
        return command_params.split('|')[2]
    else:
        return command_params.split('|')[3]

def parse_simple_command(working_key):
    rgb.bump_rgb()

    command_close           = working_key.find(')')
    command_head            = working_key.rfind('$', 0, command_close)
    command_open            = working_key.find('(', command_head, command_close)
    command_params          = working_key[command_open + 1:command_close]
    command_type            = working_key[command_head + 1:command_open]
    command_whole           = working_key[command_head:command_close + 1]

    if command_type == 'append':
        working_key = working_key.replace(command_whole , append(command_params), 1)
        return working_key

    if command_type == 'wset':
        working_key = working_key.replace(command_whole , wset(command_params), 1)
        return working_key

    if command_type == 'uset':
        working_key = working_key.replace(command_whole , b10tob6(command_params), 1)
        return working_key

    if command_type == 'pset':
        working_key = working_key.replace(command_whole , pset(command_params), 1)
        return working_key

    if command_type == 'wget':
        working_key = working_key.replace(command_whole , wget(command_params), 1)
        return working_key

    if command_type == 'uget':
        working_key = working_key.replace(command_whole , uget(command_params), 1)
        return working_key

    if command_type == 'pget':
        working_key = working_key.replace(command_whole , pget(command_params), 1)
        return working_key

    if command_type == '>':
        working_key = working_key.replace(command_whole , greater_than(command_params), 1)
        return working_key

    if command_type == '<':
        working_key = working_key.replace(command_whole , less_than(command_params), 1)
        return working_key

    if command_type == '==':
        working_key = working_key.replace(command_whole , equal(command_params), 1)
        return working_key

    if command_type == '!=':
        working_key = working_key.replace(command_whole , not_equal(command_params), 1)
        return working_key

    if command_type == '+':
        working_key = working_key.replace(command_whole , add(command_params), 1)
        return working_key

    if command_type == '-':
        working_key = working_key.replace(command_whole , subtract(command_params), 1)
        return working_key

    if command_type == 'limit':
        working_key = working_key.replace(command_whole , limit(command_params), 1)
        return working_key

    if command_type == 'b6tob10':
        working_key = working_key.replace(command_whole , b6tob10(command_params), 1)
        return working_key

    if command_type == 'b10tob6':
        working_key = working_key.replace(command_whole , b10tob6(command_params), 1)
        return working_key

    if command_type == 'button':
        working_key = working_key.replace(command_whole , button(command_params), 1)
        return working_key

    return working_key.replace(command_whole, '', 1)

##
# Command Functions
##

def append(command_params): #$append(key|value|maxlen)
    rgb.bump_rgb()
    if len(get_world_key(magicint(command_params.split('|')[0]))) + len(command_params.split('|')[1]) <= magicint(command_params.split('|')[2]):
        set_world_key(magicint(command_params.split('|')[0]), get_world_key(magicint(command_params.split('|')[0])) + command_params.split('|')[1])
    return ''

def wset(command_params): # $wset(key|value)
    rgb.bump_rgb()
    global world_key_len
    key = magicint(command_params.split('|')[0])
    value = command_params.split('|')[1]
    if key < 0:
        return ''
    elif key >= world_key_len:
        return ''
    else:
        set_world_key(key, value)
        return ''

def uset(command_params): # $uset(id|key|value)
    rgb.bump_rgb()
    load_user(magicint(command_params.split('|')[0]))
    user_key[dancemagicint(command_params.split('|')[1])] = command_params.split('|')[2]
    repack_user_file_to_disk(magicint(command_params.split('|')[0])) # save player data back to player file here
    return ''

def pset(command_params): # $pset(key|value)
    rgb.bump_rgb()
    global player_id
    return uset(str(player_id) + '|' + command_params)

def wget(command_params): # $wget(key)
    rgb.bump_rgb()
    key = magicint(command_params)
    if key < 0:
        return ''
    elif key >= world_key_len:
        return ''
    else:
        return get_world_key(key)

def uget(command_params): # $uget(user|key)
    global user_key
    rgb.bump_rgb()
    load_user(magicint(command_params.split('|')[0]))
    return user_key[dancemagicint(command_params.split('|')[1])]

def pget(command_params): # $pget(key)
    rgb.bump_rgb()
    global player_id, user_key
    load_user(player_id)
    return user_key[dancemagicint(command_params)]

def greater_than(command_params): # $>(value|value)
    rgb.bump_rgb()
    if magicint(command_params.split('|')[0]) > magicint(command_params.split('|')[1]):
        return '0'
    else:
        return '1'

def less_than(command_params):
    rgb.bump_rgb()
    if magicint(command_params.split('|')[0]) < magicint(command_params.split('|')[1]):
        return '0'
    else:
        return '1'

def equal(command_params):
    rgb.bump_rgb()
    if magicint(command_params.split('|')[0]) == magicint(command_params.split('|')[1]):
        return '0'
    else:
        return '1'

def not_equal(command_params):
    rgb.bump_rgb()
    if magicint(command_params.split('|')[0]) != magicint(command_params.split('|')[1]):
        return '0'
    else:
        return '1'

def add(command_params):
    rgb.bump_rgb()
    return str(magicint(command_params.split('|')[0]) + magicint(command_params.split('|')[1]))

def subtract(command_params):
    rgb.bump_rgb()
    return str(magicint(command_params.split('|')[0]) - magicint(command_params.split('|')[1]))

def limit(command_params):
    rgb.bump_rgb()
    if magicint(command_params.split('|')[0]) < magicint(command_params.split('|')[1]):
        return command_params.split('|')[1]
    if magicint(command_params.split('|')[0]) > magicint(command_params.split('|')[2]):
        return command_params.split('|')[2]
    return command_params.split('|')[0]

def b6tob10(command_params): #$b6tob10(value)
    rgb.bump_rgb()
    return str(moremagicint(command_params))

def b10tob6(command_params): #$b10tob6(value)
    rgb.bump_rgb()
    return str(convert_base_10_to_base_6(magicint(command_params)))

def button(command_params): # $button(action)
    rgb.bump_rgb()
    global button_next
    if buttons.add(command_params):
        return '[' + ['r', 'y', 'g', 't', 'b', 'v'][buttons.button_next - 1] + ']'
    else:
        return ''

##
# Conversion Functions
##

def safe_cast(val, to_type, default=None):
    rgb.bump_rgb()
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default

def magicint(danger): #can pass this a string number, or an .address and it will return an int no matter what (returns 0 if there was a problem)
    rgb.bump_rgb()
    print('magicint(' + danger + ')')
    if danger[0:1] == '.':
        jump_address = 0
        for i in range(3, world_key_len):
            if get_world_key(i) == danger:
                print('detected a .namedoffset: ' + danger + ' returning: ' + str(i + 1))
                jump_address = i + 1
                return jump_address

    return safe_cast(danger, int, 0)

def dancemagicint(danger): #can pass this a string number, or an !address and it will return an int no matter what (returns 0 if there was a problem)
    rgb.bump_rgb()
    global user_key
    if danger[0:1] == '!':
        jump_address = 0
        for i in range(3, len(user_key)):
            if user_key[i] == danger:
                print('detected a !namedoffset: ' + danger + ' returning: ' + str(i + 1))
                jump_address = i + 1
                return jump_address

    return safe_cast(danger, int, 0)

def moremagicint(danger): #can pass this a string base6 number and it will return an int no matter what (returns 0 if there was an issue)
    rgb.bump_rgb()
    safe = ''
    for i in range(0, len(danger)):
        if danger[i:i+1] in ['0', '1', '2', '3', '4', '5']:
            safe = safe + danger[i:i+1]
    print('safe after: ' + safe)
    if safe == '':
        safe = '0'
    return int(safe, 6)

def convert_base_10_to_base_6(base_10): # place values 216 36 6 1
    rgb.bump_rgb()
    safe_base_10 = safe_cast(base_10, int, 0)
    digit_3 = int(safe_base_10 / 216)
    safe_base_10 = safe_base_10 - (digit_3 * 216)
    digit_2 = int(safe_base_10 / 36)
    safe_base_10 = safe_base_10 - (digit_2 * 36)
    digit_1 = int(safe_base_10 / 6)
    safe_base_10 = safe_base_10 - (digit_1 * 6)
    digit_0 = safe_base_10
    return str(digit_3) + str(digit_2) + str(digit_1) + str(digit_0)

##
# File System Functions
##

def load_world(file_name): # really just stores how many lines into world_key_len
    rgb.bump_rgb()
    global world_key_file, world_key_len
    world_key_file = file_name
    world_key_len = 0
    f = open(world_key_file, 'r')
    reading = True
    line_read = ''
    while(reading):
        line_read = f.readline()
        if line_read == '': # EOF
            reading = False
        else:
            world_key_len = world_key_len + 1
    f.close()

def get_world_key(key_index): #if key is in cache return cached, if not return eeprom
    rgb.bump_rgb()
    global world_key_len, cache_lookup, cache_key, world_key_file
    if world_key_file == '':
        return '0'
    if key_index <= world_key_len:
        in_cache = False
        for i in range(0, len(cache_lookup)):
            if cache_lookup[i] == key_index:
                print('gwk#' + str(key_index) + ' cl#' + str(i) + ' ck: ' + cache_key[i])
                return cache_key[i]
                in_cache = True
                break
        if in_cache == False:
            f = open(world_key_file, "r")
            line_read = ""
            for i in range(0, key_index + 1):
                line_read = f.readline()
            f.close()
            print('gwk#' + str(key_index) + ' wk: ' + line_read)
            return line_read.rstrip('\n')

def set_world_key(key_index, key_value): #if no cache entry for this key, add one and store the value in cache
    rgb.bump_rgb()
    global world_key_len, cache_lookup, cache_key
    if key_index <= world_key_len:
        in_cache = False
        for i in range(0, len(cache_lookup)):
            if cache_lookup[i] == key_index:
                cache_key[i] = key_value
                print('swk#' + str(key_index) + ' cl#' + str(i) + ' ck: ' + cache_key[i])
                in_cache = True
                break
        if in_cache == False:
            cache_lookup.append(key_index)
            cache_key.append(key_value)
            print('swk#' + str(key_index) + ' cl+ cl#' + str(len(cache_lookup) - 1) + ' v: ' + str(cache_lookup[len(cache_lookup) - 1]))
            print('swk#' + str(key_index) + ' ck+ ck#' + str(len(cache_key) - 1) + ' v: ' + cache_key[len(cache_key) - 1])

def load_user(id):
    global loaded_id
    rgb.bump_rgb()

    #if this id does not exist, create it procedurally
    real_or_imaginary(id)

    #check to see if this is already the loaded user
    if id == loaded_id:
        return

    loaded_id = id
    unpack_user_key_to_disk(id)

    file = 'temp/loaded.tcikeys'
    f = open(file, "r")
    reading = True
    line_read = ""
    global user_key
    user_key = [str(id)]
    while(reading):
        line_read = f.readline()
        if line_read == "": #EOF
            reading = False
        else:
            user_key.append(line_read.rstrip('\n'))
    f.close()
    return

def screen_to_temp():
    f2 = open('temp/loaded.tcipage', 'wb+')
    mode0_header = [0x54, 0x59, 0x4d, 0x4b, 0x52, 0x53, 0x43, 0x49, 0x49, 0x01, 0x1e, 0x20, 0x00, 0x00, 0x00, 0x00]
    # write the tymkrscii page file header section to the file
    for i in range(0, 16):
        f2.write(mode0_header[i].to_bytes(1, 'big'))
    # write the data section to the file
    for i in range(0, 960):
        f2.write(screen.screen_buffer[i].to_bytes(1, 'big'))
    f2.close()

def unpack_user_logo_to_disk(id):
    rgb.bump_rgb()
    print('unpack_user_logo_to_disk id: ' + str(id))
    real_or_imaginary(id)
    f1 = open('users/' + str(id) + '.tciuser', 'rb')
    f2 = open('temp/loaded.tcipage', 'wb+')
    f1.seek(16)
    for i in range(0, 976):
        user_logo = f1.read(1)
        if user_logo != b'':
            f2.write(user_logo)
    f1.close()
    f2.close()

def unpack_user_key_to_disk(id):
    rgb.bump_rgb()
    print('unpack_user_key_to_disk id: ' + str(id))
    real_or_imaginary(id)
    f1 = open('users/' + str(id) + '.tciuser', 'rb')
    f2 = open('temp/loaded.tcikeys', 'wb+')
    f1.seek(992)
    for i in range(0, 2048):
        user_keys = f1.read(1)
        if user_keys != b'' and user_keys != b'\x00':
            f2.write(user_keys)
    f1.close()
    f2.close()

def unpack_user_site_to_disk(id):
    rgb.bump_rgb()
    print('unpack_user_site_to_disk id: ' + str(id))
    real_or_imaginary(id)
    f1 = open('users/' + str(id) + '.tciuser', 'rb')
    f2 = open('temp/loaded.tcisite', 'wb+')
    f1.seek(3040)
    for i in range(0, 5152):
        user_site = f1.read(1)
        if user_site != b'':
            f2.write(user_site)
    f1.close()
    f2.close()

def repack_user_file_to_disk(id):
    global user_key
    rgb.bump_rgb()
    unpack_user_logo_to_disk(id)
    unpack_user_site_to_disk(id)

    # create fresh .tcikeys from memory into temp
    f = open('temp/loaded.tcikeys', 'wb+')
    for i in range(1, len(user_key)):
        f.write(bytes(user_key[i], 'utf-8'))
        f.write(bytes('\n', 'utf-8'))
    f.close()

    pack_user_file(id)

def pack_user_file(id):
    rgb.bump_rgb()

    size_f2 = open('temp/loaded.tcipage', 'rb')
    size_f2.seek(0, 2)
    len_user_logo = size_f2.tell()
    size_f2.close()

    size_f3 = open('temp/loaded.tcikeys', 'rb')
    size_f3.seek(0, 2)
    len_user_keys = size_f3.tell()
    size_f3.close()

    size_f4 = open('temp/loaded.tcisite', 'rb')
    size_f4.seek(0, 2)
    len_user_site = size_f4.tell()
    size_f3.close()

    print('pack_user_file: len_user_logo:' + str(len_user_logo) + ' len_user_keys:' + str(len_user_keys) + ' len_user_site:' + str(len_user_site))

    if len_user_logo == 976 and len_user_keys <= 2048 and len_user_site <= 5152:

        print("pack_user_file: temp files pass checks, writing tciuser")

        tciuser_header = [0x54, 0x59, 0x4d, 0x4b, 0x52, 0x53, 0x43, 0x49, 0x49, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

        f1 = open('users/' + str(id) + '.tciuser', 'wb+')

        #write tciuser header
        for i in range(0, 16):
            f1.write(tciuser_header[i].to_bytes(1, 'big'))

        #write a 0x00 byte at the end of the file to set the file size to 8KiB
        f1.seek((1024 * 8) - 1)
        EoT = [0x00]
        f1.write(EoT[0].to_bytes(1, 'big'))

        #copy the tcipage page into the tciuser file one byte at a time (to save ram)
        f2 = open('temp/loaded.tcipage', 'rb')
        f1.seek(16)
        writing = True
        rgb.bump_rgb()
        while writing:
            user_logo = f2.read(1)
            if user_logo == b'':
                writing = False
            else:
                f1.write(user_logo)
        f2.close()

        #copy the tcikeys page into the tciuser file one byte at a time (to save ram)
        f3 = open('temp/loaded.tcikeys', 'rb')
        f1.seek(992)
        writing = True
        rgb.bump_rgb()
        while writing:
            user_keys = f3.read(1)
            if user_keys == b'':
                writing = False
            else:
                f1.write(user_keys)
        f3.close()

        #copy the tcisite page into the tciuser file one byte at a time (to save ram)
        f4 = open('temp/loaded.tcisite', 'rb')
        f1.seek(3040)
        writing = True
        rgb.bump_rgb()
        while writing:
            user_site = f4.read(1)
            if user_site == b'':
                writing = False
            else:
                f1.write(user_site)
        f4.close()
        f1.close()

        if id == player_id:
            network.increment_local_version()
            print('adventure: repack_user_file new player file version: ' + str(network.get_version(player_id)))

    else:
        print('user file pack face plant')
        if len(user_logo) != 976:
            print('user_logo wrong size: ' + str(len(user_logo)))
        if len(user_keys) > 2048:
            print('user_keys too long: ' + str(len(user_keys)))
        if len(user_site) > 5152:
            print('user_site too long: ' + str(len(user_site)))

def real_or_imaginary(id):

    #check if users/ file exists
    user_check = False
    try:
        f = open('users/' + str(id) + '.tciuser', 'rb')
        f.close()
        user_check = True
        print('adventure: load_user: user file found')
    except OSError:  # open failed
        print('adventure: load_user: user file not found')

    #check what version we have for this user
    version = network.get_version(id)

    #if we don't have the file or if the version is 0, make a prodecurally generated user
    if user_check == False or version == 0:
        print('adventure: user# ' + str(id) + ' not found, making an imaginary friend')
        make_user(id)

def make_user(working_id):

    #copy default.tcikey to temp/
    network.copy_default_user_to_temp()

    #load the temp/ user
    file = 'temp/loaded.tcikeys'
    f1 = open(file, "r")
    reading = True
    line_read = ""
    global user_key
    user_key = [str(id)]
    while(reading):
        line_read = f1.readline()
        if line_read == "": #EOF
            reading = False
        else:
            user_key.append(line_read.rstrip('\n'))
    f1.close()

    #generate a random name
    random_name = logogen.name_generator()

    #apply that name to the correct user key
    user_key[2] = random_name

    # create fresh .tcikeys from memory into temp
    f2 = open('temp/loaded.tcikeys', 'wb+')
    for i in range(1, len(user_key)):
        f2.write(bytes(user_key[i], 'utf-8'))
        f2.write(bytes('\n', 'utf-8'))
    f2.close()

    #copy the default.tcisite to temp/
    network.copy_default_site_to_temp()

    #copy the defaul.tcipage to temp/
    network.copy_default_logo_to_temp()

    #pack user file
    pack_user_file(working_id)

    #set version to 1
    network.set_version(working_id, 1)
