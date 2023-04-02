# Copyright (C) 2023 tymkrs
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name of tymkrs shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization from tymkrs.

from tkinter import *
from tkinter import ttk
from tkinter import filedialog

import png

##
#   globals, only you know ... python?
##

screen_buffer = [0] * 480
left_brush_index = 0
right_brush_index = 0
reticle_index = 0
loaded_file_name = ''

##
#   mouse event handlers
##

def tymkrscii_canvas_left_click(event):
    global screen_buffer
    global left_brush_index
    i = (int((event.x - 1) / 8) % 30) + (int((event.y - 1) / 13) * 30)
    if i < 480 and i >= 0:
        screen_buffer[i] = left_brush_index
        update_screen()

def tymkrscii_canvas_right_click(event):
    global screen_buffer
    global right_brush_index
    i = (int((event.x - 1) / 8) % 30) + (int((event.y - 1) / 13) * 30)
    if i < 480 and i >= 0:
        screen_buffer[i] = right_brush_index
        update_screen()

def tymkrscii_canvas_middle_click(event):
    global screen_buffer
    global left_brush_index
    i = (int((event.x - 1) / 8) % 30) + (int((event.y - 1) / 13) * 30)
    g = screen_buffer[i]
    if g < 512 and g >= 0:
        left_brush.tab[0]['image'] = PhotoImage(master=left_brush, file='glyphs/' + str(g) + '.png')
        left_brush.create_image(1, 1, anchor=NW, image=left_brush.tab[0]['image'])
        left_brush_index = g

def tymkrscii_canvas_scroll_up(event):
    global screen_buffer
    global left_brush_index
    i = (int((event.x - 1) / 8) % 30) + (int((event.y - 1) / 13) * 30)
    g = screen_buffer[i]
    g = (g + 1) % 512
    if g < 512 and g >= 0 and i < 480 and i >= 0:
        screen_buffer[i] = g
        update_screen()

def tymkrscii_canvas_scroll_down(event):
    global screen_buffer
    global left_brush_index
    i = (int((event.x - 1) / 8) % 30) + (int((event.y - 1) / 13) * 30)
    g = screen_buffer[i]
    g = g - 1
    if g < 0:
        g = 511
    if g < 512 and g >= 0 and i < 480 and i >= 0:
        screen_buffer[i] = g
        update_screen()

def tymkrscii_canvas_update_coords(event):
    global screen_buffer
    global reticle_index
    i = (int((event.x - 1) / 8) % 30) + (int((event.y - 1) / 13) * 30)
    if i < 480 and i >= 0:
        reticle_index = i
        status_label.config(text = str(event.x) + ', ' + str(event.y) + ' : ' + str(i) + ' = ' + str(screen_buffer[i]))
        update_screen()

def pallet_canvas_left_click(event):
    global left_brush_index
    g = (int((event.x - 1) / 8) % 30) + (int((event.y - 1) / 13) * 30)
    if g < 512 and g >= 0:
        left_brush.tab[0]['image'] = PhotoImage(master=left_brush, file='glyphs/' + str(g) + '.png')
        left_brush.create_image(1, 1, anchor=NW, image=left_brush.tab[0]['image'])
        left_brush_index = g

def pallet_canvas_right_click(event):
    global right_brush_index
    g = (int((event.x - 1) / 8) % 30) + (int((event.y - 1) / 13) * 30)
    if g < 512 and g >= 0:
        right_brush.tab[0]['image'] = PhotoImage(master=right_brush, file='glyphs/' + str(g) + '.png')
        right_brush.create_image(1, 1, anchor=NW, image=right_brush.tab[0]['image'])
        right_brush_index = g

##
#   button click handlers
##

def load_source():
    global loaded_file_name
    loaded_file_name = filedialog.askopenfilename(title='Load Source Image', filetypes=[("Image", "*.png")])
    if loaded_file_name:
        source_canvas.tab[0]['image'] = PhotoImage(master=source_canvas, file=loaded_file_name)
        source_canvas.create_image(0, 0, anchor=NW, image=source_canvas.tab[0]['image'])
        source_canvas.update()
    else:
        pass #canceled or whatever

