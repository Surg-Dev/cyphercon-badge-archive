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

# disclaimer: any divergent capitalization style is left over from Wire's hardware PoC demo

Mod = machine.Pin(15, machine.Pin.OUT, value=0)
IR_out = machine.Pin(16, machine.Pin.OUT, value=0) # UART0 -wire 2022
IR_in = machine.Pin(17, machine.Pin.IN) # UART0 -wire 2022
uart0 = machine.UART(0, baudrate=3000, tx=IR_out, rx=IR_in)

# could save a lot of ram
# if you re-write the RX buffer circular counter stuff
# to support a smaller rx_buffer size
# the packets are only 80 bytes, so this is overkill
rx_buffer = bytearray(range(8208))

tx_buffer = bytearray(range(80))

def initialize():
    PIOirTxInit()

def PIOirTxInit():
    sm0 = rp2.StateMachine(0, irPIO, freq=(38000*4), set_base=Mod, in_base=IR_out, jmp_pin=IR_out)  # freq=2000 -wire 2022
    sm0.active(1)
    return

##
@rp2.asm_pio(set_init=(rp2.PIO.OUT_LOW), in_shiftdir=rp2.PIO.SHIFT_LEFT)  # make sure to update this for every output pin you plan to use -wire 2022
def irPIO():
    wrap_target()
    label("loop_start")    # do not put a label at the end of the loop it will not work as expected.... -wire 2022
    set(pins, 0)            [0]
    jmp(pin, "loop_start")  [0]
    set(pins, 1)            [1]
    wrap()
    return

def tx(): # uarts are suddenly nonblocking and kinda broken, so this is the best we can do
    for i in range(0, 80):
        uart0.write(tx_buffer[79 - i:(79 - i) + 1])
        uart0.flush()

# not used anywhere but handy if you need it
# def ir_rx_debug():
#     while(uart0.any() > 0):
#         try:
#             print(uart0.read(1).decode('utf-8'), end = "")
#         except:
#             print(uart0.read(1))

