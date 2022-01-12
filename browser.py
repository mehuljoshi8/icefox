# Name: Mehul Joshi
# icefox: just a better version of firefox...
import socket
import ssl
import sys
import os
import io
import gzip

import tkinter

'''
TODOS: [Major issues are in * while minor are i - ...]
 * Enable scrolling text (buttons)
 * Enable scrolling text (mouse)
 * Add additional support for more complex sites
 * Make the browser resizable
 * Enable zooming in both +/- directions.

 i. View-Source needs to be tackled
 ii. Data request handlers
 iii. Handle line breaks
'''


# The initial width and height of our browser gui
WIDTH, HEIGHT = 800, 600
# The height and width step for characters in our gui
HSTEP, VSTEP = 10, 16


'''
The file_request_handler method handles the file scheme for icefox.
In general we call this method with a path that points to some
file/directory, prefixed with file://, on our computer and the
browser returns the contents of the file/directory. If the path is
not a valid path or the file doesn't open for some reason, we
raise an error. 
'''
def file_request_handler(path): 
	assert path.startswith("file://")
	path = path[len("file://"):]
	if os.path.exists(path):
		if os.path.isdir(path):
			# return a string with all the files in this dir
			res = io.StringIO()
			res.write(".\n")
			res.write("..\n")
			for f in os.listdir(path):
				res.write(f + "\n")
			return res.getvalue()
		elif os.path.isfile(path):
		    #  return the contents of this file
			mask = oct(os.stat(path).st_mode)[-3:]
			print ("permissions = ", mask)
			fd = open(path, "r")
			body = fd.read()
			fd.close()
			# right now I am just reading in the entire contents of the txt file
			# in one pass a better way to do it would be with seeking
			# so that we can have fast scrolling too :)
			return body
	else:
    	# Raise an exception here...
		return "File Not Found\nERR_FILE_NOT_FOUND"
 
'''
The data_request_handler method takes in a single parameter data
and given that it was prefixed with data:text/html we parse the data
and return html data without any of the tags. 

MINI TODO: 
 * There are more data schemes out there figure
   out which ones you want to include and update this method.
   See:
   1. https://en.wikipedia.org/wiki/Data_URI_scheme
   2. https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs
'''
def data_request_handler(data):
    # For now, I'm going to assume that the
    # data scheme can only take 1 form which is
    # text/html, just for the sake of convenience. 
    # and the general format will be: 
    # data:text/html,[my html data]
    data = data[len("data:text/html,"):]
    return lex(data)

'''
The unchunk method takes in some data that is chunked via
a chunked transfer encoding and returns the unchunked data
that can later be used to decompress and decode. 
For reference see: 
 1. https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Transfer-Encoding
 2. https://en.wikipedia.org/wiki/Chunked_transfer_encoding
'''
def unchunk(data):
    # TODO: write all the unchunking logic here...
    # the general algorithm would be to 
    # read how many bytes each chunk has and then
    # iterate through those many bytes adding it some
    # kind of variable. 
	print(data)
	bytes_stream = io.BytesIO(data)
	print(bytes_stream)
	while True:
		byte = bytes_stream.read(1)
		if not byte:
			break
		print(byte)

'''
The request method processes a url and returns
the headers and body from a given url according to
the HTTP/S. 
See for reference: 
 1. https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages
'''
def request(url): 
	scheme, url = url.split("://", 1)
	assert scheme in ["http", "https"], \
		"Unknown scheme {}".format(scheme)
	# the host is the part right after the scheme
	# and before the first / and the path
	# is everything after the first /
	host, path = url.split("/", 1)
	path = "/" + path
	# create a socket to communicate with that site
	# a socket is nothing more than a file descriptor for network
	# i/o. 
	s = socket.socket(
		family=socket.AF_INET,
		type=socket.SOCK_STREAM,
		proto=socket.IPPROTO_TCP,
	)
	# http usually uses port 443 for encrypted connections
	port = 80 if scheme == "http" else 443
	if ":" in host: 
		host, port = host.split(":", 1)
		port = int(port)
	s.connect((host, port))
	if scheme == "https": 
		ctx = ssl.create_default_context()
		s = ctx.wrap_socket(s, server_hostname=host)
	# Send the request to the socket
	# We are now on HTTP/1.1!!
	s.send(b"GET " + str.encode(path) + b" HTTP/1.1\r\n" +
		   b"Host: " + str.encode(host) + b"\r\n" + 
     	   b"Connection: close\r\n" + 
           b"User-Agent: icefox\r\n" + 
           b"Accept-Encoding: gzip\r\n\r\n")
	# get the response back
	# set the compression stuff here 
	response = s.makefile("rb", encoding="utf-8", newline="\r\n")
	# parse the response
	statusline = response.readline().decode() 
	version, status, explanation = statusline.split(" ", 2)
	assert status == "200", "{}: {}".format(status, explanation)
	# Create the headers
	headers = {}
	while True: 
		line = response.readline().decode()
		if line == "\r\n": break
		header, value = line.split(":", 1)
		headers[header.lower()] = value.strip()
	if 'content-encoding' in headers and headers['content-encoding'] == 'gzip':
		# print(response.read())
		# write a helper method to take care of the transfer-encoding being set to
		# chunk and call it here if the header has a transfer-encoding -> chunked.
		data = response.read()
		if 'transfer-encoding' in header and headers['transfer-encoding'] == "chunked":
			data = unchunk(data)
		body = gzip.decompress(data).decode()
	else:
		body = response.read().decode()
	s.close()
	return headers, body