def load_tymkrscii():
    global screen_buffer

    file = filedialog.askopenfilename(title='Load File', filetypes=[("Tymkrs Character Interchange", "*.tci")])

    if file:

        print('loading file: ' + file)
        f = open(file, "rb")

        # read in file header
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
        print('File Type: ' + tymkrscii_file_type)
        print('Version: ' + str(tymkrscii_version))
        print('Page Columns: ' + str(tymkrscii_page_columns))
        print('Page Rows: ' + str(tymkrscii_page_rows))
        print('Data Mode: ' + str(tymkrscii_data_mode))
        print('Mode Options: ' + format(tymkrscii_mode_options, '24b'))

        # perform header checks
        file_is_ok = True
        if tymkrscii_file_type != 'TYMKRSCII':
            file_is_ok = False
        if tymkrscii_version != 1:
            file_is_ok = False
        if tymkrscii_page_columns != 30:
            file_is_ok = False
        if tymkrscii_page_rows != 16:
            file_is_ok = False
        if file_is_ok and tymkrscii_data_mode == 1:
            data_bytes = [0] * 2
            for i in range(0, 480):
                data_bytes[0] = int.from_bytes(f.read(1), 'big')#, signed='False')
                data_bytes[1] = int.from_bytes(f.read(1), 'big')#, signed='False')
                if data_bytes[1] == 0: # normal mode
                    screen_buffer[i] = data_bytes[0]
                elif data_bytes[1] == 1: # inverted mode
                    screen_buffer[i] = data_bytes[0] + 256
            print('File is a valid v1 mode 1 Tymkrscii Page File')
        else:
            print('File is not a valid v1 mode 1 Tymkrscii Page File')
            # Mode 1 "256 Glyph / Morph" see Tymkrscii Page File Format Documentation for details.

        f.close()
        update_screen()
    else:
        pass #canceled or whatever

def save_file():
    global screen_buffer
    working_buffer = screen_buffer
    file = filedialog.asksaveasfilename(title='Save File', filetypes=[("Tymkrs Character Interchange", "*.tci")])
    if file:
        print('saving file ')
        print(file)
        f = open(file, "wb+")
        mode1_header = [0x54, 0x59, 0x4d, 0x4b, 0x52, 0x53, 0x43, 0x49, 0x49, 0x01, 0x1E, 0x10, 0x01, 0x00, 0x00, 0x00]
        mode1_normal = [0x00]
        mode1_inverted = [0x01]
        for i in range(0, 16):
            f.write(mode1_header[i].to_bytes(1, 'big'))
        for i in range(0, 480):
            if working_buffer[i] < 256:
                f.write(working_buffer[i].to_bytes(1, 'big'))
                f.write(mode1_normal[0].to_bytes(1, 'big'))
            else:
                corrected = working_buffer[i] - 256
                f.write(corrected.to_bytes(1, 'big'))
                f.write(mode1_inverted[0].to_bytes(1, 'big'))

        f.close()
    else:
        pass #canceled or whatever

def transcode():
    global loaded_file_name
    if loaded_file_name != '':
        trnscd(loaded_file_name)

##
#   utility functions
##

def trnscd(file_name):
    global screen_buffer
    for chunk_index in range(0, 480):
        screen_buffer[chunk_index] = fit(load_chunk(file_name, chunk_index))
        update_screen()
        tymkrscii_canvas.update()

def update_screen():
    global screen_buffer
    global reticle_index
    for i in range(0, 480):
        x = (i % 30) * 8
        y = int(i / 30) * 13
        tymkrscii_canvas.tab[i]['image'] = PhotoImage(master=tymkrscii_canvas, file='glyphs/' + str(screen_buffer[i]) + '.png')
        tymkrscii_canvas.create_image(x + 1, y + 1, anchor=NW, image=tymkrscii_canvas.tab[i]['image'])

    i = reticle_index
    x = (i % 30) * 8
    y = int(i / 30) * 13

    tymkrscii_canvas.create_image(x + 1, y + 1, anchor=NW, image=tymkrscii_canvas.tab[480]['image'])

def load_chunk(file_name, chunk_index):
    global screen_buffer

    chunk_x = (chunk_index % 30) * 8
    chunk_y = int(chunk_index / 30) * 13

    source=png.Reader(file_name)
    w, h, pixels, metadata = source.read_flat()
    pixel_byte_width = 4 if metadata['alpha'] else 3
    source_greyscale = [0] * 104
    for y in range(0,13):
        for x in range(0,8):
            pixel_position = (chunk_x + x) + (chunk_y + y) * w
            this_pixel = pixels[pixel_position * pixel_byte_width : (pixel_position + 1) * pixel_byte_width]
            if len(this_pixel) >= 3:
                source_greyscale[(y * 8) + x] = int((this_pixel[0] + this_pixel[1] + this_pixel[2]) / 3)
            else:
                source_greyscale[(y * 8) + x] = 128

    return source_greyscale

def fit(source_greyscale):
    fit_index = 255
    fit_score = 99999999
    for g in range(0, 512):
        glyph=png.Reader('glyphs/' + str(g) + '.png')
        w, h, pixels, metadata = glyph.read_flat()
        pixel_byte_width = 4 if metadata['alpha'] else 3
        tally = 0
        for y in range(0,13):
            for x in range(0,8):
                pixel_position = x + y * w
                this_pixel = pixels[pixel_position * pixel_byte_width : (pixel_position + 1) * pixel_byte_width]
                tally = tally + abs(int( ( (this_pixel[0] + this_pixel[1] + this_pixel[2]) / 3 ) / 1 ) - source_greyscale[(y * 8) + x])
        if tally < fit_score:
            fit_score = tally
            fit_index = g
            print(fit_index)
    return fit_index

