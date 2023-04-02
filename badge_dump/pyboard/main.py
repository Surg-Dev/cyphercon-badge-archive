# Copyright (C) 2023 tymkrs
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name of tymkrs shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization from tymkrs.

import gc
import screen
import rgb
import encoder
import ir
import counters
import mode
import prng
import network
import logogen
import adventure

def badge_init():
    print('booting Badge OS')
    
    network.create_cache_map_if_missing()
    network.create_versions_if_missing()
    network.create_empty_user_if_missing()
    
    screen.initialize()
    rgb.initialize()
    encoder.initialize()
    mode.initialize()
    
    adventure.initialize()
    logogen.initialize(adventure.player_id)
    
    network.initialize()
    
    mode.start(mode.MAIN_MENU_MODE)
    print('main: ' + free(full = True))

def free(full=False):
    gc.collect()
    F = gc.mem_free()
    A = gc.mem_alloc()
    T = F+A
    P = '{0:.2f}%'.format(F/T*100)
    if not full: return P
    else : return ('Total:{0} Free:{1} ({2})'.format(T,F,P))

badge_init()

while(True):
    if mode.ui_mode == mode.NETWORK_MODE:
        network.network_clock()
    else:
        if  mode.ui_mode == mode.IDLE_MODE:
            rgb.idle_animation()
            if counters.count(mode.to_next_counter_index):
                mode.next_idle_screen() # go update the idle screen
                print('main: ' + free(full = True))
        else:
            if counters.count(mode.to_idle_counter_index):
                mode.idle_entry_type = 0
                mode.start(mode.IDLE_MODE)      
    rgb.setRGBleds((0b000000000000, 0b111111111111, 0b100100100100, 0b110110110110, 0b010010010010, 0b011011011011, 0b001001001001, 0b101101101101)[encoder.get_rotation_state()])
    if encoder.get_pressed_state():
        mode.encoder_click_event()
        while(encoder.get_pressed_state()):
            pass
