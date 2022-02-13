# icefox
# browser.py contains the main driver code for our browser
# as well the main Browser class that is responsible for rendering
# the gui.

import sys

import utils
from file_handler import *
from web_handler import *
import tkinter

# The Browser class is responsible for rendering the gui
class Browser:
	SCROLL_STEP = 32
	cached_content = ""
	def __init__(self):
		self.window = tkinter.Tk()
		self.canvas = tkinter.Canvas(
			self.window,
			width=utils.WIDTH,
			height=utils.HEIGHT
		)
		self.canvas.pack()
		self.scroll = 0
		self.window.bind("<Down>", self.scrolldown)
		self.window.bind("<Up>", self.scrollup)
		self.window.bind("<Configure>", self.resize)

	def scrolldown(self, e):
		if self.scroll < self.display_list[-1][1]:
			self.scroll += self.SCROLL_STEP
			self.draw()
  
	def scrollup(self, e):
		if self.scroll > 0:
			self.scroll -= self.SCROLL_STEP
			self.draw()

	def resize(self, e):
		self.canvas.pack(fill="both", expand=True)
		utils.WIDTH = e.width
		utils.HEIGHT = e.height
		self.display_list = utils.get_layout(self.cached_content)
		self.draw()
		
	def draw(self):
		self.canvas.delete("all")
		for x, y, c in self.display_list:
			if y > self.scroll + utils.HEIGHT: continue
			if y + utils.VSTEP < self.scroll: continue
			self.canvas.create_text(x, y - self.scroll, text=c)

	# The load method attempts to load a uri into our browser. 
	def load(self, uri):
		self.uri = uri
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
				text = utils.lex(text)
		self.cached_content = text
		self.display_list = utils.get_layout(text)
		self.draw()

if __name__ == "__main__": 
	Browser().load(' '.join(sys.argv[1:]))
	tkinter.mainloop()
