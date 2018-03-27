#!/usr/bin/env python

import sys

def vlog(msg):
    sys.stderr.write('%s\n' % msg)

import textwrap

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

vlog('importing MatPlotLib')
from matplotlib.backends.backend_gtk3agg import (FigureCanvasGTK3Agg as FigureCanvas)
from matplotlib.figure import Figure
from matplotlib.patches import Circle, Wedge, Polygon
import matplotlib.lines as mlines
vlog('MatPlotLib imported')
import numpy as np

def safe_float(s):
    ret = None
    try:
        ret = float(s)
    except:
        ret = None
    return ret

class GPlot:

    def usage(self):
        sys.stderr.write(textwrap.dedent("""
        Usage:
          %s
          [-h | -help | --help]           # This message
          [-bbox <xmin xmax ymin ymax>]   #
          [-line <x1 y1  x2 y2  ...]      # repeatable
          [-circle <x y r>]               # repeatable
        """) % self.argv[0])
        self.helped = True

    def fatal(msg):
        if self.rc == 0:
            self.rc = 1
            vlog(msg)
            self.usage()

    def mayrun(self):
        return self.rc == 0 and not self.helped
    
    def __init__(self, argv):
        self.argv = argv
        self.rc = 0
        self.helped = False
        self.bbox = None
        self.lines = []
        self.circles = []
        ai = 1
        while self.mayrun() and ai < len(argv):
            opt = self.argv[ai]
            ai += 1
            if opt in ('-h', '-help', '--help'):
                self.usage()
            elif opt == '-bbox':
                self.bbox = list(map(float, argv[ai: ai + 4]))
                ai += 4
            elif opt == '-line':
                line = []
                floating = True
                while floating and  ai < len(argv):
                    z = safe_float(argv[ai])
                    if z is None:
                        floating = False
                    else:
                        line.append(z)
                        ai += 1
                ll = len(line)
                if ll == 0 or ((ll % 2) != 0):
                    self.fatal('Bad line size: %d' % ll)
                self.lines.append(line)
            elif opt == '-circle':
                circle = tuple(map(float, argv[ai: ai + 3]))
                ai += 3
                self.circles.append(circle)
            else:
                self.fatal('Unsupported option: %s' % opt)        

    def run(self):
        win = Gtk.Window()
        win.connect("delete-event", Gtk.main_quit)
        win.set_default_size(600, 400)
        win.set_title("GPlot via MatPlotLib in GTK")

        f = Figure(figsize=(6, 6), dpi=100)
        # f.add_axes([-1, -1, 2, 2])
        a = f.add_subplot(111)
        if self.bbox:
            a.set_xlim(self.bbox[0: 2])
            a.set_ylim(self.bbox[2: 4])

        for line in self.lines:
            x = list(map(lambda i: line[i], range(0, len(line), 2)))
            y = list(map(lambda i: line[i], range(1, len(line), 2)))
            a.plot(x, y)

        for (x, y, r) in self.circles:
            circle = Circle((x, y), r)
            a.add_patch(circle)

        sw = Gtk.ScrolledWindow()
        win.add(sw)
        # A scrolled window border goes outside the scrollbars and viewport
        sw.set_border_width(10)

        canvas = FigureCanvas(f)  # a Gtk.DrawingArea
        canvas.set_size_request(800, 800)
        sw.add_with_viewport(canvas)
        # f.add_axes([-1, -1, 2, 2])

        win.show_all()
        Gtk.main()


if __name__ == '__main__':
    rc = 0
    vlog('Hello')
    g = GPlot(sys.argv)
    if g.mayrun():
        g.run()
    vlog('Bye')
    sys.exit(g.rc)
