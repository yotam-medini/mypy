#!/usr/bin/env python
#
# Convert instruments of midi file  using midi package

import os
import sys
import string
sys.path.append(os.getenv("HOME") + "/pyother/midi")
import MidiInFile
import MidiOutFile

MOF = MidiOutFile.MidiOutFile

note12 = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
def note_name(n):
    name = note12[n % 12]
    octave = (n / 12) - 5
    if octave < 0:
        name += ("%d" % octave)
    elif octave > 0:
        name += ("+%d" % octave)
    return name


class Conv(MOF):

    def __init__(self, conv_prog, fn):
        MOF.__init__(self, fn)
        self.conv_prog = conv_prog
        self.stat_nTracks = 0
        self.stat_trackNames = {}
        self.track_current = -1
        self.ab_default = self.conv_prog.tv.get(-1, (1, 0))
        self.last_track = -1
        self.last_velocity = -1
        self.n_notes = -1
        self.connect_i = 0
        self.connecting = False
        self.connect_time = 0
        self.connect_velocity = 0

    def update_time(self, new_time=0, relative=1):
        self.mlog("update_time",
                  "new_time=%d, relative=%d" % (new_time, relative))
        if self.connecting:
            self.dlog("update_time: new_time=%d, relative=%d, ct=%d ..." %
                      (new_time, relative, self.connect_time))
            if relative == 1:
                self.connect_time += new_time
            self.dlog("... ct=%d" % self.connect_time)
        else:
            MOF.update_time(self, new_time, relative)

    def event_slice(self, slc):
        sslc = str(slc)
        xslc = ""
        for c in sslc:
            xslc += ("%02x" % ord(c))
        self.mlog("event_slice",
                  "slc[%d]=%s, rel_time=%d" %
                  (len(slc), xslc, self.rel_time()))
        MOF.event_slice(self, slc)

    def note_on(self, channel=0, note=0x40, velocity=0x40):
        self.n_notes += 1
        self.mlog("note_on",
                  "note=%d, channel=%d, note=%d (%s), velocity=0x%x" %
                  (self.n_notes, channel, note, note_name(note), velocity))
        note += self.conv_prog.K
        note = self.conv_prog.override.get(self.n_notes, note)
        xvelocity = self.velocity_xform(velocity)
        c = self.conv_prog.connect
        ci = self.connect_i
        if (ci < len(c)) and (c[ci][0] == self.n_notes):
            self.connecting = True
            self.connect_time = 0
            self.connect_velocity = velocity
        if self.connecting:
            self.dlog("note_on: Connecting ... note=%d" % self.n_notes)
            self.connect_velocity = max(self.connect_velocity, velocity)
        else:
            MOF.note_on(self, channel, note, xvelocity) # calls event_slice

    def note_off(self, channel=0, note=0x40, velocity=0x40):
        self.mlog("note_off", "channel=%d, note=0%d (%s), velocity=0x%x" %
                  (channel, note, note_name(note), velocity))
        note += self.conv_prog.K
        note = self.conv_prog.override.get(self.n_notes, note)
        xvelocity = self.velocity_xform(velocity)
        c = self.conv_prog.connect
        ci = self.connect_i
        if self.connecting:
            if self.n_notes == c[ci][1]:
                self.connecting = False
                velocity = self.connect_velocity
                self.dlog("Connection: c=%d, n=%d (%s), v=0x%x t=%d" %
                      (channel, note, note_name(note), velocity,
                       self.connect_time))
                MOF.note_on(self, channel, note, velocity) # calls event_slice
                MOF.update_time(self, self.connect_time, 1)
                MOF.note_off(self, channel, note, xvelocity) # calls event_slice
                MOF.update_time(self, 0, 1)
                self.connect_i += 1
                self.connect_time = 0
            self.dlog("note_off: Connecting ... note=%d" % self.n_notes)
        else:
            MOF.note_off(self, channel, note, xvelocity) # calls event_slice

    def aftertouch(self, channel=0, note=0x40, velocity=0x40):
        self.mlog("aftertouch", "channel=%d, note=0x%x, velocity=0x%x" %
                  (channel, note, velocity))
        MOF.aftertouch(self, channel, note, velocity)

    def continuous_controller(self, channel, controller, value):
        self.mlog("continuous_controller",
                  "channel=%d, controller=%d, value=%d" %
                  (channel, controller, value))
        MOF.continuous_controller(self, channel, controller, value)

    def patch_change(self, channel, patch):
        track = channel + 1 # Why o why !?
        self.mlog("patch_change", "channel=%d, patch=%d" % (channel, patch))
        new_patch = self.conv_prog.px.get(track, self.conv_prog.pdefault)
        if not new_patch is None:
            self.log("channel[%d] patch %d -> patch=%d" %
                      (channel, patch, new_patch))
            patch = new_patch
        MOF.patch_change(self, channel, patch)

    def channel_message(self, message_type, channel, data):
        self.mlog("channel_message",
                  "mt=%s, chan=%s, data=%s" % (message_type, channel, data))
        MOF.channel_message(self, message_type, channel, data)

    def channel_pressure(self, channel, pressure):
        self.mlog("channel_pressure",
                  "channel=%d, pressure=%d" % (channel, patch))
        MOF.channel_pressure(self, channel, pressure)

    def pitch_bend(self, channel, value):
        self.mlog("pitch_bend", "channel=%d, value=%d" % (channel, value))
        MOF.pitch_bend(self, channel, value)

    def system_exclusive(self, data):
        self.mlog("system_exclusive", "data=" % str(data))
        MOF.system_exclusive(self, data)

    def midi_time_code(self, msg_type, values):
        self.mlog("midi_time_code",
                  "msg_type=%d, values=%d" % (msg_type, values))
        MOF.midi_time_code(self, msg_type, values)

    def song_position_pointer(self, value):
        self.mlog("song_position_pointer", "value=" % value)
        MOF.song_position_pointer(self, value)

    def song_select(self, songNumber):
        self.mlog("song_select", "songNumber=%d" % songNumber)
        MOF.song_select(self, songNumber)

    def tuning_request(self):
        self.mlog("tuning_request")
        MOF.tuning_request(self)

    def header(self, format, nTracks, division):
        self.stat_nTracks = nTracks
        self.mlog("header", "format=%d, nTracks=%d, division=%d" %
                 (format, nTracks, division))
        MOF.header(self, format, nTracks, division)

    def eof(self):
        self.mlog("eof")
        MOF.eof(self)

    def meta_event(self, meta_type, data):
        self.mlog("meta_event",
                  "meta_type=%d, data=%s" % (meta_type, str(data)))
        MOF.meta_event(self, meta_type, data)

    def start_of_track(self, n_track=0):
        self.mlog("start_of_track", "n_track=%s" % n_track)
        self.stat_trackNames[n_track] = "??"
        self.track_current = n_track
        MOF.start_of_track(self, n_track)
        self.dlog("start_of_track: _current_track=%d" % self._current_track)
        

    def end_of_track(self):
        self.mlog("end_of_track")
        MOF.end_of_track(self)

    def sequence_number(self, value):
        self.mlog("sequence_number", "value=%d" % value)
        MOF.sequence_number(self, value)

    def text(self, text):
        self.mlog("text", text)
        MOF.text(self, text)

    def copyright(self, text):
        self.mlog("copyright", "text=%s" % text)
        MOF.copyright(self, text)

    def sequence_name(self, text):
        self.mlog("sequence_name", "text=%s" % text)
        self.stat_trackNames[self.track_current] = text
        MOF.sequence_name(self, text)

    def instrument_name(self, text):
        self.mlog("instrument_name", "text=%s" % text)
        self.stat_trackNames[self.track_current] = text
        MOF.instrument_name(self, text)

    def lyric(self, text):
        self.mlog("lyric", "text=%s" % text)
        # self.stat_trackNames[self.track_current] = text
        MOF.lyric(self, text)

    def marker(self, text):
        self.mlog("marker", "text=%s" % text)
        self.stat_trackNames[self.track_current] = text
        MOF.marker(self, text)

    def cuepoint(self, text):
        self.mlog("cuepoint", "text=%s" % text)
        self.stat_trackNames[self.track_current] = text
        MOF.cuepoint(self, text)

    def midi_ch_prefix(self, channel):
        self.mlog("midi_ch_prefix", "channel=%d" % channel)
        MOF.midi_ch_prefix(self, channel)
            
    def midi_port(self, channel):
        self.mlog("midi_port", "channel=%d" % channel)
        MOF.midi_port(self, channel)
            
    def tempo(self, value):
        self.mlog("tempo", "value=%d" % value)
        MOF.tempo(self, value)

    def smtp_offset(self, hour, minute, second, frame, framePart):
        self.mlog("smtp_offset",
                  "hour=%d, minute=%d, second=%d, frame=%d, framePart=%d,"
                  (hour, minute, second, frame, framePart))
        MOF.smtp_offset(self, hour, minute, second, frame, framePart)
        
    def time_signature(self, nn, dd, cc, bb):
        self.mlog("time_signature", "nn=%d, dd=%d, cc=%d, bb=%d" %
                  (nn, dd, cc, bb))
        MOF.time_signature(self, nn, dd, cc, bb)

    def key_signature(self, sf, mi):
        self.mlog("key_signature", "sf=%d, mi=%d" % (sf, mi))
        MOF.key_signature(self, sf, mi)

    def sequencer_specific(self, data):
        self.mlog("sequencer_specific", "Len=%d, data=%s" %
                  (len(data), str(data)))
        # MOF.sequencer_specific(self, data)


    def stats_write(self, f=sys.stdout):
        f.write("nTracks=%d\n" % self.stat_nTracks)
        tracks = self.stat_trackNames.items()
        if False:
            for i in range(len(tracks)):
                track = tracks[i]
                f.write("track[%d] = '%s'\n" % (i, track))
                f.write("dir(track)=%s, type=%s\n" % (dir(track), type(track)))
                f.write("len(track)=%d\n" % len(track))
        for item in self.stat_trackNames.items():
            f.write("track[%d] = '%s'\n" % item)

         
    def velocity_xform(self, v):
        tv = self.conv_prog.tv
        a, b = self.conv_prog.tv.get(self.track_current, self.ab_default)
        xv = int(a*v) + b
        xv = max(0, min(xv, 0x7f))
        if ((self.last_track != self.track_current) or
            (self.last_velocity != v)):
            self.last_track = self.track_current
            self.last_velocity = v
            self.mlog("velocity_xform", "track=%d: velocity: %d --> %d" %
                      (self.track_current, v, xv))
        return xv
            
        
    def mlog(self, method, msg=""):
        if self.conv_prog.log_all or method in self.conv_prog.log_methods:
            self.dlog("%s: %s" % (method, msg))

    def log(self, msg):
        sys.stderr.write("%s\n" % msg)
        pass

    def dlog(self, msg):
        sys.stderr.write("%s\n" % msg)
        pass

    def dlog0(self, msg):
        pass
        