##
#   main program
##

root = Tk()

icon=PhotoImage(file='icon.png')
root.iconphoto(True,icon)
root.title("Le Innet")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

frame = ttk.Frame(root)
frame.grid(column=0, row=0, columnspan=2, rowspan=1)

left_frame = ttk.Frame(frame)
left_frame.grid(column=0, row=0, columnspan=1, rowspan=1, sticky=(NW))

right_frame = ttk.Frame(frame)
right_frame.grid(column=1, row=0, columnspan=1, rowspan=1, sticky=(NE))

source_label = Label(left_frame, text='png source')
source_label.grid(column=0, row=0)
source_canvas = Canvas(left_frame, width=240, height=208, borderwidth=0, bg='white')
source_canvas.tab = [{} for k in range(0, 1)]
source_canvas.grid(column=0, row=1)

tymkrscii_label = Label(left_frame, text='tymkrscii')
tymkrscii_label.grid(column=0, row=2)
tymkrscii_canvas = Canvas(left_frame, width=240, height=208, borderwidth=0, bg='white')
tymkrscii_canvas.tab = [{} for k in range(0, 481)]
tymkrscii_canvas.grid(column=0, row=3)
tymkrscii_canvas.bind("<Button-1>", tymkrscii_canvas_left_click)
tymkrscii_canvas.bind("<B1-Motion>", tymkrscii_canvas_left_click)
tymkrscii_canvas.bind("<Button-3>", tymkrscii_canvas_right_click)
tymkrscii_canvas.bind("<B3-Motion>", tymkrscii_canvas_right_click)
tymkrscii_canvas.bind("<Button-2>", tymkrscii_canvas_middle_click)
tymkrscii_canvas.bind("<Motion>", tymkrscii_canvas_update_coords)
tymkrscii_canvas.bind("<Button-4>", tymkrscii_canvas_scroll_up)
tymkrscii_canvas.bind("<Button-5>", tymkrscii_canvas_scroll_down)

# I assume something will break with these binding on windows
# this may help? *shrug*
#
# with Windows OS
#<MouseWheel>
# with Linux OS
#<Button-4>
#<Button-5>

tymkrscii_canvas.tab[480]['image'] = PhotoImage(master=tymkrscii_canvas, file='reticle.png')

left_brush = Canvas(right_frame, width=8, height=13, borderwidth=0, bg='white')
left_brush.grid(column=0, row=0, sticky=(W))
left_brush.tab = [{} for k in range(0, 1)]
left_brush.tab[0]['image'] = PhotoImage(master=left_brush, file='glyphs/' + '0' + '.png')
left_brush.create_image(1, 1, anchor=NW, image=left_brush.tab[0]['image'])

right_brush = Canvas(right_frame, width=8, height=13, borderwidth=0, bg='white')
right_brush.grid(column=0, row=0, sticky=(E))
right_brush.tab = [{} for k in range(0, 1)]
right_brush.tab[0]['image'] = PhotoImage(master=right_brush, file='glyphs/' + '0' + '.png')
right_brush.create_image(1, 1, anchor=NW, image=right_brush.tab[0]['image'])

pallet_label = Label(right_frame, text='pallet')
pallet_label.grid(column=0, row=0)
pallet_canvas = Canvas(right_frame, width=240, height=234, borderwidth=0, bg='white')
pallet_canvas.tab = [{} for k in range(0, 512)]
pallet_canvas.grid(column=0, row=1)
pallet_canvas.bind("<B1-Motion>", pallet_canvas_left_click)
pallet_canvas.bind("<Button-1>", pallet_canvas_left_click)
pallet_canvas.bind("<B3-Motion>", pallet_canvas_right_click)
pallet_canvas.bind("<Button-3>", pallet_canvas_right_click)

#buttons

load_button = Button(right_frame, text='load png', command=load_source)
load_button.grid(column=0, row=2, sticky=(EW))

transcode_button = Button(right_frame, text='transcode', command=transcode)
transcode_button.grid(column=0, row=3, sticky=(EW))

load_tymkrscii_button = Button(right_frame, text='load tcipage', command=load_tymkrscii)
load_tymkrscii_button.grid(column=0, row=4, sticky=(EW))

save_button = Button(right_frame, text='save tcipage', command=save_file)
save_button.grid(column=0, row=5, sticky=(EW), columnspan=1)

status_label = Label(right_frame, text='status')
status_label.grid(column=0, row=6, sticky=(NSEW))

for g in range(0, 512):
    x = (g % 30) * 8
    y = int(g / 30) * 13
    pallet_canvas.tab[g]['image'] = PhotoImage(master=pallet_canvas, file='glyphs/' + str(g) + '.png')
    pallet_canvas.create_image(x + 1, y + 1, anchor=NW, image=pallet_canvas.tab[g]['image'])

root.mainloop()

