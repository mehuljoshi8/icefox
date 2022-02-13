# The file_request_handler is responsible for handling all
# the transactions involving some local path on the users
# computer. 
import os
import io

'''
TODO: Once styling is applied to the browser, 
need to update to return links that can be clicked.
'''

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
			fd = open(path, "r")
			content = fd.read()
			fd.close()
			return content
	else:
    	# Raise an exception here...
		return "File Not Found\nERR_FILE_NOT_FOUND"
