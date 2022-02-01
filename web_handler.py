# handles all the data that is coming through the web
import socket
import ssl

import gzip

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
