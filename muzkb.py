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

if __name__ == '__main__':
    elog('Hello')
    elog('Bye')
    sys.exit(0)