class ConvProg:

    def usage(self):
        sys.stderr.write(
"""
Usage:
  %s
    [-h | -help | --help]  # This message
    [-pdefault <n>]        # Default program index (instrument)
    [-px <m:n>]            # program[channel m] := n (repeatable)
    [-K <n>]               # shift <n> half notes
    [-tv <n> <a> <b>]      # Change velocity for track <n>, V := aV + b
                           # (n = -1 all other tracks) Repeatable
                           # Default: a=1 b=0
    [-note <m> <n>]        # Force the <m>-th note to be <n>
    [-connect <m1> <m2>    # Connect <m1>-th till <m2>-th motes
    [-mlog <metjods>]      # Comma separated method names or 'all'
  <in midi> <out midi>
""" % self.argv[0])


    def __init__(self, argv):
        self.rc = 0
        self.argv = argv
        ai = 1
        self.pdefault = None
        self.px = {}
        self.tv = {}
        self.log_methods = set()
        self.log_all = False
        self.K = 0
        self.override = {}
        self.connect = []
        while self.ok() and ai < len(argv) and argv[ai][0] == '-':
            opt = argv[ai]
            ai += 1
            if opt in ('-h', '-help', '--help'):
                self.usage()
                sys.exit(0)
            if opt == '-pdefault':
                self.pdefault = int(argv[ai])
                ai += 1
            elif opt == '-K':
                self.K = int(argv[ai])
                ai += 1
            elif opt == '-px':
                (old, new) = map(int, string.split(argv[ai], ':'))
                self.px[old] = new
                ai += 1
            elif opt == '-tv':
                self.tv[int(sys.argv[ai])] = (
                    float(sys.argv[ai+1]), int(sys.argv[ai+2]))
                ai += 3
            elif opt == '-note':
                self.override[int(sys.argv[ai])] = int(sys.argv[ai + 1])
                ai += 2
            elif opt == '-connect':
                self.connect.append((int(sys.argv[ai]), int(sys.argv[ai + 1])))
                ai += 2
            elif opt == '-mlog':
                if argv[ai] == 'all':
                    self.log_all = True
                else:
                    self.log_methods = set(string.split(argv[ai], ','))
                methods = argv[ai]
                ai += 1
            else:
                sys.stderr.write("Bad option: %s\n" % opt)
        if len(argv) != ai + 2:
            self.usage()
            sys.exit(1)
        self.connect.sort()
        self.ifn = sys.argv[ai]
        self.ofn = sys.argv[ai + 1]


    def run(self):
        midi_out = Conv(self, self.ofn)
        midi_in = MidiInFile.MidiInFile(midi_out, self.ifn)
        midi_in.read()
        midi_out.stats_write()


    def ok(self):
        return self.rc == 0
    

if __name__ == '__main__':
    p = ConvProg(sys.argv)
    if p.ok():
        p.run()
    sys.exit(p.rc)
