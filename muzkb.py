#!/usr/bin/env python3
#

import fractions
import os
import pprint
import sys
import textwrap

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
import cairo


def elog(msg):
    sys.stderr.write('%s\n' % msg)

def fatal(msg):
    elog('Fatal %s' % msg)
    sys.exit(1)

def safe_int(s, defval=None):
    try:
        ret = int(s)
    except:
        ret = defval
    return ret

class Segment:
    def __init__(self, xb, xe):
        self.xb = xb
        self.xe = xe
    def size(self):
        return self.xe - self.xb
    def __str__(self):
        return '[%d, %d)' % (self.xb, self.xe)

class Locator:

    KEY_NONE = -1
    KEY_UNDEFINED = -2

    class Key:
        def __init__(self, note, inner, outer):
            self.note = note
            self.inner = inner
            self.outer = outer
        def inner_width(self):
            return self.inner.size()
        def outer_width(self):
            return self.outer.size()
        def x_inside(self, x):
            return self.inner.xb <= x < self.inner.xe
        def __str__(self):
            return '{Key(%d, inner=%s, outer=%s}' % (
                self.note, self.inner, self.outer)

    def __init__(self, w, h, note_low, note_high):
        self.w = w
        self.h = h
        self.note_low = note_low
        self.note_high = note_high
        self.allocate()

    def black_height(self):
        return 2*self.h//3

    def __str__(self):
        return '%s(wh=%dx%d, [%d,%d])' % (self.__class__.__name__,
            self.w, self.h, self.note_low, self.note_high)

    def note_is_white(self, note):
        return (note % 12) in [0, 2, 4, 5, 7, 9, 11]

    def note_is_black(self, note):
        return not self.note_is_white(note)

    def allocate(self):
        # Consider (front) width white-key = 1
        # b = black key width
        # w1 = white-back-width C,D,E
        # w2 = white-back-width F,G,A,B
        #   3w1 + 2b = 3  ==>   w1 = -2b/3 + 1
        #   4w2 + 3b = 4  ==>   w2 = -3b/4 + 1
        #   Assuming b > 0, since 3/4 > 2/3, so w1 > w2.
        #   So we will requre  (w1 - b) = (b - w2)
        #   -5b/3 + 1 = 7b/4 - 1   ==>  (7/4 + 5/3)b = 2   ==>  b = 24/41

        self.low_white = self.note_low
        self.high_white = self.note_high
        if self.note_is_black(self.low_white):
            self.low_white += 1
        if self.note_is_black(self.high_white):
            self.high_white -= 1
        n_whites = self.n_whites_in(self.low_white, self.high_white)
        elog('n_whites=%d' % n_whites)
        self.white_outer_width = self.w // n_whites
        self.black_outer_width = (24*self.white_outer_width + 20) // 41
        white_space = max(self.white_outer_width // 32, 1)
        black_space = max(self.black_outer_width // 32, 1)

        self.keys = []
        self.white_keys = []
        self.black_keys = []
        for note in range(self.note_low, self.note_high + 1):
            if self.note_is_white(note):
                wi = len(self.white_keys)
                xl = (wi * self.w + n_whites//2) // n_whites
                xr = xl + self.white_outer_width
                key = Locator.Key(
                    note,
                    Segment(xl + white_space, xr - white_space),
                    Segment(xl, xr))
                self.white_keys.append(key)
            else:
                if note == self.note_low:
                    xr = self.black_outer_width // 2
                    key = Locator.Key(
                        note, Segment(0, xr - black_space), Segment(0, xr))
                else:
                    penta = note % 12
                    pre_white = self.white_keys[-1].outer.xe
                    q = {
                        1: (2, 3), # C#=Db
                        3: (1, 3), # D#=Ef
                        6: (3, 4), # F#=Gb
                        8: (1, 2), # G#=Ab
                        10: (1, 4)  # A#=Bb
                    }[penta]
                    xl = pre_white - (
                        q[0] * self.black_outer_width + (q[1]//2)) // q[1]
                    xl_inner = xl + black_space
                    xr = xl + self.black_outer_width
                    xr_inner = xr - black_space
                    if xr >= self.w:
                        xr = xr_inner = self.w
                    key = Locator.Key(note,
                        Segment(xl_inner, xr_inner), Segment(xl, xr))
                self.black_keys.append(key)
            self.keys.append(key)

    def n_whites_in(self, low_white, high_white):
        n = high_white - low_white
        octaves = n // 12
        inoct_low = low_white % 12
        inoct_high = high_white % 12
        swap = inoct_high < inoct_low
        if swap:
            t = inoct_low; inoct_low = inoct_high; inoct_high = t;
        n_inoct = (inoct_high - inoct_low)//2 + 1
        if (inoct_low <=4) and (inoct_high >= 5):
            n_inoct += 1
        if swap:
            n_inoct = 9 - n_inoct
        n_whites = 7*octaves + n_inoct
        return n_whites
        
    def pick(self, x, y):
        bnote = -1
        wnote = self.pick_from(self.white_keys, x)
        if y < self.black_height():
            bnote = self.pick_from(self.black_keys, x)
        ret = bnote if bnote > 0 else wnote
        return ret

    def pick_from(self, keys, x):
        note = -1
        li = 0
        hi = len(keys) - 1
        elog('li=%d, hi=%d' % (li, hi))
        while (note == -1) and (li <= hi):
            mid = (li + hi) // 2
            key = keys[mid]
            if key.x_inside(x):
                note = key.note
            elif x < key.inner.xb:
                hi = mid - 1
            else:
                li = mid + 1
        return note

    def fprint(self, f=sys.stdout):
        f.write(
            '{ w=%d, {outer_widths: W=%d, B=%d},'
            ' #(White)=%d, #(Black)=%d\n' %
            (self.w, self.white_outer_width, self.black_outer_width,
            len(self.white_keys), len(self.black_keys)))
        for key in self.keys:
            note = key.note
            f.write('%s%s\n' %
                (('' if self.note_is_white(note) else '    '), key))
        f.write('}\n')


def locator_test(argv):
    nums = list(map(int, argv))
    locator = Locator(nums[0], nums[1], nums[2], nums[3])
    elog('locator= %s' % locator)
    locator.fprint()
    tail = nums[4:]
    xys = list(zip(tail[0::2], tail[1::2]))
    for (x, y) in xys:
        elog('pick(%d, %d) = %d' % (x, y, locator.pick(x, y)))
    return 0


note_name = []
name_note = {}
def _fill_notes_names():
    snames = ['c', 'cs', 'd', 'ds', 'e', 'f', 'fs', 'g', 'gs', 'a', 'as', 'b']
    fnames = ['c', 'db', 'd', 'ef', 'e', 'f', 'gf', 'g', 'af', 'a', 'bf', 'b']
    for note in range(0*12, 8*12 + 1):
        n = note % 12
        octave = note // 12 - 1
        sname = '%s%d' % (snames[n], octave)
        fname = '%s%d' % (fnames[n], octave)
        note_name.append(sname)
        name_note[sname] = note
        name_note[fname] = note
_fill_notes_names()
# elog('note_name=%s' % pprint.pformat(note_name))
# elog('name_note=%s' % pprint.pformat(name_note))

def name_of_note(s):
    if type(s) is int:
        s = note_name[s]
    return s

def number_of_note(ns):
    n = safe_int(ns)
    if n is None:
        n = name_note[ns]
    return n

class Defaults:
    window_size = (1200, 600)
    note_low = 'c3'
    note_high = 'c5'
    volume = 0.2
    duration = 0.2
    pitch_note = 'a'
    pitch_frequency = 440
    tuning_base = 'd4'


class Tuning:

    def __init__(self, note_ref, frequeny_ref):
        self.note_ref = note_ref
        self.frequeny_ref = frequeny_ref

    def note_frequency(self, note):
        f = self.middle_note_frequency(note % 12)
        octave = note // 12 - 5
        f *= (2. ** octave)
        return f

    def middle_note_frequency(self, note):
        return None

class EqualTempered(Tuning):

    def __init__(self, note_ref, frequeny_ref):
        super().__init__(note_ref % 12, frequeny_ref)

    def middle_note_frequency(self, note):
        a = 2. ** ((note - self.note_ref)/12.)
        f = a * self.frequeny_ref
        return f

class JustIntonation(Tuning):
    def F(self, d, n):
        return fractions.Fraction(d, n)
    def __init__(self, note_ref, frequeny_ref, tuning_base):
        super().__init__(note_ref % 12, frequeny_ref)
        self.tuning_base = tuning_base % 12
        self.factors = 12*[0]
    def set_factors(self, q):
        pitch_relbase_index = ((self.note_ref + 12) - self.tuning_base) % 12
        qref = q[pitch_relbase_index]
        elog('JustIntonation: note_ref=%d, tuning_base=%d, pri=%d, qref=%g' %
              (self.note_ref, self.tuning_base, pitch_relbase_index, qref))
        dqref = 1 / qref
        octave_fix = fractions.Fraction(1)
        i = 0
        pi = self.note_ref
        qi = pitch_relbase_index
        while i < 12:
            # elog('pi=%d, qi=%d' % (pi, qi))
            self.factors[pi] = q[qi] * (dqref * octave_fix)
            i += 1
            pi += 1
            qi += 1
            if pi == 12:
                pi = 0
                octave_fix /= 2
            if qi == 12:
                qi = 0
                octave_fix *= 2
            
        # elog('q=%s' % list(map(lambda x: '%g' % x, q)))
        # elog('factors=%s' % list(map(lambda x: '%g' % x, self.factors)))
        # elog('factors=%s' % str(self.factors))
        # elog('factors=%s' % str(list(map(float, self.factors))))
        if self.note_frequency(60) < 200:
            fatal('Too low c4')
    def middle_note_frequency(self, note):
        frequeny = self.factors[note] * self.frequeny_ref
        return frequeny
    
class Pythagorean(JustIntonation):

    def __init__(self, note_ref, frequeny_ref, tuning_base):
        elog('Pythagorean(%d, %g, %d)' % (note_ref, frequeny_ref, tuning_base))
        super().__init__(note_ref % 12, frequeny_ref, tuning_base)
        F = self.F
        q = [
            1, F(2**8,3**5), F(3**2,2**3), F(2**5,3**3),
            F(3**4,2**6), F(2**2,3), F(3**6,2**9), F(3,2),
            F(2**7,3**4), F(3**3,2**4), F(2**4,3**2), F(3**5,2**7)
        ]
        self.set_factors(q)

class FiveLimit(JustIntonation):

    def __init__(self, note_ref, frequeny_ref, tuning_base):
        super().__init__(note_ref % 12, frequeny_ref, tuning_base)
        F = self.F
        q = [
            1, F(2**4,3*5), F(3**2,2**3), F(2*3,5),
            F(5,2**2), F(2**2,3), F((3**2)*5,2**5), F(3,2),
            F(2**3,5), F(5,3), F(3**2,5), F(3*5,2**3)
        ]
        self.set_factors(q)

def tuning_test(argv):
    system = argv[0]
    tuning = None
    notes = []
    note_ref = int(argv[1])
    frequeny_ref = float(argv[2])
    if system.startswith('eq'):
        tuning = EqualTempered(note_ref, frequeny_ref)
        notes = map(int, argv[3:])
    else:
        tuning_base = int(argv[3])
        notes = map(int, argv[4:])
        if system.startswith('pytha'):
            tuning = Pythagorean(note_ref, frequeny_ref, tuning_base)
        elif system.startswith('five'):
            tuning = FiveLimit(note_ref, frequeny_ref, tuning_base)
        else:
            fatal('Unknown tuning system: %s' % system)
    for note in notes:
        f = tuning.note_frequency(note)
        elog('frequeny(%d = %s) = %g' % (note, note_name[note], f))
    return 0


WHITE_SEMI = [0, 2, 4, 5, 7, 9, 11] # CBDEFGAB
SEMI_WHITE = dict(map(lambda n: (WHITE_SEMI[n], n), range(len(WHITE_SEMI))))

TUNING_RANGES = []
for b in WHITE_SEMI: # CBDEFGAB
    mult = 2. ** ((b - 9)/12.)
    TUNING_RANGES.append(
        tuple(map(lambda afreq: round(mult*afreq), [400, 460])))
    
            
class MusicKeyboard:

    color_white = (0.93, 0.93, 0.66)
    color_black = (0.3, 0.2, 0.2)
    [TUNING_EQUAL, TUNING_PYTHAGOREAN, TUNING_FIVE] = range(3)

    def __init__(
            self,
            window_size=Defaults.window_size,
            note_low=Defaults.note_low,
            note_high=Defaults.note_high,
            volume=Defaults.volume,
            duration=Defaults.duration,
            pitch_note=Defaults.pitch_note,
            pitch_frequency=Defaults.pitch_frequency,
            tuning_system=None,
            tuning_base=Defaults.tuning_base
    ):
        elog('MusicKeyboard.__init__')
        self.rc = 0
        self.note_low = number_of_note(note_low)
        self.note_high = number_of_note(note_high)
        elog('notes: low=%d, high=%d' % (self.note_low, self.note_high))
        self.volume = volume
        self.duration = duration
        elog('pitch_note=%s' % pitch_note)
        if type(pitch_note) is not int:
            wi = 'cdefgab'.find(pitch_note.lower())
            pitch_note = WHITE_SEMI[wi] if wi >= 0 else 9
        if pitch_note not in WHITE_SEMI:
            pitch_note = 9 # 'A la"
        elog('pitch_note=%d' % pitch_note)
        self.pitch_note = pitch_note
        self.pitch_frequency = pitch_frequency
        if tuning_system is None:
            tuning_system = MusicKeyboard.TUNING_EQUAL
        self.tuning_system = tuning_system
        self.tuning_base = number_of_note(tuning_base)
        self.build_ui(window_size)

    def run(self):
        elog('run')
        self.set_tuning()
        Gtk.main()
        elog('run end')

    def set_tuning(self):
        mk = MusicKeyboard
        note = self.pitch_note
        frequency = self.pitch_frequency
        elog('set_tuning')
        if self.tuning_system == mk.TUNING_EQUAL:
            self.tuning = EqualTempered(note, frequency)
        elif self.tuning_system == mk.TUNING_PYTHAGOREAN:
            self.tuning = Pythagorean(note, frequency, self.tuning_base)
        elif self.tuning_system == mk.TUNING_FIVE:
            self.tuning = FiveLimit(note, frequency, self.tuning_base)
        else:
            fatal('Bad tuning_system=%s' % self.tuning_system)
        
    def build_ui(self, window_size):
        self.window_size = window_size
        win = Gtk.Window(title="Music Keyboard")
        win.connect("destroy", self.quit, "via window destroy")
        win.set_default_size(window_size[0], window_size[1])
        vbox = Gtk.VBox()
        menubar = self.build_menubar()
        vbox.pack_start(menubar, False, True, 6)
        status_control_frame = self.build_status_control()
        vbox.pack_start(status_control_frame, False, True, 6)
        keyboard = self.build_keyboard()
        vbox.pack_start(keyboard, True, True, 6)
        self.viewlog = self.build_view_log(window_size)
        vbox.pack_start(self.viewlog, False, True, 6)        
        win.add(vbox)
        elog('viewlog size=%s' % str(self.viewlog.get_size_request()))
        win.show_all()
        elog('after show viewlog size=%s' % str(self.viewlog.get_size_request()))

    def build_menubar(self):
        mb = Gtk.MenuBar()

        file_menu = Gtk.Menu();
        mi_quit = Gtk.MenuItem("Quit");
        mi_quit.connect('activate', self.quit, "quit via menu")
        file_menu.append(mi_quit)
        file_mi = Gtk.MenuItem('File')
        file_mi.set_submenu(file_menu)
        mb.append(file_mi)

        help_menu = Gtk.Menu()
        mi_about = Gtk.MenuItem("About")
        # mi_about.connect('activate', self.about, 17)
        help_menu.append(mi_about)
        help_mi = Gtk.MenuItem('Help')
        help_mi.set_submenu(help_menu)
        mb.append(help_mi)

        return mb

    def label_frame(self, label):
        frame = Gtk.Frame()
        frame.set_label(label)
        return frame

    def hscale(self, val, vmin, vmax, step_inc, page_inc):
        HORIZONTAL = Gtk.Orientation.HORIZONTAL
        adj = Gtk.Adjustment(val, vmin, vmax, step_inc, page_inc, page_inc)
        scale = Gtk.Scale(orientation=HORIZONTAL, adjustment=adj)
        scale.set_value_pos(Gtk.PositionType.LEFT)
        scale.set_hexpand(True)
        scale.set_margin_left(6)
        scale.set_margin_right(6)
        elog('val=%g' % val)
        scale.set_value(val)
        return scale
    
    def framed_hscale(self, name, val, vmin, vmax, step_inc, page_inc):
        HORIZONTAL = Gtk.Orientation.HORIZONTAL
        frame = self.label_frame(name)
        scale = self.hscale(val, vmin, vmax, step_inc, page_inc)
        frame.add(scale)
        return frame, scale
    
    def change_pitch_note(self, combo):
        text = combo.get_active_text()
        self.pitch_note = 'CxDxEFxGxAxB'.find(text)
        self.pitch_frequency = self.tuning.note_frequency(self.pitch_note + 60)
        elog('change_pitch_note: text=%s, pitch: note=%d, frequency=%g' %
             (text, self.pitch_note, self.pitch_frequency))
        self.set_tuning()
        wi = SEMI_WHITE[self.pitch_note]
        tuning_range = TUNING_RANGES[wi]
        adj = Gtk.Adjustment(self.pitch_frequency,
            tuning_range[0], tuning_range[1], 0.5, 1.0)
        self.frequeny_scale.set_adjustment(adj)
        self.frequeny_scale.set_value(self.pitch_frequency)
        self.set_tuning()
        
    def change_pitch_frequency(self, w):
        self.pitch_frequency = w.get_value()
        elog('pitch_frequency=%g' % self.pitch_frequency)
        self.set_tuning()

    def tuning_sensitive_widgets(self, widgets):
        sensitive = self.tuning_system != MusicKeyboard.TUNING_EQUAL
        for widget in widgets:
            widget.set_sensitive(sensitive)

    def change_tuning_system(self, combo, widgets):
        text = combo.get_active_text()
        elog('change_tuning_system: text=%s, widgets=%s' % (text, str(widgets)))
        mk = MusicKeyboard
        if text.startswith('Equal'):
            self.tuning_system = mk.TUNING_EQUAL
        elif text.startswith('Pyth'):
            self.tuning_system = mk.TUNING_PYTHAGOREAN
        else:
            self.tuning_system = mk.TUNING_FIVE
        self.tuning_sensitive_widgets(widgets)
        self.set_tuning()

    def change_tuning_base(self, combo):
        text = combo.get_active_text()
        self.tuning_base = 'CxDxEFxGxAxB'.find(text)
        elog('change_tuning_system: text=%s, tuning_base=%d' %
             (text, self.tuning_base))
        self.set_tuning()
        
    def frame_tuning(self):
        frame = self.label_frame('Tuning')
        hbox = Gtk.HBox()
        combo_pitch_note = Gtk.ComboBoxText()
        for i in range(7):
            combo_pitch_note.append_text('CDEFGAB'[i])
            
        wi = SEMI_WHITE[self.pitch_note]
        combo_pitch_note.set_active(wi)
        hbox.pack_start(combo_pitch_note, False, False, 1)
        combo_pitch_note.connect('changed', self.change_pitch_note)
        elog('pitch_frequency=%g' % self.pitch_frequency)
        hbox.pack_start(Gtk.Label('='), False, False, 1)
        tuning_range = TUNING_RANGES[wi]
        self.frequeny_scale = self.hscale(
            self.pitch_frequency, tuning_range[0], tuning_range[1], 0.1, 0.5)
        self.frequeny_scale.connect('value-changed',
            self.change_pitch_frequency)
        hbox.pack_start(self.frequeny_scale, False, True, 4)
        combo_tuning_system = Gtk.ComboBoxText()
        for s in [
                'Equal Temperament',
                'Pythagorean 3:2',
                'Just Intonation :<5']:
            combo_tuning_system.append_text(s)
        combo_tuning_system.set_active(self.tuning_system)
        hbox.pack_start(combo_tuning_system, False, False, 1)
        at = Gtk.Label('@')
        hbox.pack_start(at, False, False, 1)
        combo_base = Gtk.ComboBoxText()
        for i in range(7):
            combo_base.append_text('CDEFGAB'[i])
        combo_base.set_active(1)
        combo_tuning_system.connect('changed',
            self.change_tuning_system, [at, combo_base])
        combo_tuning_system.connect('changed',
            self.change_tuning_system, [at, combo_base])
        combo_base.connect('changed', self.change_tuning_base)
        hbox.pack_start(combo_base, False, False, 1)
        self.tuning_sensitive_widgets([at, combo_base])

        frame.add(hbox)
        return frame
        
    def volume_change(self, widget):
        elog('volume_change: value=%g' % widget.get_value())
        self.volume = widget.get_value()

    def duration_change(self, widget):
        elog('volume_change: value=%g' % widget.get_value())
        self.duration = widget.get_value()

    def build_status_control(self):
        frame = self.label_frame('Status / Control')
        hbox = Gtk.HBox()
        hbox_vd = Gtk.HBox()
        frame_volume, volume_scale = self.framed_hscale(
            'Volume', self.volume, 0.1, 1., 0.01, 0.05)
        volume_scale.connect('value-changed', self.volume_change)
        hbox_vd.pack_start(frame_volume, False, True, 6)
        frame_duration, duration_scale = self.framed_hscale(
            'Duration', self.duration, 0.1, 5., 0.1, 0.5)
        duration_scale.connect('value-changed', self.duration_change)
        hbox_vd.pack_start(frame_duration, False, True, 6)
        hbox.pack_start(hbox_vd, False, True, 6)
        hbox.pack_start(self.frame_tuning(), False, True, 6)
        frame.add(hbox)
        
        return frame

    def build_keyboard(self):
        da = Gtk.DrawingArea()
        da.connect('draw', self.draw_keyboard, 17)
        elog('da.connect button event')
        da.set_events(da.get_events()
              | Gdk.EventMask.BUTTON_PRESS_MASK   
              | Gdk.EventMask.BUTTON_RELEASE_MASK 
              # | Gdk.EventMask.POINTER_MOTION_MASK
        )
        # da.connect('button_press_event', self.keyboard_press)
        da.connect('button_release_event', self.keyboard_press, 13)
        return da

    def draw_keyboard(self, da, cr, data):
        elog('da=%s, cr=%s, data=%s' % (da, cr, data))
        w = da.get_allocated_width()
        h = da.get_allocated_height()
        self.locator = Locator(w, h, self.note_low, self.note_high)
        elog('locator=%s' % self.locator)
        elog('w=%d, h=%d' % (w, h))
        cr.set_source_rgb(0.0, 0.0, 0.0)
        cr.paint()
        self.draw_white_keys(cr, w, h)
        self.draw_black_keys(cr, w, h)

    def draw_white_keys(self, cr, w, h):
        self.cr_set_rgb(cr, type(self).color_white)
        for key in self.locator.white_keys:
            inner = key.inner
            cr.rectangle(inner.xb, 0, inner.size(), h)
            cr.fill()

    def draw_black_keys(self, cr, w, h):
        cr.set_source_rgb(0.0, 0.0, 0.0)
        hb = self.locator.black_height()
        for key in self.locator.black_keys:
            outer = key.outer
            cr.rectangle(outer.xb, 0, outer.size(), hb)
            cr.fill()
        hb -= 1
        self.cr_set_rgb(cr, type(self).color_black)
        for key in self.locator.black_keys:
            inner = key.inner
            cr.rectangle(inner.xb, 0, inner.size(), hb)
            cr.fill()

    def cr_set_rgb(self, cr, rgb):
        cr.set_source_rgb(rgb[0], rgb[1], rgb[2])

    def keyboard_press(self, widget, event, *args):
        elog('keyboard_press: x=%d, y=%d, args=%s' %
            (event.x, event.y, str(args)))
        note = self.locator.pick(event.x, event.y)
        elog('note=%d' % note)
        if note > 0:
            self.play_note(note)

    def build_view_log(self, window_size):
        viewlog = Gtk.TextView()
        viewlog.set_property('editable', False)
        viewlog.set_property('cursor-visible', False)
        viewlog.set_size_request(window_size[0], window_size[1] // 6)
        return viewlog

    def view_log_add_line(self, line):
        if not line.endswith('\n'):
            line += '\n'
        buffer = self.viewlog.get_buffer()
        curr = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(),
            True)
        lines = curr.split('\n')
        lines = list(filter(lambda s: len(s) > 0, lines))
        elog('lines[%d]=%s' % (len(lines), str(lines)))
        if len(lines) < 6:
            buffer.insert(buffer.get_end_iter(), line)
        else:
            lines = lines[1:] + [line]
            text = '\n'.join(lines)
            buffer.set_text(text)
        
    def play_note(self, note):
        elog('play_note: note=%d' % note)
        f = self.tuning.note_frequency(note)
        cmd = 'play -qn synth %g pluck %g vol %g' % (
            self.duration, f, self.volume)
        self.view_log_add_line(cmd)
        self.syscmd(cmd)

    def syscmd(self, cmd):
        elog(cmd)
        rc = os.system(cmd)
        if rc != 0:
            elog('os.system: rc=%d' % rc)

    def quit(self, *args):
        elog('quit args=%s' % str(args))
        Gtk.main_quit()

class App:

    def usage(self, p0):
        MK = MusicKeyboard
        sys.stderr.write(textwrap.dedent(
        """
        Usage:                                     # [Defaults]
          %s
            -h | --help                            # This message
            -geo <width>x<height>                  # [%dx%d]
            -range <low-high>                      # [%s-%s]
            -pitch <note=frequency>                # [a=440]    
            -tuning <equal|pyth|just>[,<basenote>] # [equal]
            -vol <volume>                          # [%g] 0.1 <= volume <= 1.0
            -t <duration seconds>                  # [%g] 0.1 <= seconds <= 1.0

        Note can be:
           [cdefgab] with possible alteration [sf] and octave number
           or midi number [0-85]  (60 = middle-C [Do]))
        """ % (
            p0,
            Defaults.window_size[0], Defaults.window_size[1],
            name_of_note(Defaults.note_low), name_of_note(Defaults.note_high),
            Defaults.volume,
            Defaults.duration
            )))
        self.helped = True
        
    def __init__(self, argv):
        elog('App.__init__')
        self.rc = 0
        self.helped = False
        self.window_size = Defaults.window_size
        self.note_low  = Defaults.note_low
        self.note_high  = Defaults.note_high
        self.volume  = Defaults.volume
        self.duration  = Defaults.duration
        self.pitch_note = Defaults.pitch_note
        self.pitch_frequency = Defaults.pitch_frequency
        self.tuning = MusicKeyboard.TUNING_EQUAL
        self.tuning_base = 'd4'
        ai = 1
        while self.may_run() and ai < len(argv):
            opt = argv[ai]
            ai += 1
            elog('ai=%d, opt=%s' % (ai, opt))
            if opt in ('-h', '-help', '--help'):
                self.usage(argv[0])
            elif opt == '-geo':
                self.window_size = (int(argv[ai]), int(argv[ai + 1]));
                ai += 2
            elif opt == '-range':
                [self.note_low, self.note_high] = list(argv[ai].split('-'))
                ai += 1
            elif opt == '-pitch':
                ss = argv[ai].split('=')
                self.pitch_note = ss[0]
                self.pitch_frequency = float(ss[1])
                ai += 1
            elif opt == '-tuning':
                ss = list(argv[ai].split(','))
                if ss[0].startswith('pyth'):
                    self.tuning = MusicKeyboard.TUNING_PYTHAGOREAN
                elif ss[0].startswith('just'):
                    self.tuning = MusicKeyboard.TUNING_FIVE
                if len(ss) > 1:
                    self.tuning_base = ss[1]
                ai += 1
            else:
                self.usage(argv[0])
                fatal('Bad option: %s' % opt)

    def run(self):
        elog('App.run')
        mk = MusicKeyboard(
            window_size=self.window_size,
            note_low=self.note_low,
            note_high=self.note_high,
            volume=self.volume,
            duration=self.duration,
            pitch_note=self.pitch_note,
            pitch_frequency=self.pitch_frequency,
            tuning_system=self.tuning,
            tuning_base=self.tuning_base
        )
        mk.run()
        self.rc = mk.rc

    def may_run(self):
        return self.rc == 0 and not self.helped
                                         
                                        
        
if __name__ == '__main__':
    rc = 0
    elog('Hello')
    a1 = sys.argv[1] if len(sys.argv) > 1 else None
    if a1 == 'locator':
        rc = locator_test(sys.argv[2:])
        sys.exit(rc)
    elif a1 == 'tuning':
        rc = tuning_test(sys.argv[2:])
        sys.exit(rc)
    p = App(sys.argv)
    if p.may_run():
        p.run()
    rc = p.rc
    elog('Bye')
    sys.exit(rc)
