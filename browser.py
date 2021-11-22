# Name: Mehul Joshi
# icefox: just a better version of firefox. 
import socket
import ssl
import sys
import os
import io

def main():
    load(' '.join(sys.argv[1:]))

#############
# Handles the file:// scheme
#############
def file_request_handler(path): 
	# but the general idea would be to add the file:/// scheme assuming
	# there are no nefarious users of this feature, meaning that
	# it always starts with file:///
	# if the scheme is file:///
	# 		i >  there is no "host"
	# 		ii > so instead just find a way to read/print out the contents
	# 				of the file/directory that we are pointing to (very 333 like)
	assert path.startswith("file://")
	path = path[len("file://"):]
	# complete the rest of this method with posix
	# so the basic idea is open the file that we are pointing to
	# check if the file is a directory
	# if it is a directory, print out the contents of that directory
	# otherwise it's a file so try to print out the contents of that file. 
	if os.path.exists(path):
		if os.path.isdir(path):
			print(".")
			print("..")
			for f in os.listdir(path):
				print(f)
		else: # the path points to a file so print out the result
			file_o = open(path)
			body = file_o.read()
			file_o.close()
			return show(body)
	else:
    	# Technically a query processor wouldn't be the best thing here
		# but i do have an idea of adding another scheme
		# with a query processor that allows
		# users to search information from
		# a directory given a search phrase. 
		print("file doesn't exist")
 
############
# Handles the data:* scheme. 
############
def data_request_handler(data):
    # For now, I'm going to assume that the
    # data scheme can only take 1 form which is
    # text/html, just for the sake of convenience. 
    # and the general format will be: 
    # data:text/html,[my html data]
    data = data[len("data:text/html,"):]
    return show(data)

#############
# Requests information from a given url
#############
def request(url): 
	# get the scheme and url for the given "path"
	scheme, url = url.split("://", 1)
	
	# websites must be either http or https
	# adding support for file types
	print(url)
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
           b"User-Agent: icefox\r\n\r\n")
 
	# get the response back
	response = s.makefile("r", encoding="utf-8", newline="\r\n")

	# parse the response
	statusline = response.readline()
	version, status, explanation = statusline.split(" ", 2)
	assert status == "200", "{}: {}".format(status, explanation)

	# Create the headers
	headers = {}
	while True: 
		line = response.readline()
		if line == "\r\n": break
		header, value = line.split(":", 1)
		headers[header.lower()] = value.strip()

	# Read the rest of the body
	body = response.read()
	# Close the socket
	s.close()
	return headers, body

def show_helper(c, stream, in_angle):
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

########
#  A very 1.0 version of rendering the HTML code
########
def show(body):
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
				in_angle = show_helper(s, body_output, in_angle)
			in_angle = show_helper(s, doc_output, in_angle)
			c = c + 1
    
	if found_body:
		return body_output.getvalue()
	else:
		return doc_output.getvalue()
  
	body_output.close()
	doc_output.close()


###########
# Loads a given scheme into our "browser"
##########
def load(url):
	if url.startswith("file://"):
		print(file_request_handler(url))
	elif url.startswith("data:"): 
		print(data_request_handler(url))
	else: 
		headers, body = request(url)
		if url.startswith("view-source:"):
			print(body)
		else: 
			print(show(body))

# This is python's version of a main function
if __name__ == "__main__": 
	main()    
