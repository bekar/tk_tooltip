#!/usr/bin/env python3

'''
# Tooltip

The ToolTip class provides a flexible tooltip widget for tkinter;
it is based on IDLE's ToolTip module.

Michael Lange <klappnase@freakmail.de>
http://tkinter.unpythonic.net/wiki/ToolTip

## WIDGET METHODS

- configure(**options)
   Modifies one or more widget options. If no options are given, the
   method returns a dictionary containing all current option values.
   The changes will take effect the next time the tooltip shows up.

    **options
      Widget options

    anchor={'n', 's', 'e', 'w', 'nw', ... }; Default is CENTER.
      Where the text is placed inside the widget.

    bd={integer}; Default is 1
      The width of the widget border. The .
      NOTE: don't use "borderwidth"

    bg={string}; Default is "lightyellow"
      background color to use for the widget
      NOTE: don't use "background"

    delay={integer};  Default is 1500 ms
      delay for widget to appear when the mouse pointer hovers

    fg={string}; Default is "black"
      foreground (i.e. text) color to use;
      NOTE: don't use "foreground"

    follow_mouse={0, 1}
      tooltip follows the mouse pointer; default = 0
      NOTE: it cannot be changed after widget initialization

    font={string, list}; Default is system specific
      font to use for the widget

    justify={"left", "right", "center"}; Default is "left"
      multiple lines text alignment

    padx={integer}; Default is 4
      extra space added to the left and right within the widget

    pady={integer}; Default is 2
      extra space above and below the text

    relief={"flat", "ridge", "groove", "raised", "sunken", "solid"}; Default is "solid"

    state={"normal", "disabled"}; Default is "normal"
      if set to "disabled" the tooltip will not appear

    text={string}
      the text that is displayed inside the widget

    textvariable={StringVar() object}
      if set to an instance of tkinter.StringVar() the variable's
      value will be used as text for the widget

    width={integer}; Default is 0, which means use "wraplength"
      width of the widget

    wraplength={integer}; Default is 150
      limits the number of characters in each line

- enter()
   callback when the mouse pointer enters the parent widget

- leave()
   called when the mouse pointer leaves the parent widget

- motion()
   is called when the mouse pointer moves inside the parent
   widget if follow_mouse is set to 1 and the tooltip has shown up to
   continually update the coordinates of the tooltip window

- coords()
   calculates the screen coordinates of the tooltip window

- create_contents()
   creates the contents of the tooltip window (by default a tkinter.Label())
'''

import tkinter as tk

class ToolTip:
    def __init__(self, master, text='Your text here', delay=1500, **opts):
        self.master = master
        self._opts = {
            'anchor'       : 'center',
            'bd'           : 1,
            'bg'           : 'lightyellow',
            'delay'        : delay,
            'fg'           : 'black',
            'follow_mouse' : 0,
            'font'         : None,
            'justify'      : 'left',
            'padx'         : 4,
            'pady'         : 2,
            'relief'       : 'solid',
            'state'        : 'normal',
            'text'         : text,
            'textvariable' : None,
            'width'        : 0,
            'wraplength'   : 150
        }
        self.configure(**opts)
        self._tipwindow = None
        self._id = None
        self._id1 = self.master.bind("<Enter>", self.enter, '+')
        self._id2 = self.master.bind("<Leave>", self.leave, '+')
        self._id3 = self.master.bind("<ButtonPress>", self.leave, '+')
        self._follow_mouse = 0
        if self._opts['follow_mouse']:
            self._id4 = self.master.bind("<Motion>", self.motion, '+')
            self._follow_mouse = 1

    def configure(self, **opts):
        for key in opts:
            if key in self._opts:
                self._opts[key] = opts[key]
            else:
                KeyError = 'KeyError: Unknown option: "%s"' %key
                raise KeyError

    def enter(self, event=None): # handles <Enter> event
        self._schedule()

    def leave(self, event=None): # handles <Leave> event
        self._unschedule()
        self._hide()

    def motion(self, event=None): # handles <Motion> event
        if self._tipwindow and self._follow_mouse:
            x, y = self.coords()
            self._tipwindow.wm_geometry("+%d+%d" % (x, y))

    def _schedule(self):
        self._unschedule()
        if self._opts['state'] == 'disabled':
            return
        self._id = self.master.after(self._opts['delay'], self._show)

    def _unschedule(self):
        id = self._id
        self._id = None
        if id:
            self.master.after_cancel(id)

    def _show(self):
        if self._opts['state'] == 'disabled':
            self._unschedule()
            return
        if not self._tipwindow:
            self._tipwindow = tw = tk.Toplevel(self.master)
            # hide the window until we know the geometry
            tw.withdraw()
            tw.wm_overrideredirect(1)

            if tw.tk.call("tk", "windowingsystem") == 'aqua':
                tw.tk.call("::tk::unsupported::MacWindowStyle", "style", tw._w, "help", "none")

            self.create_contents()
            tw.update_idletasks()
            x, y = self.coords()
            tw.wm_geometry("+%d+%d" % (x, y))
            tw.deiconify()

    def _hide(self):
        tw = self._tipwindow
        self._tipwindow = None
        if tw:
            tw.destroy()

    def coords(self):
        # The tip window must be completely outside the master widget;
        # otherwise when the mouse enters the tip window we get
        # a leave event and it disappears, and then we get an enter
        # event and it reappears, and so on forever :-(
        # or we take care that the mouse pointer is always outside the tipwindow :-)
        tw = self._tipwindow
        twx, twy = tw.winfo_reqwidth(), tw.winfo_reqheight()
        w, h = tw.winfo_screenwidth(), tw.winfo_screenheight()
        # calculate the y coordinate:
        if self._follow_mouse:
            y = tw.winfo_pointery() + 20
            # make sure the tipwindow is never outside the screen:
            if y + twy > h:
                y = y - twy - 30
        else:
            y = self.master.winfo_rooty() + self.master.winfo_height() + 3
            if y + twy > h:
                y = self.master.winfo_rooty() - twy - 3
        # we can use the same x coord in both cases:
        x = tw.winfo_pointerx() - twx / 2
        if x < 0:
            x = 0
        elif x + twx > w:
            x = w - twx
        return x, y

    def create_contents(self):
        opts = self._opts.copy()
        for opt in ('delay', 'follow_mouse', 'state'):
            del opts[opt]
        label = tk.Label(self._tipwindow, **opts)
        label.pack()

if __name__ == '__main__':
    root = tk.Tk(className='ToolTip-demo')
    root.bind('<Key-Escape>', lambda e: root.quit())

    l = tk.Listbox(root)
    l.pack(side='top')
    l.insert('end', "I'm a listbox")
    t1 = ToolTip(l, follow_mouse=1, text="I'm a tooltip with follow_mouse set to 1, so I won't be placed outside my parent")

    b = tk.Button(root, text='Quit', command=root.quit)
    b.pack(side='bottom')
    t2 = ToolTip(b, text='Enough of this')

    root.mainloop()
