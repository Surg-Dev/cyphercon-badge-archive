# Copyright (C) 2023 tymkrs
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name of tymkrs shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization from tymkrs.

import screen
import buttons
import rgb
import mode
import buttons
import adventure

# url entry

branch = []

browser_address = 700
browser_page = 0
browser_exit = False

dividers = ['\x80', '\x81', '\x92', '\xd5', '\xf1', '\xc4', '\xfa', '\xfb', '\x8e', '\x01', '\x02', '\xc9', '\x07', '\xdf\xe0', '\x0b\x8f', '\x0e\x07', '\x09\x07', '\x07\x08', '\x0c\x0b\x0b\x0b', '\x07\x08\x09\x08']

def browser_click(user_input):
    global browser_page, browser_address
    if buttons.button_active[user_input] == True:
        print('browser: button action: ' + buttons.button_action[user_input])

        # change the browser to the indicated page
        if buttons.button_action[user_input] == 'next':
            #next page
            browser_page = browser_page + 1
        elif buttons.button_action[user_input] == 'top':
            browser_page = 0
        else:
            #next site
            browser_address = adventure.safe_cast(buttons.button_action[user_input], int, 700)
            browser_page = 0

        prerender_site()

        rgb.setRGBleds((0b000000000000, 0b111111111111, 0b100100100100, 0b110110110110, 0b010010010010, 0b011011011011, 0b001001001001, 0b101101101101)[mode.ui_color])

def url_entry_click(user_input):
    global browser_address
    if buttons.button_active[user_input] == True:
        print('browser: button action: ' + buttons.button_action[user_input])
        add_branch(user_input)
        rgb.setRGBleds((0b000000000000, 0b111111111111, 0b100100100100, 0b110110110110, 0b010010010010, 0b011011011011, 0b001001001001, 0b101101101101)[mode.ui_color])
    check = check_finish()
    if check == -1:
        #not done selecting url yet
        print_url_options()
    else:
        #done selecting url
        browser_address = check
        finish_browser_entry()

def finish_browser_entry():
    global browser_page
    rgb.bump_rgb()
    browser_page = 0
    prerender_site()

def prerender_site():
    global browser_page, browser_exit
    rgb.bump_rgb()
    if browser_address < 700 and browser_address >= 0:
        prerender_user_site(browser_address)
    elif browser_address >= 700:
        prerender_portal_site()
    # /temp/loaded.tcisite now exists
    # browser_page = 0
    update_browser()
    if browser_exit == True:
        browser_exit = False
    else:
        mode.ui_mode = mode.BROWSING_MODE

def prerender_user_site(user_id):
    # unpack the site into /temp/loaded.tcisite
    rgb.bump_rgb()
    adventure.unpack_user_site_to_disk(user_id)

def prerender_portal_site():
    global browser_address
    # copy the portal site into /temp/loaded.tcisite
    rgb.bump_rgb()

    try:
        f = open('portal/' + str(browser_address) + '.tcisite', 'rb')
        f.close()
    except OSError:  # open failed
        print('browser: portal site not found: ' + str(browser_address))
        rgb.bump_rgb()
        browser_address = 1294 #404 Page

    copy_portal_site_to_disk(browser_address)

def copy_portal_site_to_disk(site_id):
    rgb.bump_rgb()
    f1 = open('portal/' + str(site_id) + '.tcisite', 'rb')
    f2 = open('temp/loaded.tcisite', 'wb+')
    while(True):
        in_byte = f1.read(1)
        if in_byte == b'': #EOF
            f1.close()
            f2.close()
            break
        else:
            f2.write(in_byte)

def update_browser():
    update_page(browser_page)

def update_page(page_number):
    rgb.bump_rgb()
    screen.clear_screen()
    buttons.empty()
    buttons.add('next') #next page [r] at bottom of page
    page_line_offset = browser_page * 30
    for i in range(0, 30):
        if browser_exit == True:
            return
        working_key = load_site_line(page_line_offset + i)
        if working_key == '': #EOF
            buttons.button_action[0] = 'top'
            break
        else: # parse and add to screen_buffer
            working_key = working_key.rstrip('\n')
            working_key = parse_site(working_key)
            add_line_to_screen(page_number, i, working_key)
    add_url_to_screen(page_number)
    add_nav_to_screen()

    # invert the color for the top and bottom rows of the screen before flipping the page
    for i in range(0, 30):
        screen.morph[i] = 1
    for i in range(930, 960):
        screen.morph[i] = 1
    screen.flip_page()

def load_site_line(line_offset):
    rgb.bump_rgb()
    f1 = open('temp/loaded.tcisite', "r")
    read_line = ""
    if line_offset == 0:
        read_line = f1.readline(240)
    else:
        for i in range(0, line_offset):
            read_line = f1.readline(240)
            rgb.bump_rgb()
        read_line = f1.readline(240)
    return read_line

