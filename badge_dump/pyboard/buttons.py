# Copyright (C) 2023 tymkrs
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name of tymkrs shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization from tymkrs.

# button globals
button_action               = [''] * 6
button_active               = [False] * 6
button_next                 = 0

def empty():
    global button_action, button_active, button_next
    print('buttons: removing all button assignments')
    for i in range(0, 6):
            button_action[i] = ''
            button_active[i] = False
    button_next = 0

def add(action):
    global button_action, button_active, button_next
    if button_next < 6:
        print('buttons: adding index: ' + str(button_next) + ' action: ' + action)
        button_action[button_next] = action
        button_active[button_next] = True
        button_next = button_next + 1
        return True
    else:
        print('buttons: can not add, all buttons are already assigned')
        return False

def fill():
    empty()
    print("buttons: refilling buttons[0-5] with actions['0'-'5']")
    for i in range(0, 6):
        add(str(i))
