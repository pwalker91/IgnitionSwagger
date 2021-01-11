'''
	A set of "simple" authentication methods
'''

def allowAll(wdr, *args, **kwargs):
	'''A simple API Authentication method that simply allows all'''
	return {'success': True, 'message':'I do absolutely nothing!'}
#END DEF

def allowWithApiKeyHeader(wdr, headerName, keyValue, *args, **kwargs):
	'''
	@FUNC	A simple API Authentication method that allows if the specified value is in the specified header
	@PARAM	wdr : WebDevRequest object
	@PARAM	headerName : String, the name of the header expected to contain a special authentication value
	@PARAM	keyValue : String, the secret value expected in the header
	'''
	#Since headers are supposed to be case-insensitive, we will convert the given header name to lowercase and
	# check the dictionary in the `swag` property that contains all of the headers with the name lowercased.
	if headerName.lower() not in wdr.swag['headers-lc']:
		return {'success': False, 'message':"Did not provide a value in the header `{!s}`".format(headerName)}
	if wdr.swag['headers-lc'][headerName.lower()] != str(keyValue):
		return {'success': False, 'message':"Given authentication value did not match the expected value."}
	return {'success': True, 'message':'You gave the correct value!'}
#END DEF

def allowNone(wdr, *args, **kwargs):
	'''A simple API Authentication method that allows no one'''
	return {'success': False, 'message':'I prevent ANYONE from doing anything!'}
#END DEF