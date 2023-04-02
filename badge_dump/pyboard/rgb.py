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
import rp2
import prng
import mode

# disclaimer: any divergent capitalization style is left over from Wire's hardware PoC demo

# idle_animation
CYCLE = (0b110110, 0b111111, 0b101101, 0b001001, 0b101101, 0b111111, 0b011011, 0b010010, 0b011011, 0b111111, 0b110110, 0b100100)
top_cycle = 0
bottom_cycle = 6
speed_cycle = 40000
speed_cycle_mod = 200

rgb_prng = 0

# bump_rgb
ui_bump = 0

# RGB signals
B = machine.Pin(18, machine.Pin.OUT, value=1)
G = machine.Pin(19, machine.Pin.OUT, value=1)
R = machine.Pin(20, machine.Pin.OUT, value=1)
RGB1 = machine.Pin(21, machine.Pin.OUT, value=0)
RGB2 = machine.Pin(22, machine.Pin.OUT, value=0)
RGB3 = machine.Pin(26, machine.Pin.OUT, value=0)
RGB4 = machine.Pin(27, machine.Pin.OUT, value=0)

# led on pico
Led = machine.Pin(25, machine.Pin.OUT, value=0)

def initialize():
    global sm4, rgb_prng
    sm4 = rp2.StateMachine(4, rgbPIO, freq=100000, out_base=B, set_base=RGB1, sideset_base=RGB3, in_base=None, jmp_pin=None)
    sm4.active(1)
    setRGBleds(0x000)
    rgb_prng = prng.new_lfsr()
    prng.start(rgb_prng, 984566465465, 0)
    print('rgb: rgb_prng: ' + str(rgb_prng))

@rp2.asm_pio(
    out_init=(rp2.PIO.OUT_HIGH, rp2.PIO.OUT_HIGH, rp2.PIO.OUT_HIGH),
    set_init=(rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW),
    sideset_init=(rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW),
    in_shiftdir=rp2.PIO.SHIFT_LEFT,
    out_shiftdir=rp2.PIO.SHIFT_RIGHT
)  # make sure to update this for every output pin you plan to use -wire 2022

def rgbPIO():
    wrap_target()
    pull(noblock)       [0]  # when pulling on a empty FIFO in nonblocking the OSR will be loaded with X instead -wire 2022
    mov(x, osr)         [0]  # save the OSR to X in case it changed -wire 2022

    set(pins, 0x0)      .side(0x0) [0]
    out(pins, 3)        .side(0x0) [0]
    set(pins, 0x1)      .side(0x0) [3]
    nop()               .side(0x0) [3]
    nop()               .side(0x0) [3]
    nop()               .side(0x0) [3]
    nop()               .side(0x0) [3]
    nop()               .side(0x0) [3]
    set(pins, 0x0)      .side(0x0) [0]
    out(pins, 3)        .side(0x0) [0]
    set(pins, 0x2)      .side(0x0) [3]
    nop()               .side(0x0) [3]
    nop()               .side(0x0) [3]
    nop()               .side(0x0) [3]
    nop()               .side(0x0) [3]
    nop()               .side(0x0) [3]
    set(pins, 0x0)      .side(0x0) [0]
    out(pins, 3)        .side(0x1) [3]
    nop()               .side(0x1) [3]
    nop()               .side(0x1) [3]
    nop()               .side(0x1) [3]
    nop()               .side(0x1) [3]
    nop()               .side(0x1) [3]
    set(pins, 0x0)      .side(0x0) [0]
    out(pins, 3)        .side(0x2) [3]
    nop()               .side(0x2) [3]
    nop()               .side(0x2) [3]
    nop()               .side(0x2) [3]
    nop()               .side(0x2) [3]
    nop()               .side(0x2) [3]
    wrap()

    return

def setRGBleds(ledValues):
    # this function takes in the led state machine sm and ledValues
    # only the lower 12 bits of ledValues is used and when set the led is on
    # bit 11 = R of LED4, 10 = G of LED4, 9 = B of LED4,
    # bit 8 = R of LED3, 7 = G of LED3, 6 = B of LED3,
    # bit 5 = R of LED2, 4 = G of LED2, 3 = B of LED2,
    # bit 2 = R of LED1, 1 = G of LED1, 0 = B of LED1
    # -wire 2022
    sm4.put(~ledValues)
    return

def bump_rgb():
    global ui_bump
    ui_bump = ui_bump - 1
    if ui_bump < 0: ui_bump = 3
    if ui_bump == 0: setRGBleds((0b111000000000, 0b000111111111, 0b000100100100, 0b000110110110, 0b000010010010, 0b000011011011, 0b000001001001, 0b000101101101)[mode.ui_color])
    if ui_bump == 1: setRGBleds((0b000111000000, 0b111000111111, 0b100000100100, 0b110000110110, 0b010000010010, 0b011000011011, 0b001000001001, 0b101000101101)[mode.ui_color])
    if ui_bump == 2: setRGBleds((0b000000111000, 0b111111000111, 0b100100000100, 0b110110000110, 0b010010000010, 0b011011000011, 0b001001000001, 0b101101000101)[mode.ui_color])
    if ui_bump == 3: setRGBleds((0b000000000111, 0b111111111000, 0b100100100000, 0b110110110000, 0b010010010000, 0b011011011000, 0b001001001000, 0b101101101000)[mode.ui_color])

def idle_animation():
    global top_cycle, bottom_cycle, speed_cycle, speed_cycle_mod
    top_cycle = top_cycle + 1
    if top_cycle > 11:
        top_cycle = 0
    bottom_cycle = bottom_cycle - 1
    if bottom_cycle < 0:
        bottom_cycle = 11
    speed_cycle = speed_cycle + speed_cycle_mod
    if speed_cycle > 60000:
        speed_cycle_mod = speed_cycle_mod * -1
    if speed_cycle < 2000:
        speed_cycle_mod = speed_cycle_mod * -1
    setRGBleds((CYCLE[top_cycle] << 6) | CYCLE[bottom_cycle])
    for i in range(0, speed_cycle):
        pass

def wake_up_animation():
    for x in range(0, 32):
        setRGBleds(prng.step(rgb_prng, 0, 4096))
        for y in range(0, 3000):
            pass
    setRGBleds((0b000000000000, 0b111111111111, 0b100100100100, 0b110110110110, 0b010010010010, 0b011011011011, 0b001001001001, 0b101101101101)[mode.ui_color])
