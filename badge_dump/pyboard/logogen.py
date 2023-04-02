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
import mode
import screen
import buttons
import prng
import rgb
import adventure

# logo engine globals
logogen_badge_id = 0b1010101010100101 # not really be we really really don't want this to be a 0
logogen_layer_steps = [0] * 6
logogen_layer_enabled = [0] * 6
logogen_layer_selected = 0

logogen_prng = 0
persist_prng = 0

def initialize(badge_id):
    global logogen_badge_id, logogen_prng

    logogen_badge_id = badge_id + 1

    logogen_prng = prng.new_lfsr()
    print('logogen: logogen_prng: ' + str(logogen_prng))
    prng.start(logogen_prng, badge_id + 1, 0)

# logo gen ui event

def logogen_click(user_input):
    print('user input: ' + str(user_input))
    if user_input == 0: #r  toggle the current layer
        logogen_layer_toggle()
    elif user_input == 1: #y  return to the previous layer
        logogen_layer_previous()
    elif user_input == 2: #g  proceed to the next layer
        logogen_layer_next()
    elif user_input == 3: #t  change this layer to the previous step
        logogen_layer_step()
    elif user_input == 4: #b  change this layer to the next step
        logogen_layer_unstep()
    elif user_input == 5: # finish the logo design
        mode.verify_type = 1
        mode.start(mode.VERIFY_MODE)

    print('selected: ' + str(logogen_layer_selected))
    for i in range(0, 5):
        print('layer[' + str(i) + '] enabled: ' + str(logogen_layer_enabled[i]))
        print('layer[' + str(i) + '] steps: ' + str(logogen_layer_steps[i]))

def logogen_random_for_idle():
    global logogen_layer_enabled, logogen_layer_steps
    prng.start(logogen_prng, prng.step(rgb.rgb_prng, 1, 3113), 7)
    while(True):
        enabled_count = 0
        for i in range(0, 5):
            logogen_layer_enabled[i] = prng.step(logogen_prng, 0, 2)
            if logogen_layer_enabled[i] == 1:
                logogen_layer_steps[i] = prng.step(logogen_prng, 0, 256)
                enabled_count = enabled_count + 1
        if enabled_count > 0:
            break
    logogen_layer_changed(local = False)

# logo gen layer functions

def logogen_layer_toggle():
    global logogen_layer_enabled, logogen_layer_selected
    if logogen_layer_enabled[logogen_layer_selected] == 0:
        logogen_layer_enabled[logogen_layer_selected] = 1
    else:
        logogen_layer_enabled[logogen_layer_selected] = 0
    logogen_layer_changed()

def logogen_layer_previous():
    global logogen_layer_selected
    logogen_layer_selected = logogen_layer_selected - 1
    if logogen_layer_selected < 0: logogen_layer_selected = 5

def logogen_layer_next():
    global logogen_layer_selected
    logogen_layer_selected = logogen_layer_selected + 1
    if logogen_layer_selected > 5: logogen_layer_selected = 0

def logogen_layer_step():
    global logogen_layer_selected, logogen_layer_enabled, logogen_layer_steps
    if logogen_layer_enabled[logogen_layer_selected] == 1:
        logogen_layer_steps[logogen_layer_selected] = logogen_layer_steps[logogen_layer_selected] + 1
    if logogen_layer_steps[logogen_layer_selected] > 255:
        logogen_layer_steps[logogen_layer_selected] = 0
    logogen_layer_changed()

def logogen_layer_unstep():
    global logogen_layer_selected, logogen_layer_enabled, logogen_layer_steps
    if logogen_layer_enabled[logogen_layer_selected] == 1:
        logogen_layer_steps[logogen_layer_selected] = logogen_layer_steps[logogen_layer_selected] - 1
    if logogen_layer_steps[logogen_layer_selected] < 0:
        logogen_layer_steps[logogen_layer_selected] = 255
    logogen_layer_changed()

def logogen_layer_changed(local = True):
    screen.clear_screen()
    bake(local)
    buttons.fill()
    screen.flip_page()

def logogen_reload():
    screen.clear_screen()
    logogen_reload_bake()
    screen.flip_page()

def logogen_reload_bake():
    global logogen_layer_enabled
    for i in range(0, 5): # for each layer
        prng.start(logogen_prng, logogen_badge_id, logogen_layer_steps[i])
        if logogen_layer_enabled[i] == 1:
            render(i) # render this layer

def bake(local = True):
    global logogen_layer_enabled
    for i in range(0, 6): # for each layer
        prng.start(logogen_prng, logogen_badge_id, logogen_layer_steps[i])
        if logogen_layer_enabled[i] == 1:
            render(i, local) # render this layer

def render(layer, local = True):
    if layer == 0: render_background()          # background
    elif layer == 1: render_glyphs()            # 1 glyph per pixel glyphs
    elif layer == 2: render_tymkrscii()         # alpha tymkrscii v0
    elif layer == 3: render_big_glyph()         # 2x3 glyph per pixel
    elif layer == 4: render_username(local)     # username
    elif layer == 5: render_hud()               # heads up display for editor

