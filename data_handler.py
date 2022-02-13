# Returns the necessary data for the scheme handler. 

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
    return ""
