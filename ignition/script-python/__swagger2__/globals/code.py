'''
	This script module contains some of the global information that dictates how the server will validate
	incoming data or parse HTTP body content.
'''

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# IMPORTS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import system
import sys
import types
import re
from collections import OrderedDict
import pprint
import java.lang.Exception
import java.lang.Double
import java.util.Date



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# LOGGER and CONSTANTS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
LIBRARY_LOGGER = server.getLogger("IgnitionSwagger2.globals")



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# CLASSES and STATIC VARIABLES
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class dataParsers:
	'''
	@CLASS	This class is where we define sub-classes that provide some format validation of incoming request data
	'''
	
	class Type_JSON:
		'''
		@CLASS	Validation and parsing of Request data when given in the format JSON
		'''
		
		@staticmethod
		def isvalid(obj):
			'''
			@FUNC	Validates if the given object is "JSON", which (for our purposes) means a Python Dictionary
			@PARAM	obj : Object
			@RETURN	Boolean, True if the given Object is a Python Dictionary.
			'''
			return isinstance(obj, types.DictionaryType)
		#END DEF
		
		@staticmethod
		def parse(request):
			'''
			@FUNC	Using the given WebDev Request Python Dictionary, parses the body as JSON. Assumes that
					the original data is still in the HTTP Servlet Request's Buffered Reader.
			@PARAM	request : WebDev Request Python Dictionary
			@RETURN	Python Dictionary of parsed data. Keys include:
					- 'data' : Should be a Python Dictionary, but could be a String
					- 'original-body' : String, the original HTTP Body
			'''
			logger = LIBRARY_LOGGER.getSubLogger('dataParsers.Type_JSON__parse')
			logger.trace("Starting parsing of data as JSON")
			bReader = request['servletRequest'].getReader() #Gets a buffered reader for the body of the request
			body = ''
			line = bReader.readLine()
			while line is not None:
				body += line+"\n"
				line = bReader.readLine()
			#END WHILE
			logger.trace("Read the body as {!r}".format(body))
			#Returning both the parsed data and the original data, in case the endpoint implementation
			# needs to access the original content.
			res = {
				'data': system.util.jsonDecode(body),
				'original-body': body
			}
			logger.trace("Returning {!r}".format(res))
			logger.trace("res['data'] is {!s}".format(type(res['data'])))
			return res
		#END DEF
		
	#END CLASS
	
	class Type_URLEncoded:
		'''
		@CLASS	Validation and parsing of Request data when given in the format URL Encoded
		'''
		
		@staticmethod
		def isvalid(obj):
			#Assumes that Ignition already did everything it needed to parse the URL encoded data
			return True
			#return isinstance(obj, types.DictionaryType)
		#END DEF
		
		@staticmethod
		def parse(request):
			#If `parse` happens to be called, we'll just return the already-present data
			return {
				'data': copy.deepcopy(request['data']),
				'original-body': request['data'],
			}
		#END DEF
		
	#END CLASS
	
	class Type_FormData:
		'''
		@CLASS	Validation and parsing of Request data when given in the format Form Data
		'''
		
		@staticmethod
		def isvalid(obj):
			#Assumes that Ignition already did everything it needed to parse the URL encoded data
			return True
			#return isinstance(obj, types.DictionaryType)
		#END DEF
		
		@staticmethod
		def parse(request):
			#If `parse` happens to be called, we'll just return the already-present data
			return {
				'data': copy.deepcopy(request['data']),
				'original-body': request['data'],
			}
		#END DEF
		
	#END CLASS
	
	class Type_TextPlain:
		'''
		@CLASS	Validation and parsing of Request data when given in the format Plain Text
		'''
		
		@staticmethod
		def isvalid(obj):
			return isinstance(obj, types.StringTypes)
		#END DEF
		
		@staticmethod
		def parse(request):
			#If `parse` happens to be called, we'll just return the already-present data
			return {
				'data': copy.deepcopy(request['data']),
				'original-body': request['data'],
			}
		#END DEF
		
	#END CLASS
#END CLASSes



#The valid content types that we will accept, with references to the functions that
# determine if the data was correctly parsed by the WebDev Module, and how to parse if not
VALID_CONTENT_TYPES = {
	'application/json': dataParsers.Type_JSON,
	'application/x-www-form-urlencoded': dataParsers.Type_URLEncoded,
	'multipart/form-data': dataParsers.Type_FormData,
	'text/plain': dataParsers.Type_TextPlain,
	## NOT CURRENTLY IMPLEMENTED
	#'application/xml': None,
	#'application/octet-stream': None,
	#'text/html': None,
}

