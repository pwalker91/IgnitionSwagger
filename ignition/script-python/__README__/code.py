#This script module is simply for reference to someone using this project.
"""

# Assumptions:
 * Root WebDev resource maps to a Script Package, which contains all of the possible endpoints
 * WebDev resource will always be just the first part of URI (the "base")
 ** Affects how magic finds script resources
 * No WebDev resource folders
 * Path Params are assumed required
 ** cannot guarantee processing of "extra" path params
 * Hyphens '-' are allowed in path to "HTTP resource", and should be used instead of underscores '_'
 * no file extensions in name of script resource
 ** logic should read `wdr.swag['file-extension']` to determine what to do
 * No top-level Script Resources named after HTTP Methods
 ** processing looks for "classes" with a name like an HTTP method, which assumes it will find a Script resource
 * allows 'x-http-method-override'
 ** If a request comes in with the header set, the "override" will be searched for


# Creating a new Endpoint:
 * Create a series of Script Packages with the name you wish to use
 ** Define "Path Params" following the required format
 ** If Package is an endpoint, define Script resource inside named '__logic__'
 ** Script should define a class named as the HTTP method (all caps), which itself contains a function
 ** @staticmethod
    def __do__(wdr, LOGGER):
 ** REFERENCE: _swagger2_.statics for name of prefix, script resource, and function name
 * Logger shows up as "Endpoint.[METHOD]__[path]" (with '/' in path replaced by '_')
 * Define Swagger (refer to https://swagger.io/specification/v2/) in HTTP Method class
   as a dictionary. Variable should be named 'SWAGGER' (reference statics)
 ** Swagger MUST define some auth to use. If endpoint is to be publicly available, use a function that
    always returns a "true".
 * Use __swagger2__.responses to build a "response" (ie. JSON or HTTP Status Code)
 * Can set Swagger's keys `parameters` and `reponses` to `None` if there is not validation necessary
 * Set headers in response requires interfacing with the original Java Servlet Response
 ** wdr.request['servletResponse'].setHeader(STRING, STRING)


## Script Resources Needed:
 * packages only
 * "__logic__"
 * "[PREFIX]-[DATA_TYPE]-[URI_PARAM_NAME]"



# Basic and Custom Swagger Keys:
...





"""


from __swagger2__ import requests as swagRq
from __swagger2__ import responses as swagRsp
from __swagger2__ import statics as swagStc
PREFIX = swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX



