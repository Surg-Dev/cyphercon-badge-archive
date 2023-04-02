# Copyright (C) 2023 tymkrs
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name of tymkrs shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization from tymkrs.

import os
import ir
import counters
import rgb
import mode
import adventure

network_mode = 0
RPC = 0 # Rx Position Counter
SQC = 0 # Still Quiet Counter
TRY = 0 # cache entry to try

wait_for_quiet = False
wfq_chunk_index = 0
wfq_rolling_chunk_index = 0
wfq_remote_index = 0

def initialize():
    global RPC, SQC, TRY
    RPC = counters.start(8208) # set up for size of ir.rx_buffer
    SQC = counters.start(180) # how many no new RX network_clocks until 'quiet'
    TRY = counters.start(699)
    ir.initialize()

def network_clock():
    global wait_for_quiet, wfq_chunk_index, wfq_remote_index, wfq_rolling_chunk_index
    if rx(): # see if stuff was put in the rx_buffer
        counters.reset(SQC)
        if check_syncword(): # there is a sync word, so we may have a packet
            if check_checksum(): # checksum matches
                handle(get_from_index(), get_remote_index(), get_chunk_index(), get_remote_version(), get_chunk())
    else:
        if counters.count(SQC): # quiet counter tripped
            if wait_for_quiet: # something is waiting to be sent
                tx_wfq() # send it
                wait_for_quiet = False
            else: # nothing is waiting, so add something
                if wfq_remote_index != adventure.player_id: # last time was not my user file
                    # so add a chunk of my user file
                    print('network: clock: last broadcast was not my id')
                    wfq_remote_index = adventure.player_id
                    wfq_rolling_chunk_index = wfq_rolling_chunk_index + 1
                    if wfq_rolling_chunk_index >= 128:
                        wfq_rolling_chunk_index = 0
                    wfq_chunk_index = wfq_rolling_chunk_index
                    wait_for_quiet = True
                elif wfq_remote_index == adventure.player_id: # last time was my user file
                    # so add a chunk from something else
                    # determine first needed cache chunk
                    # this should be improved but I ran out of time
                    # if you improve it, share it and let me know! -whixr 2022
                    print('network: clock: last broadcast was my id')
                    winner_index = first_incomplete()
                    print('last was self adding: ' + str(winner_index))
                    if winner_index != adventure.player_id:
                        # global set up to TX my cache version of this chunk
                        wfq_remote_index = winner_index
                        wfq_chunk_index = first_lesser_version_chunk(winner_index)
                        # set wait for quiet semaphore
                        wait_for_quiet = True
                        print('chunk: ' + str(wfq_chunk_index))
                    else:
                        wfq_remote_index = adventure.player_id
                        wfq_rolling_chunk_index = wfq_rolling_chunk_index + 1
                        if wfq_rolling_chunk_index >= 128:
                            wfq_rolling_chunk_index = 0
                        wfq_chunk_index = wfq_rolling_chunk_index
                        wait_for_quiet = True

##
#   RX
##

def rx():
    new_data = False
    start = counters.counter[RPC]
    while ir.uart0.any() > 0:
        counters.apply_delta(RPC, 1)
        ir.rx_buffer[counters.counter[RPC]] = int.from_bytes(ir.uart0.read(1), 'big')
        new_data = True
    if new_data:
        print('network: new_data: ', end = '')
        start = start + 1
        if start >= 8208:
            start = 0
        while True:
            print(str(ir.rx_buffer[start]), end = ' ')
            if start == counters.counter[RPC]:
                break
            else:
                start = start + 1
                if start >= 8208:
                    start = 0
        print('')
    return new_data

