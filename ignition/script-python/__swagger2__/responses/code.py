'''
	This script contains helper functions for generating JSON responses or specific HTTP Status Code responses.
'''

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# IMPORTS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import httplib
import copy
import types



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# LOGGER and CONSTANTS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
LIBRARY_LOGGER = server.getLogger("IgnitionSwagger2.responses")

# https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
HTTP_CODE_STATUSES = copy.deepcopy(httplib.responses)
HTTP_CODE_STATUSES.update({418: "I'm a Teapot"})
HTTP_CODE_STATUSES.update({218: "Coffee Brewing"})
#https://en.wikipedia.org/wiki/April_Fools%27_Day_Request_for_Comments
#https://tools.ietf.org/html/rfc2324
HTTP_TEXT_STATUSES = dict([ (HTTP_CODE_STATUSES[code].lower(), code) for code in HTTP_CODE_STATUSES ])



def json(status='SUCCESS', success=True, message=None, data={}):
	'''
	@FUNC	Returns the status/message in the standard WebDev JSON object format
	@PARAM	status : String, the status to return in the JSON object. Will be uppercased [DEFAULT: "SUCCESS"]
	@PARAM	success : Boolean, whether the response returned is a success or failure (for easy testing) [DEFAULT: True]
	@PARAM	message : String, the message to return in the JSON object [DEFAULT: None]
	@PARAM	data : PyDictionary, keys/values to include in the JSON response [DEFAULT: {}]
	@RETURN	PyDictionary, a WebDev JSON response
	'''
	logger = LIBRARY_LOGGER.getSubLogger('json')
	logger.trace("Creating base dictionary structure...")
	values = {
		"status": status.upper(),
		"success": bool(success)
	}
	if message is not None:
		values['message'] = str(message)
	##Note that we created our PyDictionary 'values' above, rather than simply adding the values to 'data'. This is
	## because we want to leave it up to the developer what values they want to put in status/message/success, in case
	## they want to overwrite the value/value-type that is put in there by default.
	logger.trace("Combining base structure with given data")
	if not isinstance(data, types.DictionaryType):
		raise Exception("`data` must be a Dictionary")
	values.update(data)
	logger.trace("Returning final JSON response")
	return {'json': values}
#END DEF

def httpStatus(request, status):
	'''
	@FUNC	Sets the HTTP status code to the given value, and returns a simple WebDev 'response'
	@PARAM	request : WebDev Request object
	@PARAM	status : Integer/String, the HTTP Code (Integer) or Status (String)
	@RETURN	PyDictionary, the WebDev 'response'
	'''
	logger = LIBRARY_LOGGER.getSubLogger('httpStatus')
	logger.trace("Given HTTP Status = {!r}".format(status))
	code = status
	text = status
	if isinstance(text, types.StringTypes):
		logger.trace("Status is a String. Getting Integer code")
		code = HTTP_TEXT_STATUSES.get(text.lower(), None)
	elif isinstance(code, types.IntType):
		logger.trace("Status is an Integer. Getting String text")
		text = HTTP_CODE_STATUSES.get(code, None)
	else:
		raise Exception("Somehow got an HTTP status that is neither a String or Integer. Got a {!s}".format(type(status)))
	if code is None or text is None:
		raise Exception("Failed to find Text and Code Status based on given input {!r} ({!s})".format(status, type(status)))
	logger.trace("Extracting Servlet Response object")
	servlet = request['servletResponse']
	logger.trace("Setting Servlet Response's Code")
	servlet.setStatus(code)
	logger.trace("Returning 'response' text")
	return {'response': '{} {}'.format(code, text)}
#END DEF

def setHeader(request, header, value):
	'''
	@FUNC	Sets a header on the HHTP response
	@PARAM	request : WebDev Request object
	@PARAM	header : String, the header to set
	@PARAM	value : String, the header's value
	@RETURN	N/A
	'''
	logger = LIBRARY_LOGGER.getSubLogger('setHeader')
	logger.trace("Given Header/Value of '{!s}'/'{!s}'".format(header, value))
	request['servletResponse'].setHeader(header, value)
	logger.trace("Header set.")
#END DEF