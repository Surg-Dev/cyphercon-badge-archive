# Copyright (C) 2023 tymkrs
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name of tymkrs shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization from tymkrs.

import epaper
import rgb

screen_buffer = bytearray(range(960))
morph = bytearray(range(960))

cursor_x = 0
cursor_y = 0

def initialize():
    epaper.initialize_display()

def clear_screen():
    global screen_buffer
    set_cursor(0, 0)
    for i in range(0, 960):
        screen_buffer[i] = 0
        morph[i] = 0

def render_file(file_name, modifiers = []):
    global screen_buffer
    clear_screen()
    load_tymkrscii(file_name)
    if len(modifiers) >= 2:
        for i in range(0, len(modifiers), 2):
            if modifiers[i] >= 0 and modifiers[i] < 960:
                if modifiers[i + 1] >= 0 and modifiers[i + 1] < 256:
                    print('screen: render_file modify slot: ' + str(modifiers[i]) + ' to glyph: ' + str(modifiers[i + 1]))
                    screen_buffer[modifiers[i]] = modifiers[i + 1]
    flip_page()

def render_arttext(text):
    clear_screen()
    art_file = ''
    if text[0:5] == 'art: ' and (text.find('.tci ', 6) + 4) > 6:
        art_file = text[5:(text.find('.tci ', 6) + 4)]
    if art_file != '':
        load_tymkrscii('world/art/' + art_file)
        set_cursor(0, 16)
        add_formated_text(text.replace('art: ' + art_file + ' ', ''))
    else:
        add_formated_text(text)
    flip_page()

def flip_page():
    # send the page data
    epaper.send_spi_byte(0x13, 0)
    for row_start in range(0, 960, 30): # 32 rows
        for line in range(0, 13):
            for column in range(0, 30):
                if morph[row_start + column] == 0: # morph: normal
                    epaper.send_spi_byte(~character_map[(screen_buffer[row_start + column] * 13) + line], 1)
                else: # morph: invert
                    epaper.send_spi_byte(character_map[(screen_buffer[row_start + column] * 13) + line], 1)
    epaper.send_spi_byte(0x10, 0)
    for row_start in range(0, 960, 30): # 32 rows
        for line in range(0, 13):
            for column in range(0, 30):
                if morph[row_start + column] == 0: # morph: normal
                    epaper.send_spi_byte(~character_map[(screen_buffer[row_start + column] * 13) + line], 1)
                else: # morph: invert
                    epaper.send_spi_byte(character_map[(screen_buffer[row_start + column] * 13) + line], 1)
    # send the screen refresh
    epaper.send_spi_byte(0x12, 0)
    while(epaper.busy_check()):
        rgb.bump_rgb()
        for t in range(0, 10000):
            pass

def set_cursor(x, y):
    global cursor_x, cursor_y
    if x >= 0 and x < 30 and y >= 0 and y < 32:
        cursor_x, cursor_y = x, y
        return True
    else:
        return False

def crlf():
    return set_cursor(0, cursor_y + 1)

def cursor_advance():
    global cursor_x, cursor_y
    cursor_x = cursor_x + 1
    if cursor_x > 29:
        cursor_x = 0
        cursor_y = cursor_y + 1
        if cursor_y > 31:
            cursor_y = 0

def get_position():
    global cursor_x, cursor_y
    return (cursor_x + (cursor_y * 30))

def add_text(text):
    global screen_buffer
    for element in text:
        element_value = ord(element)
        if element_value > 255 or element_value < 0:
            element_value = 0
        screen_buffer[get_position()] = element_value
        cursor_advance()

def add_formated_text(text):
    working_text = text
    while True:
        if len(working_text) < 29:
            add_text(working_text)
            crlf()
            break
        last_space = 29
        for i in range(0, 29):
            if working_text[i:i+1] == ' ':
                last_space = i
        this_line = working_text[0:last_space+1]
        working_text = working_text.replace(this_line, '', 1)
        add_text(this_line)
        crlf()

