# Copyright (C) 2023 tymkrs
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name of tymkrs shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization from tymkrs.

import machine
import counters
import mode

# disclaimer: any divergent capitalization style is left over from Wire's hardware PoC demo

# encoder pins
Enc1A    = machine.Pin(5, machine.Pin.IN)
Enc1B    = machine.Pin(4, machine.Pin.IN)
Enc1P    = machine.Pin(1, machine.Pin.IN)

# reset encoders to 0
Enc1cnt = 0
Enc1cntLast = 0
Enc1debounce = 0

def initialize():
    Enc1A.irq(trigger=machine.Pin.IRQ_FALLING, handler=enc1_callback)

def enc1_callback(pin):
    global Enc1cnt, Enc1B
    if(Enc1B.value() == 1):
        Enc1cnt += 1
    else:
        Enc1cnt -= 1
    return

def get_rotation_state(): # returns 0-7, sets ui_color to same
    global Enc1cntLast
    # check on the quadrature encoder rotation
    if(Enc1cntLast != Enc1cnt):
        if Enc1cnt > Enc1cntLast:
            print("get down!")
            counters.reset(mode.to_idle_counter_index)
            counters.reset(mode.to_next_counter_index)
            mode.ui_color = mode.ui_color - 1
            if mode.ui_color < 0:
                mode.ui_color = 7
        if Enc1cntLast > Enc1cnt:
            print("ok, hup!")
            counters.reset(mode.to_idle_counter_index)
            counters.reset(mode.to_next_counter_index)
            mode.ui_color = mode.ui_color + 1
            if mode.ui_color > 7:
                mode.ui_color = 0
        Enc1cntLast = Enc1cnt
    return mode.ui_color

def get_pressed_state(): # returns True / False
    global Enc1debounce
    # check on the quadrature encoder press
    if(Enc1P.value() == 0 and Enc1debounce == 0):
        counters.reset(mode.to_idle_counter_index)
        counters.reset(mode.to_next_counter_index)
        Enc1debounce = 10
        return True #encoder_click()
    elif(Enc1debounce != 0):
        if(Enc1P.value() == 0):
            Enc1debounce = 10
        else:
            Enc1debounce -= 1
    return False
