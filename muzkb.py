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

    def __init__(self):
        self.rc = 0
        self.build_ui()

    def run(self):
        elog('run')
        Gtk.main()
        elog('run end')

    def build_ui(self):
        win = Gtk.Window(title="Music Keyboard")
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