def render_background():
    for z in range(0, prng.step(logogen_prng, 1, 16)):

        case = prng.step(logogen_prng, 0, 5)
        if case == 0:
            char0 = prng.step(logogen_prng, 1,3)
            char1 = char0
        elif case == 1:
            char0 = prng.step(logogen_prng, 175, 179)
            char1 = char0
        elif case == 2:
            char0 = prng.step(logogen_prng, 225, 254)
            char1 = char0
        elif case == 3:
            char0 = prng.step(logogen_prng, 179, 181)
            char1 = prng.step(logogen_prng, 179, 181)
        elif case == 4:
            char0 = prng.step(logogen_prng, 0, 256)
            char1 = prng.step(logogen_prng, 0, 256)

        spark = prng.step(logogen_prng, 2, 33)
        for i in range(0, 960):
            if i % spark == 0:
                flip = prng.step(logogen_prng, 0, 2)
                if flip == 0:
                    screen.screen_buffer[i] = char0
                elif flip == 1:
                    screen.screen_buffer[i] = char1

def render_glyphs():
    for i in range(0, prng.step(logogen_prng, 0, 5)):
        plot_glyph(get_pixels(prng.step(logogen_prng, 0, 256)), prng.step(logogen_prng, 0, 23), prng.step(logogen_prng, 0, 20), prng.step(logogen_prng, 210, 213))

def render_tymkrscii(): # tymkrscii v0 *.tci file
    file_names = []
    for file_name in os.listdir('clipart/'):
        file_names.append(file_name)

    f = open('clipart/' + file_names[prng.step(logogen_prng, 0, len(file_names))], "rb")
    for i in range(0, 960):
        glyph = int.from_bytes(f.read(1), 'big')
        if glyph > 0:
            screen.screen_buffer[i] = glyph
    f.close()

def render_big_glyph():
    big_plot_glyph(get_pixels(prng.step(logogen_prng, 0, 256)), prng.step(logogen_prng, 200, 203))

def render_username(local = True):
    name = 'cyphercon'
    if local:
        name = adventure.pget('2')
    else:
        name = name_generator() #.capitalize() but not on micropython, sadly
    for i in range(0, len(name)):
        screen.screen_buffer[928 - (len(name) - i)] = ord(name[i:i+1])
    screen.screen_buffer[928] = 93
    screen.screen_buffer[928 - len(name) - 1] = 91
    screen.screen_buffer[928 - len(name) - 2] = prng.step(logogen_prng, 15, 32)

def render_hud():
    global logogen_layer_selected, logogen_layer_steps
    logogen_layer_index = str(logogen_layer_selected)
    logogen_layer_on = str(logogen_layer_enabled[logogen_layer_selected])
    logogen_layer_value = str(logogen_layer_steps[logogen_layer_selected])

    print('logogen_layer_index: ' + logogen_layer_index)
    print('logogen_layer_on: ' + logogen_layer_on)
    print('logogen_layer_value: ' + logogen_layer_value)

    for i in range(0, len(logogen_layer_index)):
        screen.screen_buffer[870 + i] = ord(logogen_layer_index[i:i+1])
    for i in range(0, len(logogen_layer_on)):
        screen.screen_buffer[900 + i] = ord(logogen_layer_on[i:i+1])
    for i in range(0, len(logogen_layer_value)):
        screen.screen_buffer[930 + i] = ord(logogen_layer_value[i:i+1])

# logogen drawing functions

# draw a glyph from the character map
# use 3x3 glyphs on screen for each pixel
def big_plot_glyph(pixels, glyph):
    xoffset = 3
    yoffset = 3
    for y in range(0, 13):
        for x in range(0, 8):
            if pixels[(y * 8) + x] == 1:
                xoffset = 3 + (x * 3)
                yoffset = 3 + (y * 2)
                screen.screen_buffer[((yoffset + 0) * 30) + (xoffset + 0)] = glyph
                screen.screen_buffer[((yoffset + 0) * 30) + (xoffset + 1)] = glyph
                screen.screen_buffer[((yoffset + 0) * 30) + (xoffset + 2)] = glyph
                screen.screen_buffer[((yoffset + 1) * 30) + (xoffset + 0)] = glyph
                screen.screen_buffer[((yoffset + 1) * 30) + (xoffset + 1)] = glyph
                screen.screen_buffer[((yoffset + 1) * 30) + (xoffset + 2)] = glyph

# draw a glyph from the character map
# use 1x1 glyphs on screen for each pixel
def plot_glyph(pixels, xoffset, yoffset, glyph):
    for y in range(0, 13):
        for x in range(0, 8):
            if pixels[(y * 8) + x] == 1:
                screen.screen_buffer[(y * 30) + x + (yoffset * 30) + xoffset] = glyph

def get_pixels(char_index):
    pixels = []
    for y in range(0, 13):
        row = screen.character_map[(char_index * 13) + y]
        for x in range(0, 8):
            pixels.append((row & 0b10000000) >> 7)
            row = row << 1
    return pixels

# logo gen name generator

def name_generator():
    pre = ['wh','add','w','kn','c','m','r','h','chr','l','b','cl','qu','pl','gr','bl','tr','h','dr','v','y','n', 'bl']
    midv1 = ['a','e','i','o','u', 'ie', 'oo', 'ou', 'ae', 'ue','io']
    midc1 = ['sk','sh','r','w','s','k','y','l','s','ss','nt','g','t']
    midv2 = ['','a','e','i','o','u', 'ie', 'oo', 'ou', 'ae', 'ue','io']
    post = ['','s','t']
    return pre[prng.step(logogen_prng, 0,len(pre))] + midv1[prng.step(logogen_prng, 0,len(midv1))] + midc1[prng.step(logogen_prng, 0,len(midc1))] + midv2[prng.step(logogen_prng, 0,len(midv2))] + post[prng.step(logogen_prng, 0,len(post))]
