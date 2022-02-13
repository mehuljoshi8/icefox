# handles all the data that is coming through the web
import socket
import ssl
import io

import gzip

# The get_chunk_size method takes in a bytes stream
# and returns the chunk_size of a given block
def __get_chunk_size(stream): 
		hex_string = ""
		prev_byte = None
		curr_byte = None
		while True:
			curr_byte = stream.read(1)
			if prev_byte == b'\r' and curr_byte == b'\n':
				break
			if not curr_byte == b'\r':
				hex_string += curr_byte.decode()
			prev_byte = curr_byte
		return int(hex_string, 16)

'''
The unchunk method takes in some data that is chunked via
a chunked transfer encoding and returns the unchunked data
that can later be used to decompress and decode. 
For reference see: 
 1. https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Transfer-Encoding
 2. https://en.wikipedia.org/wiki/Chunked_transfer_encoding
'''
def __unchunk(data):
	bytes_stream = io.BytesIO(data)
	bytes_read = 0
	unchunked_data = b''
	while True:
		chunk_size = __get_chunk_size(bytes_stream)
		if chunk_size == 0:
			break
  		# also read two additional bytes for the \r\n
		for i in range(0, chunk_size):
			byte = bytes_stream.read(1)
			unchunked_data += byte
		bytes_stream.read(2)
	return unchunked_data

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
	data = response.read()
	if 'content-encoding' in headers and headers['content-encoding'] == 'gzip':
		if 'transfer-encoding' in headers and headers['transfer-encoding'] == "chunked":
			data = __unchunk(data)
		body = gzip.decompress(data).decode(errors="replace")
	else:
		body = data.decode()
	s.close()
	return headers, body
