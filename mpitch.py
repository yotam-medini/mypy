#!/usr/bin/env python
#  Author:  Yotam Medini  yotam.medini@gmail.com -- Created: 2018/March/24
import math
import os
import sys
import textwrap

def vlog(msg):
    sys.stderr.write('%s\n' % msg)
    
def usage(a0):
    sys.stderr.write(textwrap.dedent("""
    Usage:
       %s <fnin> <fnout> <change>
    Where:
       pitch is frequency factor. Using '/' is an option.
    """))

def fatal(msg, rc=1):
    vlog(msg)
    usage(sys.argv[0])
    sys.exit(rc)

def syscmd(cmd):
    vlog(cmd)
    rc = os.system(cmd)
    if rc != 0:
        fatal('Failed: %s', rc)

if __name__ == '__main__':
    if len(sys.argv) != 1 + 3:
        fatal('')

    fnin = sys.argv[1]
    fnout = sys.argv[2]
    change = sys.argv[3]
    if '/' in change:
        ss = change.split('/')
        change = float(ss[0]) / float(ss[1])
    else:
        change = float(change)
    # vlog('change=%g' % change)
    half_tone = 2. ** (1./12.)
    sox_change = 100 * math.log(change) / math.log(half_tone)
    vlog('change=%g, sox_change=%g' % (change, sox_change))
    # sys.exit(13)
    scrwav0 = '/tmp/mpitch-0.wav'
    scrwav1 = '/tmp/mpitch-1.wav'
    for fn in scrwav0, scrwav1:
        vlog('unlink %s' % fn)
        try:
            os.unlink(fn)
        except Exception as e:
            vlog(str(e))
    syscmd('avconv -i %s %s' % (fnin, scrwav0))
    syscmd('sox %s %s pitch %g' % (scrwav0, scrwav1, sox_change))
    syscmd('lame %s %s' % (scrwav1, fnout))
    sys.exit(0)