def load_tymkrscii(file_name):
    global screen_buffer
    print('screen: loading file: ' + file_name)
    rgb.bump_rgb()
    try:
        f = open(file_name, "rb")
    except OSError:  # open failed
        print('screen: file not found: ' + file_name)
        rgb.bump_rgb()
        return
    file_header = [0] * 16
    for i in range(0, 16):
        file_header[i] = int.from_bytes(f.read(1), 'big')
    tymkrscii_file_type = ''
    for i in range(0, 9):
        tymkrscii_file_type = tymkrscii_file_type + chr(file_header[i])
    tymkrscii_version = file_header[9]
    tymkrscii_page_columns = file_header[10]
    tymkrscii_page_rows = file_header[11]
    tymkrscii_data_mode = file_header[12]
    tymkrscii_mode_options = (file_header[13] << 16) + (file_header[14] << 8) + file_header[15]

    print('screen: File Type: ' + tymkrscii_file_type)
    print('screen: Version: ' + str(tymkrscii_version))
    print('screen: Page Columns: ' + str(tymkrscii_page_columns))
    print('screen: Page Rows: ' + str(tymkrscii_page_rows))
    print('screen: Data Mode: ' + str(tymkrscii_data_mode))
    rgb.bump_rgb()

    if tymkrscii_data_mode == 0:
        file_is_ok = True
        if tymkrscii_file_type != 'TYMKRSCII':
            file_is_ok = False
        if tymkrscii_version != 1:
            file_is_ok = False
        if tymkrscii_page_columns != 30:
            file_is_ok = False
        if tymkrscii_page_rows != 32:
            file_is_ok = False
        if file_is_ok:
            data_bytes = [0]
            for i in range(0, 960):
                data_bytes[0] = int.from_bytes(f.read(1), 'big')
                screen_buffer[i] = data_bytes[0]
            rgb.bump_rgb()
        else:
            print('screen: invalid file')

    elif tymkrscii_data_mode == 1:
        file_is_ok = True
        if tymkrscii_file_type != 'TYMKRSCII':
            file_is_ok = False
        if tymkrscii_version != 1:
            file_is_ok = False
        if tymkrscii_page_columns != 30:
            file_is_ok = False
        if tymkrscii_page_rows != 16:
            file_is_ok = False
        if file_is_ok:
            data_bytes = [0] * 2
            for i in range(0, 480):
                data_bytes[0] = int.from_bytes(f.read(1), 'big')
                data_bytes[1] = int.from_bytes(f.read(1), 'big')
                screen_buffer[i] = data_bytes[0]
                morph[i] = data_bytes[1]
            rgb.bump_rgb()
        else:
            print('screen: invalid file')

    f.close()