def handle(from_index, remote_index, chunk_index, remote_version, chunk_data):
    global wait_for_quiet, wfq_chunk_index, wfq_remote_index

    if remote_index == adventure.player_id:
        print('network: handle: chunk is from my own user file so ignoring')
        pass
    else:
        if remote_version > read_cache_map(remote_index, chunk_index):
            print('network: handle: newer than local, ri: ' + str(remote_index) + ' ci: ' + str(chunk_index) + ' rv: ' + str(remote_version))
            write_chunk_to_cache(remote_index, chunk_index, chunk_data)
            write_cache_map(remote_index, chunk_index, remote_version)
            if test_completed_cache_map(remote_index) and remote_index != adventure.player_id: # have whole file
                copy_cache_to_users(remote_index)
                set_version(remote_index, remote_version)
        elif remote_version < read_cache_map(remote_index, chunk_index):
            print('network: handle: stale vs cache: sending back newer version of ri: ' + str(remote_index) + ' ci: ' + str(chunk_index) + ' rv: ' + str(remote_version))
            wfq_chunk_index = chunk_index
            wfq_remote_index = remote_index
            wait_for_quiet = True

##
#   TX
##

def tx_wfq():
    print('network: tx_wfq sending wfq_ci: ' + str() + ' wfq_ri: ' + str())
    clear_tx_buffer()
    if wfq_remote_index == adventure.player_id:
        chunk_index = wfq_chunk_index
        from_index = adventure.player_id
        remote_version = get_version(adventure.player_id)
        remote_index = adventure.player_id
        print('network: tx_wfq ci: ' + str(chunk_index) + ' fi: ' + str(from_index) + ' rv: ' + str(remote_version) + ' ri: ' + str(remote_index))
        write_chunk_packet(chunk_index, from_index, remote_version, remote_index)
    else:
        write_chunk_packet(wfq_chunk_index, adventure.player_id, read_cache_map(wfq_remote_index, wfq_chunk_index), wfq_remote_index)
    ir.tx()
    print('network: tx_wfq sent')

##
#   TX Packet Tools
##

def write_chunk_packet(chunk_index, from_index, remote_version, remote_index):

    print('network: write_tx_header')
    print('network: write_tx_header chunk_index: ' + str(chunk_index))
    print('network: write_tx_header from_index: ' + str(from_index))
    print('network: write_tx_header remote_version: ' + str(remote_version))
    print('network: write_tx_header remote_index: ' + str(remote_index))

    # syncword
    ir.tx_buffer[0:4] = bytearray([22, 22, 22, 22])

    # type
    ir.tx_buffer[7:8] = chunk_index.to_bytes(1, 'big')

    # from_index
    ir.tx_buffer[8:10] = from_index.to_bytes(2, 'big')

    # remote_version
    ir.tx_buffer[10:14] = remote_version.to_bytes(4, 'big')

    # remote_index
    ir.tx_buffer[14:16] = remote_index.to_bytes(2, 'big')

    # user file
    chunk = load_chunk(remote_index, chunk_index)
    for i in range(0, 64):
        ir.tx_buffer[16 + i] = chunk[i]

    # checksum
    ir.tx_buffer[4:7] = tally_tx_checksum().to_bytes(3, 'big')

def load_chunk(remote_index, chunk_index):
    chunk = bytearray(range(64))
    if remote_index == adventure.player_id:
        f = open('users/' + str(remote_index) + '.tciuser', 'rb')
    else:
        create_if_missing(remote_index)
        f = open('cache/' + str(remote_index) + '.tciuser', 'rb')
    f.seek(chunk_index * 64)
    for i in range(0, 64):
        chunk[63 - i] = int.from_bytes(f.read(1), 'big')
    f.close()
    print('network: chunk_from_live: ri: ' + str(remote_index) + ' ci: ' + str(chunk_index) + ' c: ', end = '')
    print(chunk)
    return chunk

def tally_tx_checksum():
    tally = 0
    for i in range(7, 80):
        tally = tally + ir.tx_buffer[i]
    print('network: tally_tx_checksum: ' + str(tally))
    return tally

def clear_tx_buffer():
    for i in range(0, 80):
        ir.tx_buffer[i] = 0
    print('network: clear_tx_buffer')

##
#   RX Packet Tools
##

SYNCWORD = -3           # -3 -2 -1 -0
CHECKSUM = -6           # -6 -5 -4
CHUNK_INDEX = -7        # -7
FROM_INDEX = -9         # -9 -8
REMOTE_VERSION = -13    # -13 -12 -11 -10
REMOTE_INDEX = -15      # -15 -14
CHUNK = -79             # -79 .. -16

