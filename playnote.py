#!/usr/bin/env python

import os
import sys
import time

def vlog(msg):
    sys.stderr.write('%s\n' % msg)

def step2mult(n):
    return (2. ** (n/12.))

rc = 0
amult = {
    'b': step2mult(2),
    'as': step2mult(1),
    'a': step2mult(0),
    'gs': step2mult(-1),
    'g': step2mult(-2),
    'fs': step2mult(-3),
    'f': step2mult(-4),
    'e': step2mult(-5),
    'ds': step2mult(-6),
    'd': step2mult(-7),
    'cs': step2mult(-8),
    'c': step2mult(-9),
}

amult['af'] = amult['gs']
amult['bf'] = amult['as']
amult['df'] = amult['cs']
amult['ef'] = amult['ds']
amult['gf'] = amult['fs']

t = 0.2
gap = 0
note = 'a'
afreq = 440
vol = 0.1

ai = 1
while ai < len(sys.argv) and sys.argv[ai][0] == '-':
    opt = sys.argv[ai]
    if opt == '-t':
        ai += 1
        t = float(sys.argv[ai])
    elif opt == '-A':
        ai += 1
        afreq = int(sys.argv[ai])
    elif opt == '-s':
        ai += 1
        gap = float(sys.argv[ai])
    elif opt == '-v':
        ai += 1
        vol = float(sys.argv[ai])
    ai += 1
if ai == len(sys.argv):
    tune = [note]
else:
    tune = sys.argv[ai:]

nap = 0
oct_mult = 1
for note in tune:
    time.sleep(nap); nap = gap
    digit = note[-1]
    if digit in '0123456789':
        oct_mult = 2 ** (int(digit) - 4)
        note = note[:-1]
    f = oct_mult * afreq * amult[note]
    cmd = 'play -n synth %g sin %g vol %g 2>/dev/null' % (t, f, vol)
    vlog(cmd)
    os.system(cmd)
    time.sleep(0.005)

sys.exit(rc)
