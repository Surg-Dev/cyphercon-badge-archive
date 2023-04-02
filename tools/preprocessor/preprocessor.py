# Copyright (C) 2023 tymkrs
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name of tymkrs shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization from tymkrs.

import time

from random import *

from tkinter import *
from tkinter import ttk
from tkinter import filedialog

###
#   globals
###

world_key = []
address_list = []
address_line = []

user_key = []
user_address_list = []
user_address_line = []

##
#   loading source code
##

def load_world():
    global world_key
    file = filedialog.askopenfilename(title='Load File', filetypes=[("Tymkrs Character Interchange World", "*.tciworld")])
    if file:
        f = open(file, "r")
        reading = True
        line_read = ""
        world_key = []
        while(reading):
            line_read = f.readline()
            if line_read == "": # EOF
                reading = False
            else:
                world_key.append(line_read.rstrip('\n'))
        f.close()
    else:
        pass #canceled or whatever

def load_user():
    global user_key
    file = filedialog.askopenfilename(title='Load File', filetypes=[("Tymkrs Character Interchange World", "*.tcikeys")])
    if file:
        f = open(file, "r")
        reading = True
        line_read = ""
        user_key = ['0']
        while(reading):
            line_read = f.readline()
            if line_read == "": # EOF
                reading = False
            else:
                user_key.append(line_read.rstrip('\n'))
        f.close()
    else:
        pass #canceled or whatever

##
#   .addresses
##

def collect_addresses():
    global world_key, address_list
    for i in range(0, len(world_key)):
        if world_key[i][0:1] == '.':
            address_list.append(world_key[i])
            address_line.append(str(i + 1))

def replace_addresses():
    global address_list

    while True:
        fail = False

        for address_list_index in range(0, len(address_list)):
            if address_list[address_list_index][0:1] == '.':
                if check_address(address_list_index):
                    replace_address_in_world_keys(address_list_index)
                    address_list[address_list_index] = '#done'
                else:
                    fail = True
        if fail == False:
            break

def check_address(address_list_index):
    global address_list
    safe = True
    for ai in range(0, len(address_list)):
        if ai != address_list_index and address_list[ai][0:1] == '.':
            if address_list[ai].find(address_list[address_list_index]) != -1:
                safe = False
                print('fail, ali:' + str(address_list_index) + ' ai:' + str(ai) + ' al[ai]|' + address_list[ai] + '| al[ali]|' + address_list[address_list_index] + '|')
    return safe

def replace_address_in_world_keys(address_list_index):
    global world_key
    for i in range(0, len(world_key)):
        if world_key[i][0:1] != '.':
            world_key[i] = world_key[i].replace(address_list[address_list_index], address_line[address_list_index])

##
#   !addresses
##

def user_collect_addresses():
    global user_key, user_address_list
    for i in range(0, len(user_key)):
        if user_key[i][0:1] == '!':
            user_address_list.append(user_key[i])
            user_address_line.append(str(i + 1))

def user_replace_addresses():
    global user_address_list

    while True:
        fail = False

        for user_address_list_index in range(0, len(user_address_list)):
            if user_address_list[user_address_list_index][0:1] == '!':
                if user_check_address(user_address_list_index):
                    user_replace_address_in_world_keys(user_address_list_index)
                    user_address_list[user_address_list_index] = '#done'
                else:
                    fail = True
        if fail == False:
            break

def user_check_address(user_address_list_index):
    global user_address_list
    safe = True
    for ai in range(0, len(user_address_list)):
        if ai != user_address_list_index and user_address_list[ai][0:1] == '!':
            if user_address_list[ai].find(user_address_list[user_address_list_index]) != -1:
                safe = False
                print('fail, ali:' + str(user_address_list_index) + ' ai:' + str(ai) + ' al[ai]|' + user_address_list[ai] + '| al[ali]|' + user_address_list[user_address_list_index] + '|')
    return safe

def user_replace_address_in_world_keys(user_address_list_index):
    global world_key
    for i in range(0, len(world_key)):
        if world_key[i][0:1] != '!':
            world_key[i] = world_key[i].replace(user_address_list[user_address_list_index], user_address_line[user_address_list_index])

##
#   escapees {.} {!}
##

def escapees():
    global world_key
    for i in range(0, len(world_key)):
        world_key[i] = world_key[i].replace('{.}', '.')
        world_key[i] = world_key[i].replace('{!}', '!')

##
#   save processed source to disk
##

def save_world_static_file_to_disk():
    global world_key
    file = filedialog.asksaveasfilename(title='Save File', filetypes=[("Static World", "*.static")])

    f = open(file, 'wb+')
    for i in range(0, len(world_key)):
        f.write(bytes(world_key[i], 'utf-8'))
        f.write(bytes('\n', 'utf-8'))
    f.close()

##
#   main program
##

load_world()
load_user()

collect_addresses()
replace_addresses()

user_collect_addresses()
user_replace_addresses()

escapees()

save_world_static_file_to_disk()
