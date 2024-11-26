#!/usr/bin/env python
"""Color Selector

GtkColorSelection lets the user choose a color. GtkColorSelectionDialog is a
prebuilt dialog containing a GtkColorSelection."""

import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

class ColorSelectorDemo(Gtk.Window):
    color = Gdk.color_parse("blue")

    def __init__(self, parent=None):
        # Create the toplevel window
        Gtk.Window.__init__(self)
        try:
            self.set_screen(parent.get_screen())
        except AttributeError:
            self.connect('destroy', lambda *w: Gtk.main_quit())

        self.set_title(self.__class__.__name__)
        self.set_border_width(8)
        vbox = Gtk.VBox()
        vbox.set_border_width(8)
        self.add(vbox)

        # Create the color swatch area
        frame = Gtk.Frame()
        frame.set_shadow_type(Gtk.ShadowType.IN)
        vbox.pack_start(frame, True, True, 8)

        self.d_area = Gtk.DrawingArea()
        self.d_area.set_size_request(200, 200)
        self.d_area.modify_bg(Gtk.StateType.NORMAL, self.color)
        frame.add(self.d_area)

        button = Gtk.Button("_Change the above color")
        button.set_halign(Gtk.Align.END)
        button.set_valign(Gtk.Align.CENTER)

        vbox.pack_start(button, True, True, 8)

        button.connect('clicked', self.on_change_color_clicked)
        # button.set_flags(Gtk.CAN_DEFAULT)
        button.grab_default()

        self.show_all()

    def on_change_color_clicked(self, button):

        dialog = Gtk.ColorSelectionDialog("Changing color")
        dialog.set_transient_for(self)
        colorsel = dialog.colorsel

        colorsel.set_previous_color(self.color)
        colorsel.set_current_color(self.color)
        colorsel.set_has_palette(True)

        response = dialog.run()

        if response == Gtk.RESPONSE_OK:
            self.color = colorsel.get_current_color()
            self.d_area.modify_bg(Gtk.StateType.NORMAL, self.color)

        dialog.destroy()
        return True

def main():
    ColorSelectorDemo()
    Gtk.main()

if __name__ == '__main__':
    main()
