#!/usr/bin/env python3
#

import os
import sys

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

    def print(self, f=sys.stdout):
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
    locator.print()
    tail = nums[4:]
    xys = list(zip(tail[0::2], tail[1::2]))
    for (x, y) in xys:
        elog('pick(%d, %d) = %d' % (x, y, locator.pick(x, y)))
    return 0


class MusicKeyboard:

    # defult_note_low = 60 - 2*12
    defult_note_low = 60
    # defult_note_high = 60 + 2*12
    defult_note_high = defult_note_low + 11
    color_white = (0.93, 0.93, 0.66)
    color_black = (0.13, 0.13, 0.07)

    def __init__(self, note_low = None, note_high=None):
        self.rc = 0
        self.note_low = (type(self).defult_note_low if note_low is None
            else note_low)
        self.note_high = (type(self).defult_note_high if note_high is None
            else note_high)
        self.build_ui()

    def run(self):
        elog('run')
        Gtk.main()
        elog('run end')

    def build_ui(self):
        win = Gtk.Window(title="Music Keyboard")
        win.set_default_size(1200, 400)
        vbox = Gtk.VBox()
        menubar = self.build_menubar()
        vbox.pack_start(menubar, False, True, 0)
        keyboard = self.build_keyboard()
        vbox.pack_start(keyboard, True, True, 2)
        win.add(vbox)
        win.show_all()

    def build_menubar(self):
        mb = Gtk.MenuBar()

        file_menu = Gtk.Menu();
        mi_quit = Gtk.MenuItem("Quit");
        mi_quit.connect('activate', self.quit, 17)
        file_menu.append(mi_quit)
        file_mi = Gtk.MenuItem('File')
        file_mi.set_submenu(file_menu)
        mb.append(file_mi)

        help_menu = Gtk.Menu();
        mi_about = Gtk.MenuItem("About");
        # mi_about.connect('activate', self.about, 17)
        help_menu.append(mi_about)
        help_mi = Gtk.MenuItem('Help')
        help_mi.set_submenu(help_menu)
        mb.append(help_mi)

        return mb

    def build_keyboard(self):
        da = Gtk.DrawingArea()
        da.connect('draw', self.draw_keyboard, 17)
        elog('da.connect button event')
        da.set_events(da.get_events()
              | Gdk.EventMask.BUTTON_PRESS_MASK   
              | Gdk.EventMask.BUTTON_RELEASE_MASK 
              | Gdk.EventMask.POINTER_MOTION_MASK)
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
        
    def quit(self, *args):
        elog('quit args=%s' % str(quit))
        Gtk.main_quit()

if __name__ == '__main__':
    rc = 0
    elog('Hello')
    a1 = sys.argv[1] if len(sys.argv) > 1 else None
    if a1 == 'locator':
        rc = locator_test(sys.argv[2:])
        sys.exit(rc)
    p = MusicKeyboard()
    p.run()
    rc = p.rc
    elog('Bye')
    sys.exit(rc)
