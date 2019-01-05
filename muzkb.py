#!/usr/bin/env python3
#

import os
import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
# from gi.repository import Gdk
import cairo


def elog(msg):
    sys.stderr.write('%s\n' % msg)


class MusicKeyboard:

    defult_note_low = 60 - 2*12
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
        return da

    def draw_keyboard(self, da, cr, data):
        elog('da=%s, cr=%s, data=%s' % (da, cr, data))
        w = da.get_allocated_width()
        h = da.get_allocated_height()
        elog('w=%d, h=%d' % (w, h))
        cr.set_source_rgb(0.0, 0.0, 0.0)
        cr.paint()

        self.draw_white_keys(cr, w, h)
        self.draw_black_keys(cr, w, h)
        # cr.set_source_rgb(0.93, 0.93, 0.66)
        # cr.rectangle(w/10, h/6, 2*w/19, h)
        # cr.fill()
    
    def draw_white_keys(self, cr, w, h):
        n = self.note_high - self.note_low + 1
        elog('draw_white_keys: n=%d' % n)
        key_width_portion = w//n
        low_white = self.note_low
        lskip = 0
        if not self.note_is_white(low_white):
            lskip = key_width_portion // 2
            w -= lskip
            low_white += 1
        high_white = self.note_high
        if not self.note_is_white(high_white):
            w -= lskip
            high_white -= 1
        n_whites = self.n_whites_in(low_white, high_white)
        key_width_outer = w // n_whites
        space = max(key_width_outer // 32, 1)
        key_width_inner = key_width_outer - 2*space
        elog('space=%d, lskip=%d' % (space, lskip))
        elog('w=%d, key_width_outer=%d, key_width_inner=%d' %
             (w, key_width_outer, key_width_inner))
        self.cr_set_rgb(cr, type(self).color_white)
        for k in range(n_whites):
            xl = ((k*w + n_whites//2) // n_whites) + space + lskip
            xr = xl + key_width_inner
            elog('k=%d, xl=%d, xr=%d' % (k, xl, xr))
            cr.rectangle(xl, 0, key_width_inner, h)
            cr.fill()

    def draw_black_keys(self, cr, w, h):
        n = self.note_high - self.note_low + 1
        elog('draw_black_keys: n=%d' % n)
        key_width_portion = w//n
        elog('draw_black_keys: key_width_portion=%d' % key_width_portion)
        space = max(key_width_portion // 16, 1)
        key_width_inner = key_width_portion - 2*space
        self.cr_set_rgb(cr, type(self).color_black)
        for note in range(self.note_low, self.note_high + 1):
            if self.note_is_black(note):
                k = note - self.note_low
                xl = ((k*w + n//2) // n) + space
                elog('draw_black_keys: xl=%d' % xl)
                cr.rectangle(xl, 0, key_width_inner, 2*h//3)
                cr.fill()
        
    def note_is_white(self, note):
        return (note % 12) in [0, 2, 4, 5, 7, 9, 11]

    def note_is_black(self, note):
        return not self.note_is_white(note)

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
        
    def cr_set_rgb(self, cr, rgb):
        cr.set_source_rgb(rgb[0], rgb[1], rgb[2])

    def quit(self, *args):
        elog('quit args=%s' % str(quit))
        Gtk.main_quit()
        
if __name__ == '__main__':
    elog('Hello')
    p = MusicKeyboard()
    p.run()
    rc = p.rc
    elog('Bye')
    sys.exit(rc)


    
if __name__ == 'x__main__':

    def draw(da, cr):
        elog('draw(da=%s, cr=%s)' % (da, cr))
        w = da.get_allocated_width()
        h = da.get_allocated_height()
        size = min(w,h)

        cr.set_source_rgb(0.0,0.2,0.0)
        cr.paint()

        cr.set_source_rgb(1.0,0.0,0.0)

        cr.arc(0.5*w,0.5*h,0.5*size,0.0,6.3)
        cr.fill()

    def exercise():
        win = Gtk.Window(title="Music Keyboard")
        win.connect("destroy", Gtk.main_quit)
        vbox = Gtk.VBox()

        drawingarea = Gtk.DrawingArea()
        vbox.add(drawingarea)
        drawingarea.connect('draw', draw)
        win.add(vbox)
        win.show_all()
        Gtk.main()

    elog('Hello')
    exercise()
    elog('Bye')
    sys.exit(0)
