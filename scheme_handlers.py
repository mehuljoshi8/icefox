# icefox: just a better firefox

import io

'''
TODOS: [Major issues are in * while minor are i - ...]
 * Files that aren't suffixed with .html are treated as HTML files :(
	This applies to both files retrieved over the web and local files. 
 
 * Enable scrolling text (mouse)
 * Add additional support for more complex sites
 * Make the browser resizable
 * Enable zooming in both +/- directions.
 * Add additional support for files
 
 i. View-Source needs to be tackled
 ii. Data request handlers
 iii. Handle line breaks
'''

# The initial width and height of our browser gui
WIDTH, HEIGHT = 800, 600
# The height and width step for characters in our gui
HSTEP, VSTEP = 10, 16


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


# Need an update
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

# TODO needs an update
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
    
	res = ""
	if found_body:
		res =  body_output.getvalue()
	else:
		res = doc_output.getvalue()

	body_output.close()
	doc_output.close()
	print("in lex")
	print(found_body)
	return res

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
	print("text = ", text)
	for c in text:
		if c == '\n':
			cursor_y += VSTEP
			cursor_x = HSTEP
		if cursor_x >= WIDTH - HSTEP:
			cursor_y += VSTEP
			cursor_x = HSTEP
		display_list.append((cursor_x, cursor_y, c))
		cursor_x += HSTEP
	return display_list