def add_line_to_screen(page_number, page_line_number, working_key):
    rgb.bump_rgb()
    buffer_start = (page_line_number + 1) * 30 # line 1 - line 30
    working_key = working_key[0:30]
    i = buffer_start
    for element in working_key:
        element_value = ord(element)
        if element_value > 255 or element_value < 0:
            element_value = 0
        screen.screen_buffer[i] = element_value
        i = i + 1

def add_url_to_screen(page_number):
    url = 'btp://cypher.' + str(browser_address) + '.con/?page=' + str(page_number)
    url = url[0:30]
    i = 0
    for element in url:
        element_value = ord(element)
        if element_value > 255 or element_value < 0:
            element_value = 0
        screen.screen_buffer[i] = element_value
        i = i + 1

def add_nav_to_screen():
    nav = '                 next page [r]'
    nav = nav[0:30]
    i = 930
    for element in nav:
        element_value = ord(element)
        if element_value > 255 or element_value < 0:
            element_value = 0
        screen.screen_buffer[i] = element_value
        i = i + 1

def parse_site(working_site):

    while(True):

        rgb.bump_rgb()

        # evaluate any environment variables
        adventure.load_user(adventure.player_id)
        working_site = adventure.parse_environment_variables(working_site)

        if browser_address >=0 and browser_address < 700:
            working_site = working_site.replace('{url}', str(browser_address))
        else:
            working_site = working_site.replace('nope', str(browser_address))

        # check to see if there are any commands remaining
        if adventure.check_command(working_site) == False:
            return working_site

        # check to see if there is a random command
        # if so, evaluate the random()
        if working_site.find('$random(') != -1:
            working_site = adventure.parse_random_command(working_site)
            continue

        # evaluate a remaining simple command()
        working_site = parse_site_simple_command(working_site)

def parse_site_simple_command(working_key):
    global browser_exit
    rgb.bump_rgb()

    command_close           = working_key.find(')')
    command_head            = working_key.rfind('$', 0, command_close)
    command_open            = working_key.find('(', command_head, command_close)
    command_params          = working_key[command_open + 1:command_close]
    command_type            = working_key[command_head + 1:command_open]
    command_whole           = working_key[command_head:command_close + 1]

    if command_type == 'warp':
        browser_exit = True
        working_key = working_key.replace(command_whole, '', 1)
        adventure.warp(command_params)
        return working_key

    if command_type == 'silent_warp':
        working_key = working_key.replace(command_whole, '', 1)
        adventure.silent_warp(command_params)
        return working_key

    if command_type == 'divider':
        working_key = working_key.replace(command_whole, divider(command_params), 1)
        return working_key

    if command_type == 'uget':
        working_key = working_key.replace(command_whole, adventure.uget(command_params), 1)
        return working_key

    if command_type == 'button':
        working_key = working_key.replace(command_whole, adventure.button(command_params), 1)
        return working_key

    if command_type == 'pget':
        working_key = working_key.replace(command_whole, adventure.pget(command_params), 1)
        return working_key

    if command_type == 'c':
        working_key = working_key.replace(command_whole, special_character(command_params), 1)

    return working_key.replace(command_whole, '', 1) # remove any invalid commands

def special_character(str_value):
    int_value = adventure.safe_cast(str_value, int, 0)
    if int_value < 0 or int_value > 255:
        int_value = 0
    return chr(int_value)

def divider(danger):
    sequence = ''
    while(len(sequence) < 30):
        sequence = sequence + dividers[adventure.safe_cast(danger, int, 0)]
    return sequence

##
#   senary tree search for browser address entry ui
##

def calc_range():
    offset = 0
    span = 0
    layers = len(branch)
    if layers > 3:
        layers = 3
    for layer in range(0, layers):
        span = calc_span(layer)
        offset = offset + (span * branch[layer])
    return offset, offset + (span - 1)

def calc_span(layer):
    span = 1296
    for i in range(0, layer + 1):
        span = int(span / 6)
    return span

def clear_tree():
    global branch
    branch = []

def add_branch(option):
    global branch
    branch.append(option)

def check_finish():
    if len(branch) == 4:
        offset = calc_range()[0]
        return offset + branch[3]
    else:
        return -1

def print_url_options():

    screen.clear_screen()
    buttons.empty()
    for i in range(0, 6):
        buttons.add(str(i))

    span = calc_span(len(branch))
    offset = calc_range()[0]

    for option in range(0, 6):
        buffer_start = (option + 2) * 30 # line 2 - line 7
        working_key = '[' + ['r', 'y', 'g', 't', 'b', 'v'][option] + '] ' + str(offset + (option * span))
        if len(branch) < 3:
            working_key = working_key + '-' + str((offset + (option * span)) + (span - 1))

        i = buffer_start
        for element in working_key:
            element_value = ord(element)
            if element_value > 255 or element_value < 0:
                element_value = 0
            screen.screen_buffer[i] = element_value
            i = i + 1

    i = 0
    for element in 'select browser address':
        element_value = ord(element)
        if element_value > 255 or element_value < 0:
            element_value = 0
        screen.screen_buffer[i] = element_value
        i = i + 1

    for i in range(0, 30):
        screen.morph[i] = 1

    screen.flip_page()