'''
The lex_helper method...
'''
def lex_helper(c, stream, in_angle):
	if c == "&lt;":
		stream.write("<")
		return False
	if c == "&gt;": 
		stream.write(">")
		return False
	if c == "<":
		return True
	if c == ">":
		return False
	if not in_angle:
		stream.write(c)
		return False
	return True

'''
The lex method...
'''
def lex(body):
	body_output = io.StringIO()
	doc_output = io.StringIO()
	found_body = False
	in_body = False
	in_angle = False
	c = 0
	while c < len(body):
		if body[c: c + 6] == "<body>":
			c = c + 6
			in_body = True
			found_body = True
		elif body[c: c + 7] == "</body>":
			c = c + 7
			in_body = False
		else:
			s = body[c]
			# add support for the less-than and greater-than entities here
			if body[c: c + 4] == "&lt;" or body[c: c + 4] == "&gt;":
				s = body[c: c + 4]
				c = c + 3

			if in_body:
				in_angle = lex_helper(s, body_output, in_angle)
			in_angle = lex_helper(s, doc_output, in_angle)
			c = c + 1
    
	if found_body:
		return body_output.getvalue()
	else:
		return doc_output.getvalue()
  
	body_output.close()
	doc_output.close()

'''
The layout function takes in some text and determines where
on the screen each character on the screen is supposed to be rendered.
Note: it doesn't actually have to handle the rendering of each character on our gui. 

1. Figure out a way to enable scrolling through
   preloading the location of each character on the gui
   and then when a user scrolls we just have to figure out
   what's the "frame" that they are looking at of our slice. 
2. Then optimize...
'''
def layout(text):
	# one idea is to just bind each character 0 - len
	# to some position on our gui and that's all this function has to return. 
	display_list = []
	cursor_x, cursor_y = HSTEP, VSTEP
	for c in text:
		if c == '\n':
			cursor_y += VSTEP
			cursor_x = HSTEP
		if cursor_x >= WIDTH - HSTEP:
			cursor_y += VSTEP
			cursor_x = HSTEP
		if cursor_y >= HEIGHT - VSTEP:
			cursor_y = VSTEP
		display_list.append((cursor_x, cursor_y, c))
		cursor_x += HSTEP
	return display_list

# The Browser class is responsible for rendering the gui
class Browser: 
	def __init__(self):
		self.window = tkinter.Tk()
		self.canvas = tkinter.Canvas(
			self.window,
			width=WIDTH,
			height=HEIGHT
		)
		self.canvas.pack()
	
	'''
	The load method takes in a single parameter uri
	and attempts to load what that uri points to in
	our browser. 
 	'''
	def load(self, uri):
		if uri.startswith("file://"):
			self.render(lex(file_request_handler(uri)))
		elif uri.startswith("data:"):
			print(data_request_handler(uri))
		else: 
			header, body = request(uri)
			# Technically files can also be put underview source
			# but I am going to save that for a later exercise   	
			if uri.startswith("view-source:"):
				print(body)
			else:
				pos_lst = layout(lex(body))
				print(pos_lst)
				for pos in layout(lex(body)):
					self.canvas.create_text(pos[0], pos[1], text=pos[2])
	
	def render(self, s):
		# TODO: write a render function that can be used by all of the
		# schemes
		pos_lst = layout(s)
		print(pos_lst)
		cursor_x, cursor_y = HSTEP, VSTEP
		for c in s: 
			if c == "\n":
				cursor_y += VSTEP
				cursor_x = HSTEP
			if cursor_x >= WIDTH - HSTEP:
				cursor_y += VSTEP
				cursor_x = HSTEP
			self.canvas.create_text(cursor_x, cursor_y, text=c)
			cursor_x += HSTEP

if __name__ == "__main__": 
	Browser().load(' '.join(sys.argv[1:]))
	tkinter.mainloop()
