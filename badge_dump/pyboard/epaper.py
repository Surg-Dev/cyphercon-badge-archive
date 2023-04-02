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

epaper_busy_pin = machine.Pin(9, machine.Pin.IN)
epaper_reset_pin = machine.Pin(10, machine.Pin.OUT, value=0)
epaper_data_command_pin = machine.Pin(13, machine.Pin.OUT, value=0)
epaper_chip_select_pin = machine.Pin(12, machine.Pin.OUT, value=1)
epaper_serial_clock_pin = machine.Pin(14, machine.Pin.ALT)
epaper_serial_data_out_pin = machine.Pin(11, machine.Pin.ALT)

spi_epaper = machine.SPI(1, baudrate = 6000000, polarity = 0, phase = 0, bits = 8, firstbit = machine.SPI.MSB, sck = epaper_serial_clock_pin, mosi = epaper_serial_data_out_pin, miso = None)

def initialize_display():
    for t in range(0, 20000): pass # long enough delay to allow ePaper to fully reset
    epaper_reset_pin.on() # pin is initially set low when initilized above
    for t in range(0, 20000): pass # allow reset to settle
    send_spi_byte(0x04, 0) # power on screen
    send_spi_byte(0x00, 0) # configure the screen
    send_spi_byte(0b00011111, 1) # using defaults
    send_spi_byte(0x00, 1)
    clear_display()

def clear_display():
    # send black data (0 = pixel black or red, 1 = pixel white or red)
    send_spi_byte(0x10, 0)
    for i in range(0, 12480):
        send_spi_byte(0xFF, 1)
    # send red data (1 = pixel red, 0 = pixel white or black) # screen get mad if you don't *shrug*
    send_spi_byte(0x13, 0)
    for i in range(0, 12480):
        send_spi_byte(0x00, 1)
    # send the screen refresh
    send_spi_byte(0x12, 0)

def send_spi_byte(data, data_command):
    busy_blocking()
    xfer = bytearray()                                          # format the data...
    xfer.append(data & 0xFF)
    epaper_data_command_pin.value(data_command)                 # set the data / #command pin
    epaper_chip_select_pin.off()                                # set CS low to indicate new xfer
    spi_epaper.write(xfer)                                      # send byte
    epaper_chip_select_pin.on()                                 # set CS high to indicate xfer done

def busy_check():
    if(epaper_busy_pin.value() == 0):
        return True
    else:
        return False

def busy_blocking():
    while(busy_check()):
        pass
