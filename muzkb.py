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


win = Gtk.Window(title="Music Keyboard")
win.connect("destroy", Gtk.main_quit)
vbox = Gtk.VBox()

drawingarea = Gtk.DrawingArea()
vbox.add(drawingarea)
drawingarea.connect('draw', draw)
win.add(vbox)
win.show_all()
Gtk.main()


if __name__ == '__main__':
    elog('Hello')
    elog('Bye')
    sys.exit(0)
