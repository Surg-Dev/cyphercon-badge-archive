# Copyright (C) 2023 tymkrs
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name of tymkrs shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization from tymkrs.

counter = []
threshold = []

def start(new_threshold):
    global counter, threshold
    counter.append(0)
    threshold.append(new_threshold)
    print('counters: started a new counter index: ' + str(len(threshold) - 1) + ' threhold: ' + str(new_threshold))
    return len(threshold) - 1

def restart(index, new_threshold):
    global counter, threshold
    threshold[index] = new_threshold
    counter[index] = 0

def reset(index):
    #print('counters: reset counter index: ' + str(index)) #can get spammy so leaving it off
    counter[index] = 0

def count(index): # increments counter, resets and returns True if threshold tripped
    global counter, threshold
    counter[index] = counter[index] + 1
    if counter[index] > threshold[index]:
        #print('counters: counter #' + str(index) + ' tripped') #can get spammy so leaving it off
        reset(index)
        return True
    return False

def apply_delta(index, delta):
    global counter
    counter[index] = calc_relative_position(index, delta)

def calc_relative_position(index, delta):
    relative_position = counter[index] + delta
    if relative_position < 0:
        relative_position = relative_position + threshold[index]
    elif relative_position >= threshold[index]:
        relative_position = relative_position - threshold[index]
    return relative_position
