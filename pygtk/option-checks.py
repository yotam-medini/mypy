#!/usr/bin/env python
import sys
import string
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

def reactivate(e, *data):
    check_buttons = data[0];
    for cb in check_buttons:
        cb.set_active(True)
   

N = int(sys.argv[1]) if len(sys.argv) > 1 else 5
win = Gtk.Window(title="Set/Unset Options")
win.connect("destroy", Gtk.main_quit)
vbox = Gtk.VBox(spacing=6)
reactive = Gtk.Button(label="ReActive All");
vbox.pack_start(Gtk.Label(label="The buttons are 4u"), True, True, 0);
vbox.pack_start(reactive, True, True, 0);
check_buttons = []
for c in string.ascii_uppercase[:N]:
    hbox = Gtk.HBox()
    hbox.pack_start(Gtk.Label(label=c), True, True, 0)
    # toggle = Gtk.ToggleButton(label=c)
    # hbox.pack_start(toggle, True, True, 0)
    check = Gtk.CheckButton(label=c)
    check_buttons.append(check)
    hbox.pack_start(check, True, True, 0)
    vbox.pack_start(hbox, True, True, 0)
win.add(vbox)
reactive.connect("clicked", reactivate, check_buttons)
    
win.show_all()

Gtk.main()
