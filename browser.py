# Name: Mehul Joshi
# Dogzilla

import socket
import ssl

#############
# Requests information from a given path
#############
def request(url): 
	# if we are going to be adding support for opening files on my computer
	# I might need to think of the design of the existing code and how
	# introducing this new feature will clash with my existing code base. 
 
 
 
 	# get the scheme and url for the given "path"
	scheme, url = url.split("://", 1)
	
	# websites must be either http or https
	# adding support for file types
	assert scheme in ["http", "https"], \
		"Unknown scheme {}".format(scheme)
	
	# the host is the part right after the scheme
	# and before the first / and the path
	# is everything after the first /
	host, path = url.split("/", 1)
	path = "/" + path
	
	# create a socket to communicate with that site
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
           b"User-Agent: Amoli\r\n\r\n")
 
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

########
#  A very 1.0 version of rendering the HTML code
########
def show(body):
	in_angle = False
	for c in body:
		if c == "<":
			in_angle = True
		elif c == ">": 
			in_angle = False
		elif not in_angle: 
			print(c, end="")

###########
# Loads a given page into our "browser"
##########
def load(url):
    headers, body = request(url)
    show(body)

# This is python's version of a main function
if __name__ == "__main__": 
    import sys
    load(sys.argv[1])