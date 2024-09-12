#!/usr/bin/env python

import glob
import os
import sys
import time

# musicfn = "4b-BeetSym9Karajan.mp3"

def vlog(msg):
    sys.stderr.write("%s\n" % msg)

def run(cmd):
    vlog("%s" % cmd)
    rc = os.system(cmd)
    if rc != 0:
        vlog("Error: rc=0x%x" % rc)
        sys.exit(rc)


class Segment:
    def __init__(self, p, musicfn, comment, tb, te=None, seg=None):
        self.p = p
        if not os.path.exists(musicfn):
            fns = glob.glob(musicfn)
            if len(fns) == 1:
                musicfn = fns[0]
        self.musicfn = musicfn
        self.comment = comment
        self.tb = tb
        self.te = te
        self.seg = seg

    def play(self, segi, period=0, sleep=3):
        vlog(64*'=' + "\n\n")
        vlog("Playing: [%2d] %s" % (segi, self.comment))
        player_params = "??"
        if sleep > 0:
            sys.stderr.write("sleep(%d)\n" % sleep)
            time.sleep(sleep)
        if self.musicfn.endswith(".mp3") or self.musicfn.endswith(".mov"):
            player_params = (self.p.live_player_params
                if self.musicfn.endswith(".mp3") else self.p.video_player_params)
            if self.p.av or self.tb.find(':') < 0:
                if self.te is None:
                    run("aplayseg.py %s %s" % (self.musicfn, self.tb))
                else:
                    run("aplayseg.py %s %s %s" %
                        (self.musicfn, self.tb, self.te))
            else:
                # run("mplayseg.py %s %s %s %s" % 
                #     (self.musicfn, self.tb, self.te, player_params))
                run(f'mpv --start={self.tb} --end={self.te} {player_params} {self.musicfn}')
        elif self.seg:
            player_params = self.p.midi_player_params
            pp_pad = " " if player_params == "" else (" %s " % player_params)
            run("timiseg%s-idt --segment %s %s" % 
                (pp_pad, self.seg, self.musicfn))
        else:
            run("timiticks %s --ticks %s:%s:%d %s" % 
                (player_params, self.tb, self.te, period, self.musicfn))

    def __str__(self):
        if self.seg:
            s = '"%s"  [%s]' % (self.comment, self.seg)
        else:
            s = '"%s"  [%s -> %s]' % (self.comment, self.tb,
                                      ("" if self.te is None else self.te))
        return s


class PSegs:

    def usage(self):
        vlog("""
Usage: 
  %s 
    -i <data-filename>
    [-pp <player_params>] # any
    [-lpp <player_params>] # live-audio
    [-mpp <player_params>] # midi
    [-sleep <seconds>]
    [-period <n>]
    [-av]                  # Use avplay instead of mplayer
    [sbegin send] [seg]
"""
             % self.argv[0])
        for si in range(len(self.segs)):
            seg = self.segs[si]
            vlog(" [%2d] %s" % (si, seg))
        sys.exit(1)


    def __init__(self, argv):
        self.rc = 0
        self.argv = argv
        self.musicfn = ""
        self.segs = []
        self.player_params = ""
        self.live_player_params = ""
        self.video_player_params = ""
        self.midi_player_params = ""
        self.ticks_period = 0
        self.sleep_seconds = 3
        self.any_midi = False
        self.av = False
        ai = 1
        while ai < len(sys.argv) and self.argv[ai][0] == '-':
            opt = sys.argv[ai]
            if opt == "-i":
                ai += 1
                self.data_read(sys.argv[ai])
            elif opt == "-pp":
                ai += 1
                self.player_params = sys.argv[ai]
            elif opt == "-lpp":
                ai += 1
                self.live_player_params = sys.argv[ai]
            elif opt == "-vpp":
                ai += 1
                self.video_player_params = sys.argv[ai]
            elif opt == "-mpp":
                ai += 1
                self.midi_player_params = sys.argv[ai]
            elif opt == "-period":
                ai += 1
                self.ticks_period = int(sys.argv[ai])
            elif opt == "-sleep":
                ai += 1
                self.sleep_seconds = int(sys.argv[ai])
            elif opt == "-av":
                self.av = True
            else:
                vlog("Bad option: %s" % opt)
                self.usage()
            ai += 1

        if ai >= len(sys.argv):
            self.usage()
        self.nums = list(map(int, self.argv[ai:]))


    def data_read(self, fn):
        lines = open(fn, "r").readlines()
        li = 0
        musicfn = None
        segs = []
        while li < len(lines) and musicfn is None:
            line = lines[li]
            ss = line.split()
            si = 0 
            while si < len(ss) and musicfn is None:
                ext = ss[si].split(".")[-1]
                if ext in ("mp3", "mid", "midi", "MID", "MIDI"):
                    musicfn = ss[si]
                    self.any_midi = True
                si += 1
            li += 1
        for line in lines[li:]:
            colon = -1 if line.startswith("#") else line.find(": ")
            if colon > 0:
                # comment = "[%2d] %s" % (len(segs), line[:colon].strip())
                # comment = "%s" % (line[:colon].strip())
                comment = line[:colon]
                ss = line[colon + 1:].split()
                if len(ss) == 2:
                    dash = ss[1].find("-")
                    comma = ss[1].find(",")
                    if dash >= 0 or comma >= 0:
                        seg = Segment(self, ss[0], comment, None, None, ss[1])
                    else:
                        # seg = Segment(self, musicfn, comment, ss[0], ss[1])
                        seg = Segment(self, ss[0], comment, ss[1], None)
                    segs.append(seg)
                elif len(ss) == 3:
                    segs.append(Segment(self, ss[0], comment, ss[1], ss[2]))
        # self.musicfn = musicfn
        self.segs = segs


    def run(self):
        if self.player_params != "":
            if self.live_player_params == "":
                self.live_player_params == self.player_params
            if self.midi_player_params == "":
                self.midi_player_params == self.player_params
        nums = self.nums
        ab = 0
        ae = 1
        sleep = 0
        while ae < len(nums):
            for si in range(nums[ab], nums[ae]):
                self.play(si, sleep)
                sleep = self.sleep_seconds
            ab += 2
            ae += 2

        if ab < len(nums):
            self.play(nums[ab], 0)
            if self.any_midi:
                sys.stderr.write("\n")


    def play(self, segi, sleep):
        self.segs[segi].play(segi, self.ticks_period, sleep)



p = PSegs(sys.argv)
p.run()
sys.exit(p.rc)