character_map = bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x33, 0x99, 0xcc, 0x66, 0x33, 0x99, 0xcc, 0x66, 0x33, 0x99, 0xcc, 0x66, 0x33, 0xcc, 0x99, 0x33, 0x66, 0xcc, 0x99, 0x33, 0x66, 0xcc, 0x99, 0x33, 0x66, 0xcc, 0x0, 0x0, 0x0, 0x10,
                 0x30, 0x7f, 0xff, 0x7f, 0x30, 0x10, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x8, 0xc, 0xfe, 0xff, 0xfe, 0xc, 0x8, 0x0, 0x0, 0x0, 0x18, 0x3c, 0x7e, 0xff, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18,
                 0x18, 0xff, 0x7e, 0x3c, 0x18, 0xff, 0x81, 0x81, 0x81, 0x81, 0x81, 0x81, 0x81, 0x81, 0x81, 0x81, 0x81, 0xff, 0x0, 0x7e, 0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x7e, 0x0, 0x0, 0x0, 0x3c, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x3c,
                 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x0, 0x0, 0x0, 0x0, 0x7e, 0x42, 0x5a, 0x5a, 0x5a, 0x5a, 0x5a, 0x5a, 0x5a, 0x42, 0x7e, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xff, 0x81, 0xbd, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xa5, 0xbd, 0x81, 0xff, 0x0, 0x6c, 0xfe, 0xfe, 0xfe, 0x7c, 0x38, 0x10, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x10, 0x38, 0x7c, 0xfe, 0x7c, 0x10, 0x38, 0x0, 0x0,
                 0x0, 0x0, 0x0, 0x0, 0x38, 0x38, 0xfe, 0xee, 0xee, 0x10, 0x38, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x10, 0x38, 0x7c, 0xfe, 0x7c, 0x38, 0x10, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x2, 0x7c, 0xa8, 0x28, 0x28, 0x28, 0x28, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x10, 0x28,
                 0x28, 0x44, 0x44, 0x82, 0xfe, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x30, 0x48, 0x48, 0x30, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x92, 0x7c, 0x44, 0xd6, 0x44, 0x7c, 0x92, 0x0, 0x0, 0x0, 0x0, 0x0, 0x10, 0x28, 0x44, 0x92, 0xc6, 0xaa, 0x92, 0x54,
                 0x38, 0x10, 0x0, 0x0, 0x0, 0x0, 0x0, 0xfe, 0xc6, 0x38, 0x7c, 0xfe, 0xfe, 0x0, 0x0, 0x0, 0x0, 0x0, 0x8d, 0xc1, 0x81, 0xc1, 0x99, 0xcd, 0x81, 0xcd, 0x81, 0xc1, 0x81, 0xc1, 0x91, 0xc, 0x3c, 0x22, 0x1, 0x1, 0x39, 0x7f, 0xff, 0xfe, 0xfc, 0xa8, 0x28,
                 0x28, 0x0, 0x7c, 0xfe, 0x92, 0xba, 0x6c, 0xfe, 0x54, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x7c, 0xfe, 0xba, 0xfe, 0xee, 0xfe, 0x7c, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x7c, 0xfe, 0x92, 0xfe, 0x82, 0xfe, 0x7c, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x7c, 0xfe, 0xd6,
                 0xfe, 0xc6, 0xfe, 0x7c, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x7c, 0xfe, 0xd6, 0xfe, 0x82, 0xc6, 0x7c, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x10, 0x10, 0x10, 0x10, 0x10, 0x0, 0x10, 0x0, 0x0, 0x0,
                 0x0, 0x0, 0x28, 0x28, 0x28, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x28, 0x28, 0xfe, 0x28, 0xfe, 0x28, 0x28, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x10, 0x3c, 0x50, 0x38, 0x14, 0x78, 0x10, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x40, 0xa4, 0x48,
                 0x10, 0x24, 0x4a, 0x4, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x30, 0x48, 0x40, 0x20, 0x54, 0x48, 0x34, 0x0, 0x0, 0x0, 0x0, 0x0, 0x10, 0x10, 0x10, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x8, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x8, 0x0,
                 0x0, 0x0, 0x0, 0x20, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x20, 0x0, 0x0, 0x0, 0x0, 0x10, 0x54, 0x38, 0x38, 0x54, 0x10, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x10, 0x10, 0x7c, 0x10, 0x10, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                 0x0, 0x0, 0x0, 0x0, 0x10, 0x10, 0x20, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x7c, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x10, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x4, 0x8, 0x8, 0x10, 0x10, 0x20, 0x20, 0x40, 0x0, 0x0,
                 0x0, 0x0, 0x0, 0x38, 0x44, 0x4c, 0x54, 0x64, 0x44, 0x38, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x10, 0x30, 0x10, 0x10, 0x10, 0x10, 0x38, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x38, 0x44, 0x4, 0x8, 0x10, 0x20, 0x7c, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x38, 0x44, 0x4,
                 0x18, 0x4, 0x44, 0x38, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x8, 0x18, 0x28, 0x48, 0x7c, 0x8, 0x8, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x38, 0x20, 0x20, 0x38, 0x4, 0x44, 0x38, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x38, 0x44, 0x40, 0x78, 0x44, 0x44, 0x38, 0x0, 0x0,
                 0x0, 0x0, 0x0, 0x0, 0x7c, 0x4, 0x4, 0x8, 0x8, 0x10, 0x10, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x38, 0x44, 0x44, 0x38, 0x44, 0x44, 0x38, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x38, 0x44, 0x44, 0x3c, 0x4, 0x44, 0x38, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x10, 0x10,
                 0x0, 0x10, 0x10, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x10, 0x10, 0x0, 0x10, 0x10, 0x20, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x8, 0x10, 0x20, 0x40, 0x20, 0x10, 0x8, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x7c, 0x0, 0x7c, 0x0, 0x0, 0x0, 0x0, 0x0,
                 0x0, 0x0, 0x0, 0x20, 0x10, 0x8, 0x4, 0x8, 0x10, 0x20, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x38, 0x44, 0x44, 0x8, 0x10, 0x0, 0x10, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x38, 0x44, 0x5c, 0x54, 0x5c, 0x40, 0x38, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x10, 0x28, 0x44,
                 0x7c, 0x44, 0x44, 0x44, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x78, 0x44, 0x44, 0x78, 0x44, 0x44, 0x78, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x38, 0x44, 0x40, 0x40, 0x40, 0x44, 0x38, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x78, 0x44, 0x44, 0x44, 0x44, 0x44, 0x78, 0x0,
                 0x0, 0x0, 0x0, 0x0, 0x0, 0x7c, 0x40, 0x40, 0x78, 0x40, 0x40, 0x7c, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x7c, 0x40, 0x40, 0x70, 0x40, 0x40, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x3c, 0x40, 0x40, 0x5c, 0x44, 0x44, 0x38, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x44,
                 0x44, 0x44, 0x7c, 0x44, 0x44, 0x44, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x38, 0x10, 0x10, 0x10, 0x10, 0x10, 0x38, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x3c, 0x4, 0x4, 0x4, 0x4, 0x44, 0x38, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x44, 0x48, 0x50, 0x60, 0x50, 0x48, 0x44,
                 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x7c, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x82, 0xc6, 0xaa, 0x92, 0x82, 0x82, 0x82, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x44, 0x64, 0x54, 0x4c, 0x44, 0x44, 0x44, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                 0x38, 0x44, 0x44, 0x44, 0x44, 0x44, 0x38, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x78, 0x44, 0x44, 0x78, 0x40, 0x40, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x38, 0x44, 0x44, 0x44, 0x44, 0x48, 0x34, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x78, 0x44, 0x44, 0x78, 0x50,
                 0x48, 0x44, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x38, 0x44, 0x40, 0x38, 0x4, 0x44, 0x38, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x7c, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x44, 0x44, 0x44, 0x44, 0x44, 0x44, 0x38, 0x0, 0x0, 0x0, 0x0,
                 0x0, 0x0, 0x44, 0x44, 0x44, 0x44, 0x44, 0x28, 0x10, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x82, 0x82, 0x82, 0x92, 0xaa, 0xc6, 0x82, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x44, 0x44, 0x28, 0x10, 0x28, 0x44, 0x44, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x44, 0x44, 0x28,
                 0x10, 0x10, 0x10, 0x10, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x7c, 0x4, 0x8, 0x10, 0x20, 0x40, 0x7c, 0x0, 0x0, 0x0, 0x0, 0x0, 0x18, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x18, 0x0, 0x0, 0x0, 0x0, 0x0, 0x40, 0x20, 0x20, 0x10, 0x10, 0x8, 0x8, 0x4, 0x0,
                 0x0, 0x0, 0x0, 0x30, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x30, 0x0, 0x0, 0x0, 0x0, 0x10, 0x28, 0x44, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xfe, 0x0, 0x0, 0x0, 0x0, 0x20, 0x10, 0x8, 0x0,
                 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x3c, 0x44, 0x44, 0x44, 0x3e, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x40, 0x40, 0x78, 0x44, 0x44, 0x44, 0x78, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x38, 0x44, 0x40, 0x44, 0x38, 0x0, 0x0, 0x0,
                 0x0, 0x0, 0x0, 0x4, 0x4, 0x3c, 0x44, 0x44, 0x44, 0x3c, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x38, 0x44, 0x7c, 0x40, 0x3c, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x18, 0x24, 0x70, 0x20, 0x20, 0x20, 0x20, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x38,
                 0x44, 0x44, 0x44, 0x3c, 0x4, 0x4, 0x44, 0x38, 0x0, 0x0, 0x40, 0x40, 0x78, 0x44, 0x44, 0x44, 0x44, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x10, 0x0, 0x10, 0x10, 0x10, 0x10, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x8, 0x0, 0x8, 0x8, 0x8, 0x8, 0x8, 0x8,
                 0x48, 0x30, 0x0, 0x0, 0x40, 0x40, 0x44, 0x48, 0x70, 0x48, 0x44, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x18, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x6c, 0x92, 0x92, 0x82, 0x82, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                 0x38, 0x44, 0x44, 0x44, 0x44, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x38, 0x44, 0x44, 0x44, 0x38, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x38, 0x44, 0x44, 0x44, 0x78, 0x40, 0x40, 0x40, 0x40, 0x0, 0x0, 0x0, 0x0, 0x38, 0x44, 0x44, 0x44, 0x3c,
                 0x4, 0x4, 0x4, 0x4, 0x0, 0x0, 0x0, 0x0, 0x38, 0x44, 0x40, 0x40, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x3c, 0x40, 0x38, 0x4, 0x78, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x20, 0x20, 0x7c, 0x20, 0x20, 0x24, 0x18, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                 0x0, 0x44, 0x44, 0x44, 0x44, 0x38, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x44, 0x44, 0x44, 0x28, 0x10, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x82, 0x92, 0x92, 0x92, 0x6c, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x44, 0x28, 0x10, 0x28, 0x44,
                 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x44, 0x44, 0x44, 0x44, 0x3c, 0x4, 0x4, 0x44, 0x38, 0x0, 0x0, 0x0, 0x0, 0x7c, 0x8, 0x10, 0x20, 0x7c, 0x0, 0x0, 0x0, 0x0, 0x0, 0x8, 0x10, 0x10, 0x10, 0x20, 0x10, 0x10, 0x10, 0x8, 0x0, 0x0, 0x0, 0x0, 0x0,
                 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x0, 0x0, 0x0, 0x0, 0x0, 0x20, 0x10, 0x10, 0x10, 0x8, 0x10, 0x10, 0x10, 0x20, 0x0, 0x0, 0x0, 0x0, 0x0, 0x32, 0x4c, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x38, 0x44, 0x92, 0x82, 0xaa, 0x82,
                 0xfe, 0x7c, 0xaa, 0x82, 0x44, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xaa, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xaa, 0xaa, 0xaa, 0x0, 0x0, 0x0, 0x0, 0x0, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18,
                 0x18, 0x0, 0x18, 0x18, 0x0, 0x18, 0x18, 0x0, 0x18, 0x18, 0x0, 0x18, 0x18, 0x0, 0x0, 0x3c, 0x3c, 0x0, 0x3c, 0x3c, 0x0, 0x3c, 0x3c, 0x0, 0x3c, 0x3c, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x1f, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x0, 0x0, 0x0, 0x0,
                 0x0, 0x0, 0xf8, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x1f, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0xf8, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x1f, 0x18,
                 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0xf8, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xff, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0xff, 0x0, 0x0, 0x0, 0x0, 0x0,
                 0x0, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0xff, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xe7, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xe7, 0xe7, 0xe7, 0x0, 0x0, 0x0, 0x0, 0x0, 0x18, 0x18, 0x18, 0x18, 0x18,
                 0x18, 0x0, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x3c, 0x3c, 0x3c, 0x3c, 0x3c, 0x3c, 0x0, 0x3c, 0x3c, 0x3c, 0x3c, 0x3c, 0x3c, 0x0, 0x0, 0x0, 0x0, 0x0, 0xff, 0x0, 0xff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24,
                 0x24, 0x24, 0x24, 0x24, 0x0, 0x0, 0x0, 0x0, 0x0, 0x1f, 0x18, 0x1f, 0x18, 0x18, 0x18, 0x18, 0x18, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x3f, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x0, 0x0, 0x0, 0x0, 0x0, 0x3f, 0x20, 0x27, 0x24, 0x24, 0x24, 0x24, 0x24, 0x0,
                 0x0, 0x0, 0x0, 0x0, 0xf8, 0x18, 0xf8, 0x18, 0x18, 0x18, 0x18, 0x18, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xfc, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x0, 0x0, 0x0, 0x0, 0x0, 0xfc, 0x4, 0xe4, 0x24, 0x24, 0x24, 0x24, 0x24, 0x18, 0x18, 0x18, 0x18, 0x18, 0x1f,
                 0x18, 0x1f, 0x0, 0x0, 0x0, 0x0, 0x0, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x3f, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x24, 0x24, 0x24, 0x24, 0x24, 0x27, 0x20, 0x3f, 0x0, 0x0, 0x0, 0x0, 0x0, 0x18, 0x18, 0x18, 0x18, 0x18, 0xf8, 0x18, 0xf8, 0x0, 0x0, 0x0,
                 0x0, 0x0, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0xfc, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x24, 0x24, 0x24, 0x24, 0x24, 0xe4, 0x4, 0xfc, 0x0, 0x0, 0x0, 0x0, 0x0, 0x18, 0x18, 0x18, 0x18, 0x18, 0x1f, 0x18, 0x1f, 0x18, 0x18, 0x18, 0x18, 0x18, 0x24, 0x24,
                 0x24, 0x24, 0x24, 0x24, 0x27, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x27, 0x20, 0x27, 0x24, 0x24, 0x24, 0x24, 0x24, 0x18, 0x18, 0x18, 0x18, 0x18, 0xf8, 0x18, 0xf8, 0x18, 0x18, 0x18, 0x18, 0x18, 0x24, 0x24, 0x24, 0x24,
                 0x24, 0x24, 0xe4, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0xe4, 0x4, 0xe4, 0x24, 0x24, 0x24, 0x24, 0x24, 0x0, 0x0, 0x0, 0x0, 0x0, 0xff, 0x0, 0xff, 0x18, 0x18, 0x18, 0x18, 0x18, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xff, 0x24,
                 0x24, 0x24, 0x24, 0x24, 0x24, 0x0, 0x0, 0x0, 0x0, 0x0, 0xff, 0x0, 0xe7, 0x24, 0x24, 0x24, 0x24, 0x24, 0x18, 0x18, 0x18, 0x18, 0x18, 0xff, 0x0, 0xff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0xff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                 0x24, 0x24, 0x24, 0x24, 0x24, 0xe7, 0x0, 0xff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x18, 0x18, 0x18, 0x18, 0x18, 0xff, 0x18, 0xff, 0x18, 0x18, 0x18, 0x18, 0x18, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0xff, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24,
                 0x24, 0x24, 0xe7, 0x0, 0xe7, 0x24, 0x24, 0x24, 0x24, 0x24, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x7, 0xc, 0x18, 0x18, 0x18, 0x18, 0x18, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xe0, 0x30, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x30, 0xe0, 0x0,
                 0x0, 0x0, 0x0, 0x0, 0x0, 0x18, 0x18, 0x18, 0x18, 0x18, 0xc, 0x7, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x1, 0x3, 0x3, 0x6, 0xe, 0x1c, 0x3c, 0x38, 0x70, 0x60, 0xc0, 0xc0, 0x80, 0x80, 0xc0, 0xc0, 0x60, 0x70, 0x38, 0x3c, 0x1c, 0xe, 0x6, 0x3, 0x3, 0x1, 0x81,
                 0xc3, 0xc3, 0x66, 0x7e, 0x3c, 0x3c, 0x3c, 0x7e, 0x66, 0xc3, 0xc3, 0x81, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xf8, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x1f,
                 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x0, 0x0, 0x0, 0x0, 0x0, 0xf8, 0xf8, 0xf8, 0x0, 0x0, 0x0, 0x0, 0x0, 0x3c, 0x3c, 0x3c, 0x3c, 0x3c, 0x3c, 0x3c, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                 0x0, 0x0, 0x0, 0x0, 0x1f, 0x1f, 0x1f, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x3c, 0x3c, 0x3c, 0x3c, 0x3c, 0x3c, 0x3c, 0x0, 0x0, 0x0, 0x0, 0x0, 0xf, 0xff, 0xf, 0x0, 0x0, 0x0, 0x0, 0x0, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x3c,
                 0x3c, 0x3c, 0x3c, 0x3c, 0x3c, 0x3c, 0x0, 0x0, 0x0, 0x0, 0x0, 0xf0, 0xff, 0xf0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x3c, 0x3c, 0x3c, 0x3c, 0x3c, 0x3c, 0x3c, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xff, 0xff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xff, 0xff, 0xff, 0xff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xff,
                 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x0, 0x0, 0x0, 0x0, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x0, 0x0, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
                 0xff, 0xff, 0xff, 0x7f, 0x7f, 0x7f, 0x7f, 0x7f, 0x7f, 0x7f, 0x7f, 0x7f, 0x7f, 0x7f, 0x7f, 0x7f, 0x3f, 0x3f, 0x3f, 0x3f, 0x3f, 0x3f, 0x3f, 0x3f, 0x3f, 0x3f, 0x3f, 0x3f, 0x3f, 0x1f, 0x1f, 0x1f, 0x1f, 0x1f, 0x1f, 0x1f, 0x1f, 0x1f, 0x1f, 0x1f, 0x1f,
                 0x1f, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0x7, 0x7, 0x7, 0x7, 0x7, 0x7, 0x7, 0x7, 0x7, 0x7, 0x7, 0x7, 0x7, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1,
                 0x1, 0x1, 0x1, 0x1, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xaa, 0x77, 0xaa, 0xdd, 0xaa, 0x77, 0xaa, 0xdd, 0xaa, 0x77, 0xaa, 0xdd, 0xaa, 0xaa, 0x55, 0xaa, 0x55, 0xaa, 0x55, 0xaa, 0x55, 0xaa, 0x55, 0xaa, 0x55, 0xaa, 0x0,
                 0x33, 0x0, 0xcc, 0x0, 0x33, 0x0, 0xcc, 0x0, 0x33, 0x0, 0xcc, 0x0, 0xff, 0xff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xf0, 0xf0, 0xf0,
                 0xf0, 0xf0, 0xf0, 0xf0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf0, 0xf0, 0xf0, 0xf0, 0xf0, 0xf0, 0xf0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xf0, 0xf0, 0xf0,
                 0xf0, 0xf0, 0xf0, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xf0, 0xf0, 0xf0, 0xf0, 0xf0, 0xf0, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
                 0xff, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf0, 0xf0, 0xf0, 0xf0, 0xf0, 0xf0, 0xff, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xf, 0xff, 0xf0, 0xf0, 0xf0, 0xf0, 0xf0, 0xf0, 0x3, 0x3, 0x3, 0x7, 0x7, 0x1f, 0x1f, 0x1f, 0x3f, 0x3f, 0xff, 0xff,
                 0xff, 0xc0, 0xc0, 0xc0, 0xe0, 0xe0, 0xf8, 0xf8, 0xf8, 0xfc, 0xfc, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xfc, 0xfc, 0xf8, 0xf8, 0xf8, 0xe0, 0xe0, 0xc0, 0xc0, 0xc0, 0xff, 0xff, 0xff, 0x3f, 0x3f, 0x1f, 0x1f, 0x1f, 0x7, 0x7, 0x3, 0x3, 0x3, 0xff, 0x0,
                 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                 0x0, 0x0, 0x0, 0x0, 0x0, 0xff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xff,
                 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xff, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xff, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40,
                 0x40, 0x40, 0x40, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x20, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x8, 0x8, 0x8, 0x8, 0x8, 0x8, 0x8, 0x8, 0x8, 0x8, 0x8, 0x8, 0x8, 0x4,
                 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1, 0x1, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa,
                 0xaa, 0xaa, 0xaa, 0xaa, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x55, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33,
                 0x33, 0x33, 0x0, 0x20, 0x40, 0x80, 0x40, 0x20, 0x4, 0x20, 0x40, 0x80, 0x40, 0x20, 0x0, 0x14, 0x14, 0x54, 0x80, 0x4c, 0x12, 0x12, 0x4c, 0x80, 0x54, 0x14, 0x14, 0x0])