#The valid Content Types that the different HTTP Methods we implement will accept. If the HTTP
# Method maps to `None`, then any Content Type can be provided, and no limitations will be placed
# on what incoming data the Swagger Magic will allow to get to the actual endpoint logic.
#Use a `.keys()` call to determine the valid HTTP Methods that can be called, either directly
# or by specifying in the header 'X-HTTP-Method-Override'
VALID_METHODS = OrderedDict([
	#You'll notice that this is an Ordered Dictionary. I wanted to maintain an "order" to the HTTP
	# Methods defined in this dictionary. And to maintain that order, I need to initialize the
	# Ordered Dictionary using a list of tuples, and NOT a Dictionary.
	('GET',		None),
	('POST',	['application/json', 'application/x-www-form-urlencoded', 'multipart/form-data', 'text/plain']),
	('PUT',		['application/json', 'application/x-www-form-urlencoded', 'multipart/form-data', 'text/plain']),
	('PATCH',	['application/json', 'application/x-www-form-urlencoded', 'multipart/form-data', 'text/plain']),
	('DELETE',	['application/json', 'application/x-www-form-urlencoded', 'multipart/form-data', 'text/plain']),
	('HEAD',	None),
	('OPTIONS',	None),
	('TRACE',	None),
])

#In Swagger, the "in" field on a parameter definition defines where the data is
# excepted to be found in `WebDevRequest.swag`
VALID_SWAGGER_IN = OrderedDict([
	#('path',	'pathParams'),
	('header',	'headers'),
	('query',	'params'),
	('formData', 'data'),
	('body',	'data'),
])

#The valid Swagger Data Types that are allowed at a specfic data location (ie. the "in"
# portion of the parameter definition).
VALID_SWAGGER_TYPES = {
	'path':		['string', 'integer'],
	'header':	['string', 'integer', 'number', 'boolean'],
	'query':	['string', 'integer', 'number', 'boolean', 'array'],
	'formData':	['string', 'integer', 'number', 'boolean', 'array'],
	'body':		['string', 'integer', 'number', 'boolean', 'array', 'object'],
}

VALID_SWAGGER_ARRAY_COLLECTION_FORMATS = {
	'csv':		{'delimiter': ',', 'name': 'Comma-separated Values'},
	'ssv':		{'delimiter': ' ', 'name': 'Space-separated Values'},
	'pipes':	{'delimiter': '|', 'name': 'Pipe-separated Values'},
}

VALID_SWAGGER_DATE_FORMATS = dateFormat = {
	'date': "yyyy-MM-dd",
	'datetime': "yyyy-MM-dd'T'HH:mm:ss XXX",
}

#Most of the allowed data types have some simple Swagger Keys that define what values are allowed.
# This dictionary defines what those simple keys are, and what Python type the value should be.
BASIC_PARAMETER_FIELDS = {
	'array': {
		'minItems': {
			'required': False,
			'valueType': types.IntType,
		},
		'maxItems': {
			'required': False,
			'valueType': types.IntType,
		},
		'uniqueItems': {
			'required': False,
			'valueType': types.BooleanType,
		},
	},
	'integer': {
		'minimum': {
			'required': False,
			'valueType': types.IntType,
		},
		'maximum': {
			'required': False,
			'valueType': types.IntType,
		},
		'exclusiveMinimum': {
			'required': False,
			'valueType': types.BooleanType,
		},
		'exclusiveMaximum': {
			'required': False,
			'valueType': types.BooleanType,
		},
	},
	'string': {
		'format': {
			'required': False,
			'valueType': types.StringTypes,
			'allowedValues': ['byte', 'date', 'datetime']
		},
		'minLength': {
			'required': False,
			'valueType': types.IntType,
		},
		'maxLength': {
			'required': False,
			'valueType': types.IntType
		},
		'pattern': {
			'required': False,
			'valueType': types.StringTypes
		},
	},
	'number': {
		'format': {
			'required': True,
			'valueType': types.StringTypes,
			'allowedValues': ['float', 'long', 'double'],
			'default': 'float'
		},
		'minimum': {
			'required': False,
			'valueType': (types.IntType, types.LongType, types.FloatType, java.lang.Double),
		},
		'exclusiveMinimum': {
			'required': False,
			'valueType': types.BooleanType,
		},
		'maximum': {
			'required': False,
			'valueType': (types.IntType, types.LongType, types.FloatType, java.lang.Double),
		},
		'exclusiveMaximum': {
			'required': False,
			'valueType': types.BooleanType,
		},
		#TODO!
		#'multipleOf': {},
	},
}