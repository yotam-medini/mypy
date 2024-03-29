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
import random


def safe_float(s):
    ret = None
    try:
        ret = float(s)
    except:
        ret = None
    return ret

def rand_color():
    return '#%06x' % random.randint(0, 16**6 - 1)
    
class GPlot:

    def usage(self):
        sys.stderr.write(textwrap.dedent("""
        Usage:
          %s
          [-h | -help | --help]           # This message
          [-bbox <xmin xmax ymin ymax>]   #
          [-line <x1 y1  x2 y2  ...>]     # repeatable
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
        self.polys = []
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
            elif opt in ('-line', '-poly'):
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
                if opt == '-line':
                    self.lines.append(line)
                else:
                    self.polys.append(line)
            elif opt == '-circle':
                circle = tuple(map(float, argv[ai: ai + 3]))
                ai += 3
                self.circles.append(circle)
            else:
                self.fatal('Unsupported option: %s' % opt)        

    def set_bbox(self, xs, ys):
        # vlog('xs=%s' % str(xs))
        xmin = min(xs) - 1 if len(xs) > 0 else 0
        xmax = max(xs) + 1 if len(xs) > 0 else 1
        ymin = min(ys) - 1 if len(ys) > 0 else 0
        ymax = max(ys) + 1 if len(ys) > 0 else 1
        vlog('X: min=%g, max=%g, %s' % (xmin, xmax, str(xs)))
        vlog('Y: min=%g, max=%g, %s' % (ymin, ymax, str(ys)))
        dx = xmax - xmin
        dy = ymax - ymin
        extra = abs(dy - dx)/2.
        if dx < dy:
            xmin -= extra
            xmax += extra
        else:
            ymin -= extra
            ymax += extra
        self.bbox = [xmin, xmax, ymin, ymax]
        vlog('bbox: %s' % str(self.bbox))

    def run(self):
        win = Gtk.Window()
        win.connect("delete-event", Gtk.main_quit)
        win.set_default_size(600, 400)
        win.set_title("GPlot via MatPlotLib in GTK")

        f = Figure(figsize=(6, 6), dpi=100)
        # f.add_axes([-1, -1, 2, 2])
        a = f.add_subplot(111)

        xs = []
        ys = []
        for line in self.lines:
            x = list(map(lambda i: line[i], range(0, len(line), 2)))
            y = list(map(lambda i: line[i], range(1, len(line), 2)))
            xs.extend(x)
            ys.extend(y)
            a.plot(x, y)

        for poly in self.polys:
            x = list(map(lambda i: poly[i], range(0, len(poly), 2)))
            y = list(map(lambda i: poly[i], range(1, len(poly), 2)))
            xs.extend(x)
            ys.extend(y)
            xy = []
            for i in range(len(poly) / 2):
                xy.append((poly[2*i], poly[2*i + 1]))
            gpoly = Polygon(xy, color=rand_color())
            a.add_patch(gpoly)

        for (x, y, r) in self.circles:
            circle = Circle((x, y), r, fill=False)
            xs.append(x - r)
            xs.append(x + r)
            ys.append(y - r)
            ys.append(y + r)
            a.add_patch(circle)

        if self.bbox is None:
            self.set_bbox(xs, ys)
        a.set_xlim(self.bbox[0: 2])
        a.set_ylim(self.bbox[2: 4])

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
