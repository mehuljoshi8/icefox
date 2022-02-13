# utils.py contains all the important utilities for the browser and
# scheme handlers.

import io

# The initial width and height of our browser gui
WIDTH, HEIGHT = 800, 600
# The height and width step for characters in our gui
HSTEP, VSTEP = 10, 16

# The get_layout method takes in some text string
# and returns the layout of each character relative to
# the current size of the browser
def get_layout(text):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
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

# The lex_helper_method is used to help
# parse the html passed into the lex method
def __lex_helper(c, stream, in_angle):
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

# The lex method takes in the html and parses it
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
				in_angle = __lex_helper(s, body_output, in_angle)
			in_angle = __lex_helper(s, doc_output, in_angle)
			c = c + 1
    
	res = ""
	if found_body:
		res =  body_output.getvalue()
	else:
		res = doc_output.getvalue()

	body_output.close()
	doc_output.close()
	return res