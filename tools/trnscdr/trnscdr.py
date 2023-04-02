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

screen_buffer = [0] * 960
loaded_file_name = ''

def start_button():
    global loaded_file_name
    if loaded_file_name != '':
        trnscd(loaded_file_name)

def load_button():
    global loaded_file_name
    loaded_file_name = filedialog.askopenfilename(title='Load Source Image', filetypes=[("Image", "*.png")])
    if loaded_file_name:
        pallet.tab[0]['image'] = PhotoImage(master=pallet, file=loaded_file_name)
        pallet.create_image(0, 0, anchor=NW, image=pallet.tab[0]['image'])
        pallet.update()
    else:
        pass #canceled or whatever

def plot_full(file_name):
    for g in range(0, 960):
        plot_chunk(g, load_chunk(loaded_file_name, g))

def plot_chunk(chunk_index, source_greyscale):

    chunk_x = (chunk_index % 30) * 8
    chunk_y = int(chunk_index / 30) * 13

    for y in range(0,13):
        for x in range(0,8):
            if source_greyscale[(y * 8) + x] < 128:
                screen.create_rectangle(x + chunk_x, y + chunk_y, x + chunk_x, y + chunk_y, outline='#444', fill='#444')
    screen.update()

def trnscd(file_name):
    global screen_buffer

    print(file_name)

    x = 0
    y = 0
    i = 0
    pallet.tab[i]['image'] = PhotoImage(master=pallet, file=file_name)
    pallet.create_image(x + 1, y + 1, anchor=NW, image=pallet.tab[i]['image'])

    for chunk_index in range(0, 960):
        screen_buffer[chunk_index] = fit(load_chunk(file_name, chunk_index))
        update_screen()
        screen.update()

def load_chunk(file_name, chunk_index):

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
    for g in range(0, 256):
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

def clear_screen():
    for i in range(0, 960):
        screen_buffer[i] = 0
    update_screen()

def update_screen():
    for i in range(0, 960):
        x = (i % 30) * 8
        y = int(i / 30) * 13
        screen.tab[i]['image'] = PhotoImage(master=screen, file='glyphs/' + str(screen_buffer[i]) + '.png')
        screen.create_image(x + 1, y + 1, anchor=NW, image=screen.tab[i]['image'])

def update_pallet():
    for i in range(0, 960):
        x = (i % 30) * 8
        y = int(i / 30) * 13
        pallet.tab[i]['image'] = PhotoImage(master=pallet, file='glyphs/' + str(screen_buffer[i]) + '.png')
        pallet.create_image(x + 1, y + 1, anchor=NW, image=pallet.tab[i]['image'])

def save_file():
    file = filedialog.asksaveasfilename(title='Save File', filetypes=[("Tymkrs Character Interchange", "*.tci")])

    if file:
        print('saving file ')
        print(file)
        f = open(file, "wb+")
        for i in range(0, 960):
            f.write(screen_buffer[i].to_bytes(1, 'big'))
        f.close()
    else:
        pass #canceled or whatever

def not_load_file():
    file = filedialog.askopenfilename(title='Load File', filetypes=[("Tymkrs Character Interchange", "*.tci")])

    if file:
        print('loading file ')
        print(file)
        f = open(file, "rb")
        for i in range(0, 960):
            screen_buffer[i] = int.from_bytes(f.read(1), 'big')

        f.close()
        update_screen()
    else:
        pass #canceled or whatever

root = Tk()

root.title("Tymkrscii Trnscdr") #Pronounced Tim Kerski

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

#Layout Frame
frame = ttk.Frame(root)
frame.grid(column=1, row=3, columnspan=3, rowspan=2)

#Screen Label
screen_label = Label(frame, text='screen')
screen_label.grid(column=0, row=0)

#Pallet Label
pallet_label = Label(frame, text='source')
pallet_label.grid(column=1, row=0)

#Under Screen
clear_button = Button(frame, text='start', command=start_button)
clear_button.grid(column=0, row=2, sticky=(W))

coord_label = Label(frame, text='?, ?')
coord_label.grid(column=0, row=2)

#Under Pallet
fg_label = Label(frame, text='Brush: ')
fg_label.grid(column=1, row=2, sticky=(W))
fg_brush = Canvas(frame, width=8, height=13, borderwidth=0, bg='white')
fg_brush.tab = [{} for k in range(0, 1)]
fg_brush.grid(column=1, row=2)
fg_brush.tab[0]['image'] = PhotoImage(master=fg_brush, file='glyphs/' + '254' + '.png')
fg_brush.create_image(1, 1, anchor=NW, image=fg_brush.tab[0]['image'])
save_button = Button(frame, text='save', command=save_file)
save_button.grid(column=1, row=2, sticky=(E))

#Under Under Pallet
load_button = Button(frame, text='load', command=load_button)
load_button.grid(column=1, row=3, sticky=(E))

#Screen Canvas
screen = Canvas(frame, width=240, height=416, borderwidth=0, bg='white')
screen.tab = [{} for k in range(0, 960)]
screen.grid(column=0, row=1)

#Pallet Canvas
pallet = Canvas(frame, width=240, height=416, borderwidth=0, bg='white')
pallet.tab = [{} for k in range(0, 256)]
pallet.grid(column=1, row=1)

##
#   main program
##

root.mainloop()