def peek(delta):
    return ir.rx_buffer[counters.calc_relative_position(RPC, delta)]

def check_syncword():
    passed = True
    for i in range(0, 4):
        if peek(SYNCWORD + i) != 22: passed = False
    #print('network: check_syncword: ', end = '') # spammy
    #print(passed) # spammy
    return passed

def check_checksum():
    passed = True
    if get_checksum() != tally_checksum(): passed = False
    print('network: check_checksum: ', end = '')
    print(passed)
    return passed

def get_checksum():
    checksum = 0
    for i in range(0, 3):
        checksum = checksum + (peek(CHECKSUM + i) * (256 ** i))
    print('network: get_checksum: ' + str(checksum))
    return checksum

def tally_checksum():
    tally = 0
    for i in range(-7, -80, -1):
        tally = tally + peek(i)
    print('network: tally_checksum: ' + str(tally))
    return tally

def get_chunk_index():
    chunk_index = peek(CHUNK_INDEX)
    print('network: get_chunk_index chunk_index: ' + str(chunk_index))
    return chunk_index

def get_from_index():
    checksum = 0
    for i in range(0, 2):
        checksum = checksum + (peek(FROM_INDEX + i) * (256 ** i))
    print('network: get_from_index: ' + str(checksum))
    return checksum

def get_remote_version():
    checksum = 0
    for i in range(0, 4):
        checksum = checksum + (peek(REMOTE_VERSION + i) * (256 ** i))
    print('network: get_remote_version: ' + str(checksum))
    return checksum

def get_remote_index():
    checksum = 0
    for i in range(0, 2):
        checksum = checksum + (peek(REMOTE_INDEX + i) * (256 ** i))
    print('network: get_remote_index: ' + str(checksum))
    return checksum

def get_chunk():
    chunk = bytearray(range(64))
    for i in range(0, 64):
        chunk[i] = peek(CHUNK + i)
    print('network: get_chunk: ', end = '')
    print(chunk)
    return chunk

##
#   cache map file
##

def write_cache_map(remote_index, chunk_index, cache_version):
    f = open('cache_map', 'rb+')
    f.seek( (remote_index * 512) + (chunk_index * 4) )
    f.write(cache_version.to_bytes(4, 'big'))
    f.close()

def read_cache_map(remote_index, chunk_index):
    f = open('cache_map', 'rb')
    f.seek( (remote_index * 512) + (chunk_index * 4) )
    return int.from_bytes(f.read(4), 'big')

def test_completed_cache_map(remote_index):
    completed = True
    version = read_cache_map(remote_index, 0)
    for i in range(1, 128):
        if read_cache_map(remote_index, i) != version:
            completed = False
            break
    return completed

def first_incomplete():
    counters.count(TRY)
    print('network: first_incomplete: trying index: ' + str(counters.counter[TRY]))
    rgb.bump_rgb()
    i = counters.counter[TRY]
    if test_completed_cache_map(i) == False:
        print('network: first_incomplete: found: ' + str(i))
        return i
    print('network: first_incomplete: not incomplete so: returning: self')
    return adventure.player_id

# this works but blocks the UI while running so trying above instead
# def first_incomplete():
#     for i in range(0, 700):
#         rgb.rgb_bump()
#         if test_completed_cache_map(i) == False:
#             print('first_incomplete: ' + str(i))
#             return i
#     print('first_incomplete: none found so self')
#     return adventure.player_id

def find_latest(remote_index):
    winner = 0
    highest_version = 0
    for i in range(0, 128):
        version = read_cache_map(remote_index, i)
        if version > highest_version:
            highest_version = version
            winner = i
    return winner

def first_lesser_version_chunk(remote_index):
    latest = find_latest(remote_index)
    for i in range(0, 128):
        if read_cache_map(remote_index, i) != latest:
            return i

def create_cache_map_if_missing():
    #check if cache_map file exists
    user_check = False
    try:
        f1 = open('cache_map', 'rb')
        f1.close()
        user_check = True
        print('network: create_cache_map_if_missing: file found')
    except OSError:  # open failed
        pass
        print('network: create_cache_map_if_missing: file not found')

    if user_check == False:
        print('network: create_cache_map_if_missing: generating empty cache_map file')
        create_empty_cache_map()

