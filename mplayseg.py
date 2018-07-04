#!/usr/bin/env python
#

import os
import string
import sys

def mmss_to_seconds(s_mmss):
    # mmss = map(int, s_mmss.split(':'))
    mmss = s_mmss.split(':')
    n_segs = len(mmss)
    if n_segs == 2:
        ss = 60*int(mmss[0]) + float(mmss[1])
    elif n_segs == 3:
        # We have hours!
        ss = 3600 * int(mmss[0]) + 60*int(mmss[1]) + float(mmss[2])
    else:
        sys.stderr.write("Error in mmss_to_seconds(%s)\n" % s_mmss)
        sys.exit(1)
    # sys.stderr.write("mmss_to_seconds: s_mmss=%s, ss=%f\n" % (s_mmss, ss))
    return ss


def seconds_to_mmss(seconds):
    # s = "%d:%02d" % (seconds / 60, seconds % 60)
    mm = int(seconds / 60)
    ss = seconds - 60*mm;
    iss = int(ss)
    ss100 = int(100 * (ss - iss) + 0.5)
    s = "%d:%02d.%02d" % (mm, iss, ss100)
    return s
    
    
# debug
if False:
    for x in [1, 120, 0.5, 100.3]:
        sys.stdout.write("x=%f, mmss=%s\n" % (x, seconds_to_mmss(x)))
    sys.exit(7)


# if not len(sys.argv) in (3, 4):
if len(sys.argv) < 2:
    sys.stderr.write(
        "Usage: %s <fn>  <begin time>  [<end time> [mplayer params]]\n" %
        sys.argv[0])
    sys.exit(1)
    
fn = sys.argv[1]
bt = sys.argv[2] if 2 < len(sys.argv) else "0:00"
# et = "99:55" if len(sys.argv) < 4 else sys.argv[3]
et = sys.argv[3] if 3 < len(sys.argv) else "99:55"
ss_b = mmss_to_seconds(bt)
ss_e = mmss_to_seconds(et)
# sys.stderr.write("ss_b: %f, ss_e=%f\n" % (ss_b, ss_e));
t_endpos = ss_e - ss_b
endpos = seconds_to_mmss(t_endpos)
e_params = None
# e_params = os.getenv("MPLAYERSPAR")
if e_params is None:
    e_params = ""
if len(sys.argv) > 4:
    e_params += ' ' + string.join(sys.argv[4:], ' ')
# cmd = "mplayer %s -ss %s -endpos %s %s" % (e_params, bt, endpos, fn)
start = "" if bt == "0:00" else ("--start %s" % bt)
end = "" if et == "99:55" else ("--end %s" % et)
# cmd = "mpv %s --vid=no --start %s -end %s %s" % (e_params, bt, et, fn)
if e_params != ' ':
    if not e_params.startswith(' '):
        e_params = ' ' + e_params
    if not e_params.endswith(' '):
        e_params += ' '
# cmd = "mpv%s--vid=no %s %s %s" % (e_params, start, end, fn)
os.unsetenv('DISPLAY')
cmd = "mpv%s %s %s %s" % (e_params, start, end, fn)
sys.stderr.write("%s\n" % cmd)
rc = os.system(cmd)
sys.exit(rc)
