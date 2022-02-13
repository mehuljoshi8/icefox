# icefox
# browser.py contains the main driver code for our browser
# as well the main Browser class that is responsible for rendering
# the gui.

import sys

from utils import *
from file_handler import *
from web_handler import *
import tkinter

# The Browser class is responsible for rendering the gui
class Browser:
	SCROLL_STEP = 32
	def __init__(self):
		self.window = tkinter.Tk()
		self.canvas = tkinter.Canvas(
			self.window,
			width=WIDTH,
			height=HEIGHT
		)
		self.canvas.pack()
		self.scroll = 0
		self.window.bind("<Down>", self.scrolldown)
		self.window.bind("<Up>", self.scrollup)

	def scrolldown(self, e):
		if self.scroll < self.display_list[-1][1]:
			self.scroll += self.SCROLL_STEP
			self.draw()
  
	def scrollup(self, e):
		if self.scroll > 0:
			self.scroll -= self.SCROLL_STEP
			self.draw()
 
	def draw(self):
		self.canvas.delete("all")
		for x, y, c in self.display_list:
			if y > self.scroll + HEIGHT: continue
			if y + VSTEP < self.scroll: continue
			self.canvas.create_text(x, y - self.scroll, text=c)

	# The load method attempts to load a uri into our browser. 
	def load(self, uri):
		if uri.startswith("file://"):
			text = file_request_handler(uri)
			if uri.endswith(".html"):
				text = lex(text)
		elif uri.startswith("data:"):
			text = ""
			print(data_request_handler(uri))
		else:
			header, text = request(uri)
			if uri.endswith(".html"):
				text = lex(text)
		self.display_list = get_layout(text)
		self.draw()

if __name__ == "__main__": 
	Browser().load(' '.join(sys.argv[1:]))
	tkinter.mainloop()