def create_empty_cache_map():
    f = open('cache_map', 'wb+')
    for u in range(0, 700):
        for c in range(0, 128):
            version = 0
            f.write(version.to_bytes(4, 'big'))
    f.close()

##
#   user cache files
##

def copy_cache_to_users(remote_index):
    f1 = open('cache/' + str(remote_index) + '.tciuser', 'rb')
    f2 = open('users/' + str(remote_index) + '.tciuser', 'wb+')
    while True:
        read_byte = f1.read(1)
        if read_byte == b'':
            break
        else:
            f2.write(read_byte)
    f1.close()
    f2.close()

def write_chunk_to_cache(remote_index, chunk_index, chunk_data):
    if remote_index != adventure.player_id: # Don't stow your own crap, n00b
        create_if_missing(remote_index)
        f = open('cache/' + str(remote_index) + '.tciuser', 'rb+')
        f.seek(chunk_index * 64)
        f.write(bytes(chunk_data))
        f.close()

def create_if_missing(remote_index):

    #check if cache/ file exists
    user_check = False
    try:
        f1 = open('cache/' + str(remote_index) + '.tciuser', 'rb')
        f1.close()
        user_check = True
        print('network: create_if_missing: user file found')
    except OSError:  # open failed
        pass
        print('network: create_if_missing: user file not found')

    if user_check == False:
        print('network: create_if_missing: creating cache/' + str(remote_index) + '.tciuser file')
        f2 = open('defaults/empty.tciuser', 'rb')
        f3 = open('cache/' + str(remote_index) + '.tciuser', 'wb+')
        while True:
            read_byte = f2.read(1)
            if read_byte == b'':
                break
            else:
                f3.write(read_byte)
        f2.close()
        f3.close()

def create_empty_user_if_missing():
    #check if cache_map file exists
    file_check = False
    try:
        f1 = open('defaults/empty.tciuser', 'rb')
        f1.close()
        file_check = True
        print('network: create_empty_user_if_missing: file found')
    except OSError:  # open failed
        pass
        print('network: create_empty_user_if_missing: file not found')

    if file_check == False:
        print('network: create_empty_user_if_missing: generating empty user file')
        create_empty_user()

def create_empty_user():
    f = open('defaults/empty.tciuser', 'wb+')
    for i in range(0, 8192):
        f.write(bytearray([0]))
    f.close()

##
#   versions file
##

def get_version(index):
    f = open('versions', 'rb')
    f.seek(index * 4)
    version = int.from_bytes(f.read(4), 'big')
    f.close()
    print('network: get_version index: ' + str(index) + ' version: ' + str(version))
    return version

def set_version(index, value):
    print('network: set_version index: ' + str(index) + ' value: ' + str(value))
    f = open('versions', 'rb+')
    f.seek(index * 4)
    f.write(value.to_bytes(4, 'big'))
    f.close()

def increment_local_version():
    current_version = get_version(adventure.player_id)
    new_version = current_version + 1 #
    if current_version <= 1 or current_version >= 4294967295:
        new_version = 2
    set_version(adventure.player_id, new_version)

def create_versions_if_missing():
    #check if cache_map file exists
    file_check = False
    try:
        f1 = open('versions', 'rb')
        f1.close()
        file_check = True
        print('network: create_versions_if_missing: file found')
    except OSError:  # open failed
        pass
        print('network: create_versions_if_missing: file not found')

    if file_check == False:
        print('network: create_versions_if_missing: generating empty versions file')
        create_empty_versions()

def create_empty_versions():
    f = open('versions', 'wb+')
    for i in range(0, 700):
        f.write(bytearray([0, 0, 0, 0]))
    f.close()

##
#   upload custom site or logo from eeprom to local user's user file
##

