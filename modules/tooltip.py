import tkinter as tk
from tkinter import ttk

#thank you smart people on stackoverflow
class Tooltip:
	"""
	It creates a tooltip for a given widget as the mouse goes on it.

	See:

	- http://stackoverflow.com/questions/3221956/what-is-the-simplest-way-to-make-tooltips-in-tkinter/36221216#36221216
	- http://www.daniweb.com/programming/software-development/code/484591/a-tooltip-class-for-tkinter

	- Originally written by vegaseat on 2014.09.09.

	- Modified to include a delay time by Victor Zaccardo on 2016.03.25.

	- Modified
		- to correct extreme right and extreme bottom behavior,
		- to stay inside the screen whenever the tooltip might go out on the top but still the screen is higher than the tooltip,
		- to use the more flexible mouse positioning,
		- to add customizable background color, padding, waittime and wraplength on creation
		by Alberto Vassena on 2016.11.05.
		- border width and color for the tooltip, along with doctext for the class
		by WINRARisyou on 02/27/25

	Tested on Windows 11, running Python 3.13.1 64-bit
	
	:param tk.Widget widget: The widget the tooltip should be applied to
	:param str bg: The hex color or color name of the tooltip background
	:param tuple pad: A tuple of four integers representing the padding (left, top, right, bottom) around the tooltip text, e.g. `(5, 3, 5, 3)`
	:param str text: The text the tooltip should display
	:param str borderColor: The hex color or color name of the tooltip border
	:param int borderWidth: The width of the tooltip border
	:param int waittime: The amount of time in milliseconds before the tooltip is displayed
	:param int wraplength: The maximum line length in pixels
	"""

	def __init__(self, widget, bg="#FFFFEA", pad:tuple=(5, 3, 5, 3), text="Tooltip Text", borderColor:str=None, borderWidth=0, waittime=400, wraplength=250):
		self.waittime = waittime  # in miliseconds, originally 500
		self.wraplength = wraplength  # in pixels, originally 180
		self.widget = widget
		self.text = text
		self.widget.bind("<Enter>", self.onEnter)
		self.widget.bind("<Leave>", self.onLeave)
		self.widget.bind("<ButtonPress>", self.onLeave)
		self.bg = bg
		self.borderColor = borderColor
		self.borderWidth = borderWidth
		self.pad = pad
		self.id = None
		self.tw = None

	def onEnter(self, event=None):
		self.schedule()

	def onLeave(self, event=None):
		self.unschedule()
		self.hide()

	def schedule(self):
		self.unschedule()
		self.id = self.widget.after(self.waittime, self.show)

	def unschedule(self):
		id_ = self.id
		self.id = None
		if id_:
			self.widget.after_cancel(id_)

	def show(self):
		def tip_pos_calculator(widget, label, *, tip_delta=(10, 5), pad=(5, 3, 5, 3)):

			w = widget

			s_width, s_height = w.winfo_screenwidth(), w.winfo_screenheight()

			width, height = (pad[0] + label.winfo_reqwidth() + pad[2], pad[1] + label.winfo_reqheight() + pad[3])

			mouse_x, mouse_y = w.winfo_pointerxy()

			x1, y1 = mouse_x + tip_delta[0], mouse_y + tip_delta[1]
			x2, y2 = x1 + width, y1 + height

			x_delta = x2 - s_width
			if x_delta < 0:
				x_delta = 0
			y_delta = y2 - s_height
			if y_delta < 0:
				y_delta = 0

			offscreen = (x_delta, y_delta) != (0, 0)

			if offscreen:

				if x_delta:
					x1 = mouse_x - tip_delta[0] - width

				if y_delta:
					y1 = mouse_y - tip_delta[1] - height

			offscreen_again = y1 < 0  # out on the top

			if offscreen_again:
				# No further checks will be done.

				# TIP:
				# A further mod might automagically augment the
				# wraplength when the tooltip is too high to be
				# kept inside the screen.
				y1 = 0

			return x1, y1

		bg = self.bg
		pad = self.pad
		widget = self.widget

		# creates a toplevel window
		self.tw = tk.Toplevel(widget)

		# Leaves only the label and removes the app window
		self.tw.wm_overrideredirect(True)

		win = tk.Frame(self.tw, background=bg, borderwidth=0, highlightbackground=self.borderColor, highlightthickness=self.borderWidth)
		label = tk.Label(win, text=self.text, justify=tk.LEFT, background=bg, relief=tk.SOLID, borderwidth=0, wraplength=self.wraplength)

		label.grid(padx=(pad[0], pad[2]), pady=(pad[1], pad[3]), sticky=tk.NSEW)
		win.grid()

		x, y = tip_pos_calculator(widget, label)

		self.tw.wm_geometry("+%d+%d" % (x, y))

	def hide(self):
		tw = self.tw
		if tw:
			tw.destroy()
		self.tw = None