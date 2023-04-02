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

import random

screen_buffer = [0] * 960
brush_index = 0

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

def update_coords(event):
    i = (int((event.x - 1) / 8) % 30) + (int((event.y - 1) / 13) * 30)
    if i < 960:
        coord_label.config(text = str(event.x) + ', ' + str(event.y) + ' : ' + str(i) + ' = ' + str(screen_buffer[i]))

def screen_leftclick(event):
    i = (int((event.x - 1) / 8) % 30) + (int((event.y - 1) / 13) * 30)
    if i < 960:
        screen_buffer[i] = brush_index
        update_screen()

def savePosn(event):
    global lastx, lasty
    lastx, lasty = event.x, event.y

def addLinePallet(event):
    g = (int((event.x - 1) / 8) % 30) + (int((event.y - 1) / 13) * 30)
    if g < 256:
        fg_brush.tab[0]['image'] = PhotoImage(master=fg_brush, file='glyphs/' + str(g) + '.png')
        fg_brush.create_image(1, 1, anchor=NW, image=fg_brush.tab[0]['image'])
        global brush_index
        brush_index = g
    savePosn(event)

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

def save_tymkrscii_page_file():
    global glyph, background, foreground

    working_buffer = screen_buffer
    file = filedialog.asksaveasfilename(title='Save File', filetypes=[("Tymkrscii Page File", "*.tcipage")])
    if file:
        print('saving file ')
        print(file)
        f = open(file, "wb+")
        mode0_header = [0x54, 0x59, 0x4d, 0x4b, 0x52, 0x53, 0x43, 0x49, 0x49, 0x01, 0x1e, 0x20, 0x00, 0x00, 0x00, 0x00]

        # Write Header section to the file
        for i in range(0, 16):
            f.write(mode0_header[i].to_bytes(1, 'big'))

        # Write Data section to the file
        for i in range(0, 960):
            f.write(screen_buffer[i].to_bytes(1, 'big'))

        f.close()

    else:
        pass #canceled or whatever

def load_file():
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

def addLineScreen(event):
    g = random.randrange(0, 960, 1)
    x = (g % 30) * 8
    y = int(g / 30) * 13
    screen.tab[g]['image'] = PhotoImage(master=screen, file='glyphs/' + str(random.randrange(0, 256, 1)) + '.png')
    screen.create_image(x + 1, y + 1, anchor=NW, image=screen.tab[g]['image'])

root = Tk()

root.title("Tymkrscii Draw") #Pronounced Tim Kerski

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

#Layout Frame

frame = ttk.Frame(root)
frame.grid(column=1, row=3, columnspan=3, rowspan=2)

#Screen Label

screen_label = Label(frame, text='screen')
screen_label.grid(column=0, row=0)

#Pallet Label

pallet_label = Label(frame, text='pallet')
pallet_label.grid(column=1, row=0)

#Under Screen

clear_button = Button(frame, text='clear', command=clear_screen)
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

save_button = Button(frame, text='save v1', command=save_tymkrscii_page_file)
save_button.grid(column=1, row=2, sticky=(E))

#Under Under Pallet

load_button = Button(frame, text='load', command=load_file)
load_button.grid(column=1, row=3, sticky=(E))

old_save_button = Button(frame, text='save v0', command=save_file)
old_save_button.grid(column=0, row=3, sticky=(E))

#Screen Canvas

screen = Canvas(frame, width=240, height=416, borderwidth=0, bg='white')
screen.tab = [{} for k in range(0, 960)]
screen.grid(column=0, row=1)
screen.bind("<Button-1>", screen_leftclick)
screen.bind("<B1-Motion>", screen_leftclick)
screen.bind("<Motion>", update_coords)

#Pallet Canvas

pallet = Canvas(frame, width=240, height=416, borderwidth=0, bg='white')
pallet.tab = [{} for k in range(0, 256)]
pallet.grid(column=1, row=1)
pallet.bind("<B1-Motion>", addLinePallet)
pallet.bind("<Button-1>", addLinePallet)

for g in range(0, 256):
    x = (g % 30) * 8
    y = int(g / 30) * 13
    pallet.tab[g]['image'] = PhotoImage(master=pallet, file='glyphs/' + str(g) + '.png')
    pallet.create_image(x + 1, y + 1, anchor=NW, image=pallet.tab[g]['image'])

root.mainloop()