def apply_updates_from_eeprom():

    site_check = False
    try:
        f = open('custom.tcisite', 'rb')
        f.close()
        site_check = True
        print('network: apply_updates_from_eeprom: found custom.tcisite in /')
    except OSError:  # open failed
        pass
        print('network: apply_updates_from_eeprom: no custom.tcisite in /')

    logo_check = False
    try:
        f = open('custom.tcipage', 'rb')
        f.close()
        logo_check = True
        print('network: apply_updates_from_eeprom: found custom.tcipage logo in /')
    except OSError:  # open failed
        pass
        print('network: apply_updates_from_eeprom: no custom.tcipage logo in /')

    if site_check or logo_check:

        adventure.load_user(adventure.player_id)

        if site_check:
            copy_custom_site_to_temp()
            os.rename('custom.tcisite', 'custom.tcisite_backup')
        else:
            adventure.unpack_user_site_to_disk(adventure.player_id)

        if logo_check:
            copy_custom_logo_to_temp()
            os.rename('custom.tcipage', 'custom.tcipage_backup')
        else:
            adventure.unpack_user_logo_to_disk(adventure.player_id)

        adventure.pack_user_file(adventure.player_id)

def copy_custom_site_to_temp():
    f1 = open('custom.tcisite', 'rb')
    f2 = open('temp/loaded.tcisite', 'wb+')
    while True:
        read_byte = f1.read(1)
        if read_byte == b'':
            break
        else:
            f2.write(read_byte)
    f1.close()
    f2.close()

def copy_custom_logo_to_temp():
    f1 = open('custom.tcipage', 'rb')
    f2 = open('temp/loaded.tcipage', 'wb+')
    while True:
        read_byte = f1.read(1)
        if read_byte == b'':
            break
        else:
            f2.write(read_byte)
    f1.close()
    f2.close()

def copy_default_site_to_temp():
    f1 = open('defaults/default.tcisite', 'rb')
    f2 = open('temp/loaded.tcisite', 'wb+')
    while True:
        read_byte = f1.read(1)
        if read_byte == b'':
            break
        else:
            f2.write(read_byte)
    f1.close()
    f2.close()

def copy_default_user_to_temp():
    f1 = open('defaults/default.tcikeys', 'rb')
    f2 = open('temp/loaded.tcikeys', 'wb+')
    while True:
        read_byte = f1.read(1)
        if read_byte == b'':
            break
        else:
            f2.write(read_byte)
    f1.close()
    f2.close()

def copy_default_logo_to_temp():
    f1 = open('defaults/default.tcipage', 'rb')
    f2 = open('temp/loaded.tcipage', 'wb+')
    while True:
        read_byte = f1.read(1)
        if read_byte == b'':
            break
        else:
            f2.write(read_byte)
    f1.close()
    f2.close()

##
#   factory resets
##

def player_reset():
    remove_users_file(adventure.player_id)
    adventure.make_user(adventure.player_id)

#          ---------
#         /         \
#        /    REST   \
#       /      IN     \
#      /     PEACE     \
#     /                 \
#     |      whixr      |
#     |   killed by a   |
#     |   micropython   |
#     |                 |
#     |      2023       |
#     |    *  *  *      | *
#__)/\|\_//(\/(/\)/\//\/|_)__________
#
# Goodbye whixr the tymkr...
#
# You died in The Dungeons of Cyphercon on badge level 6 with 0 points.
# You were level overflow with a maximum of overflow hit points when you died.
# You were poisoned by a micropython, while wielding a keyboard,
# while fainted from lack of sunlight.
#
# You were just fast enough, you were polymorphic, you are done.

# The last function, after 94 consecutive 17 hour work days
# -whixr 3/17/2023
def factory_reset():
    for i in range(0, 700):
        remove_users_file(i)
        remove_cache_file(i)
    create_empty_versions()
    create_empty_cache_map()
    adventure.make_user(adventure.player_id)

def remove_users_file(index):
    try:
        os.remove('users/' + str(index) + '.tciuser')
        print('network: remove_users_file: removed users/' + str(index) + '.tciuser')
    except OSError:  # open failed
        print('network: remove_users_file: file did not exist')

def remove_cache_file(index):
    try:
        os.remove('cache/' + str(index) + '.tciuser')
        print('network: remove_cache_file: removed cache/' + str(index) + '.tciuser')
    except OSError:  # open failed
        print('network: remove_cache_file: file did not exist')
