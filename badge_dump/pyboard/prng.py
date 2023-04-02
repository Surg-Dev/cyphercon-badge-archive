# Copyright (C) 2023 tymkrs
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name of tymkrs shall not be used in advertising or otherwise to promote the sale, use or other dealings in this Software without prior written authorization from tymkrs.

lfsr = []

def new_lfsr():
    global lfsr
    lfsr.append(0)
    return len(lfsr) - 1

def start(index, seed, steps):
    global lfsr
    lfsr[index] = seed
    for i in range(0, steps):
        step(index, 0, 256)
    print('prng: start index: ' + str(index) + ' seed: ' + str(seed) + ' steps: ' + str(steps) + ' lfsr[index]: ' + str(lfsr[index]))

def step(index, lower, upper):
    global lfsr
    #taps: 16 15 13 4; feedback polynomial: x^16 + x^15 + x^13 + x^4 + 1
    bit = (lfsr[index] ^ (lfsr[index] >> 1) ^ (lfsr[index] >> 3) ^ (lfsr[index] >> 12)) & 1
    lfsr[index] = (lfsr[index] >> 1) | (bit << 15)
    if upper <= lower: upper = lower + 1
    value = (lfsr[index] % (upper - lower)) + lower
    #print('prng: index: ' + str(index) + ' lfsr ' + str(lfsr[index]) + ' value: ' + str(value)) # spammy
    return value