class ExampleHttpMethodClasses:
	
	class HTTP_METHOD_NAME: #eg. GET, POST, DELETE, PATH, OPTIONS
		SWAGGER = {
			# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
			# CUSTOM KEYS FOR IA PURPOSES
			# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
			#Authentication method(s) [function and extra keyword args].
			#PyList of PyDictionaries: At least ONE method must be defined.
			PREFIX+'auth': [
				{
					'method': FUNCTION,
					'extraArgs': {
						'<KEYWORD PARAMETER>': '<VALUE>'
					}
				},
			],
			#Boolean (default=False): Whether to hide this endpoint definition from API consumers but not including it in
			# the 'swagger.json'. If this key is set to [True], then the none of the Swagger keys are required, unless you
			# want to enforce a specific format or clean up the incoming data/outgoing response.
			PREFIX+'hide': False,
			#Boolean (default=True): Whether to validate (and clean up) the incoming data using the definition in the
			# `parameters` key of this Swagger.
			PREFIX+'validateRequest': True,
			#Boolean (default=True): Whether to validate (and clean up) the generated response using the definition in
			# the `responses` key of this Swagger.
			PREFIX+'validateResponse': True,
			#String (no default): The ReDoc "tag group" that this endpoint belongs to.
			PREFIX+'tagGroup': 'Tests',
			#Dictionary : Custom headers to add to every response. Every key should map to a String. This is helpful when
			# your endpoints need to include the CORS headers. (https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
			PREFIX+'includeHeaders': {
				'My-Custom-Header': 'value'
			},
		
			# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
			# ACTUAL SWAGGER DEFINITION
			# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
			#String: Unique string across all endpoints defined by the API. Only letters (upper and lower) and underscores
			'operationId': 'base_http_method',
			#String: Human readable summary (ie. Title)
			'summary': 'Example HTTP Method Definition',
			#String: Human readable description of the purpose of the endpoint
			'description': '''An example HTTP Method Definition, following the Swagger 2.0 Definition Standards.''',
			#PyList of Strings: A list of tags, telling the doc generation method that this endpoint relates to other
			# endpoints with the same tag.
			'tags': [
				'Example'
			],
			#PyList of Strings: A list of the Content Types that this endpoint will accept. This should only include String
			# values that can be found as keys in 'statics.VALID_CONTENT_TYPES'
			'consumes': [
				'application/json',
				'application/x-www-form-urlencoded',
			],
			#PyList of Strings: A list of the Content Types that this endpoint will produce
			'produces': [
				'application/json',
			],
			#Boolean: Declares this operation to be deprecated
			'deprecated': False,
			
			#PyList of PyDictionaries: The accepted types of authentication for the endpoint
			'security': [],
		
			# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
			#PyList of PyDictionaries: The definition of the parameters to this endpoint.
			# For the acceptable values for the `in` properties of parameter definitions,
			# see the `statics.VALID_SWAGGER_IN` dictionary.
			'parameters': [
				# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
				# HEADER
				# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
				{
					'description': 'Example Header Parameter',
					'in': 'header',
					'name': 'Custom-IS-Header',
					#The `type` must be one of the allowed values as defined in statics.VALID_SWAGGER_TYPES['header']
					'type': 'string',
					'required': False,
					#Custom key for our purposes, which is used when the request is logged to the database. If the incoming
					# data is sensitive and we don't want it logged, this will change the value to the string 'REDACTED' before
					# saving it to the database.
					PREFIX+'obscure': True,
					'example': '12345678-abcd-44bb-a83e-abcd1234de52',
				},
				# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
				# URL QUERY
				# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
				{
					'description': 'Example Query Integer argument',
					'in': 'query',
					'name': 'arg1',
					#Note that, while information coming from a URL query is always a "string", the data validation that is
					# done when `ia-validateRequest` is True will do some type casting.
					'type': 'integer',
					'required': True,
					PREFIX+'obscure': True,
					'example': 42,
				},
				{
					'description': 'Example Query String argument',
					'in': 'query',
					'name': 'arg2',
					'type': 'string',
					'required': False,
					PREFIX+'obscure': False,
					#If the parameter is not required, you can specify a default. If a value for the parameter is not
					# provided by the callee, then the "default" value will be copied in to the data.
					'default': 'hello world',
					'example': 'hello world',
				},
				{
					'description': 'Example Query String argument',
					'in': 'query',
					'name': 'arg3',
					'type': 'array',
					'required': False,
					'items': {
						'name': 'listArg',
						'description': 'Arg in a List',
						'type': 'integer',
					},
					#Supported collection formats are 
					#	- csv - comma separated values. EG. foo,bar
					#	- tsv - tab separated values. EG. foo\tbar
					#	- pipes - pipe separated values. EG. foo|bar
					'collectionFormat': 'csv',
					PREFIX+'obscure': False,
					'default': [1,2,3,4],
					'example': '1,2,3,4',
				},
				# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
				# BODY
				# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
				{
					'in': 'body',
					'schema': {
						'type': 'object',
						'properties': {
							'arg_string': {'type': 'string',},
							'arg_boolean': {'type': 'boolean',},
							'arg_date': {'type': 'string', 'format': 'datetime', 'example': '2019-01-01T00:00:00 -08:00'},
							'arg_date2': {'type': 'string', 'format': 'date', 'x-nullable': True, 'example': '2019-01-01'},
							'arg_int': {'type': 'integer',},
							'arg_float': {'type': 'number', 'format': 'float'},
							'arg_array': {
								'type': 'array',
								'items': {'type': 'integer', 'title': 'Numbers',},
							},
							'arg_object': {
								'type': 'object',
								'title': 'Simple Object',
								'properties': {
									'arg_string': {'type': 'string'},
									'arg_int': {'type':'integer'},
									'arg_obj_array': {
										'type': 'array',
										'items': {
											'type': 'object',
											'title': 'Special Items',
											'properties': {
												'arg_obj_item_string': {'type': 'string'},
												'arg_obj_item_int': {'type':'integer'},
											},
											'required': ['arg_obj_item_string','arg_obj_item_int'],
										},
									},
								},
								'required': ['arg_string', 'arg_int','arg_obj_array'],
							},
						},
						'required': [
							'arg_string','arg_boolean','arg_int'
						],
					},
				},
			],
		
			# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
			#Python Dictionary of (HTTP Response Code => PyDictionaries): The definiton of the expected HTTP response.
			# The keys are expected to be HTTP Response Codes (as Strings) that map to a single Python Dictionary that
			# defines the structure and format of the data being returned.
			# The `default` key is meant to be the "default" response that the server will return. Our convention is, if
			# the endpoint can return a JSON Object for when the request was "unsuccessful", the 'default' key is defined
			# to reference the "failure response" definition.
			# The "failure response" (ie. 'default') will need to have the following keys/values:
			#	- success = False
			#	- status = "FAILURE"
			#	- message = "<THE REASON THE REQUEST FAILED>"
			'responses': {
				'200': {
					'description': '**SUCCESS** (returns HTTP Status `OK`)',
					'schema': {
						'type': 'object',
						'properties': {
							'success': {'type': 'boolean', 'enum': [True]},
							#If you want the status to accept values other than 'SUCCESS', simply add them
							# to the `enum` PyList.
							'status': {'type': 'string', 'enum': ['SUCCESS']},
							'arg_a': {'type': 'integer'},
							'arg_b': {'type': 'string'},
						},
						'required': ['success','status'],
					},
					'examples': {
						"application/json": {
							'success': True,
							'status': 'SUCCESS',
						}
					},
				},
				'default': {'$ref': '#/definitions/objs_failure_response'},
			}
		}
		
		@staticmethod
		def __do__(wdr, logger):
			'''
			@FUNC	The actual, ACTUAL logic of a REST endpoint, where we assume that the request has been vetted, cleaned up,
					authenticated, authorized, etc.
			@PARAM	wdr : WebDevRequest object. All of the relevant data will be in `wdr.swag`, but one
							can still access the original information.
			@PARAM	logger : Gateway Logger, assumed to be defined by the `BaseEndpoint` object.
			@RETURN	Python Dictionary, a WebDev Response that a WebDev Resource can return. The valid keys are:
					 - 'html' - HTML source as a String.
					 - 'json' - A Python Dictionary which will be encoded as 'application/json' data.
					 - 'file' - A file path to send as the response.
					 - 'bytes' - A byte[] to send back. The content type will be 'application/octet-stream' if not specified.
					 - 'response' - Any type of plain text response.
					 - 'contentType' - The mime type. Need only if ambiguous.
			'''
			return {'response': '42 is the answer'}
		#END DEF
	#END CLASS
#END CLASSes