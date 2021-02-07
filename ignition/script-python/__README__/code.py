"""

HELLO! Welcome to your API Service, hosted on an Ignition Gateway.

This project allows you to design API Endpoints that adhere to the OpenApi 2.0 Specification (aka Swagger).
API Endpoints created in this project can take advantage of automatic variable typing and validation, central
security checkpoints for multiple endpoints, automatic logging, version control within the Ignition ecosystem,
and anything else you could imagine.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

There are a few assumptions being made in this project that you will need to aware of.

	1.	All Endpoints are Script Resources. We are essentially hijacking the Script Resource area as our central
		repository of all API endpoint magic and structure.
		This is because we can use type-testing to determine when we have found an Endpoint.
	2.	In the WebDev section of the project, you will find a WebDev Resource that contains the following code
		for all possible HTTP Methods.
			```
			return __swagger2__.requests.processRequest(request, session)
			```
		This WedDev Resource MUST exist at the root level, and absolutely MUST map to a top-level Script Package
		Resource in the Project's Package Library.
		In this example project, you will notice how there exists a `v1` WebDev Resource and a `v1` Script Package
	3.	The WebDev Resource will be part of the "base" of the URL of every API Endpoint.
		In this example project, this means that every URL will be structured like so...
			http://mygateway:8088/system/webdev/IgnitionSwagger/v1/____
	4.	Multiple WebDev Resources are allowed, as long as the appropriate Script Package Resource is created.
		This means that you could create a `v2` WebDev Resource that maps to a `v2` Script Package containing
		a completely new generation of API Endpoints.
	5.	When creating new Endpoints, you will be creating new Script Package Resources underneath the "root" Package.
		Each Package can contain yet more packages. What defines an Endpoint is the existance of a Script Resource
		named `__logic__`.
			a.	The naming of this resource is dictated by the Variables in the `statics` Script Resource. This
				Script Resource will need to exist under the "root" Script Package.
			b.	Similarly, there are "definitions" that Swagger will expect. This includes information about
				what HTTP protocols are allowed, security definitions, generic contact info about the API service,
				and other Swagger stuff.
				You will need to create a `definitions Script Resource under the "root" Script Package.
	6.	Hyphens '-' are absolutely allowed in Script Package names, and should be used instead of underscores '_'.
	7.	Path Parameters are defined by created a specifically name Script Package Resource. The format is as follows:
			`[CUSTOM_PREFIX]-[SWAGGER_PRIMITIVE_TYPE]-[VARIABLE_NAME]`
		An example of an Integer Path parameter, using the default Custom Prefix, would be as follows
			`is-x-integer-myCustomPathParam`
		The Custom Prefix is defined in the `(root).statics` Script Resource's variable `IGNITION_SWAGGER_CUSTOM_PREFIX`.
	8.	The Endpoint's Script Package Resource should NOT contain any file extensions.
		Instead, the Script Package's `__logic__` Resource should be written such that it reads the file extension given
		and constructs its response accordingly.
		The logic should make use of `wdr.swag['file-extension']` to determine the requested response file type.
	9.	Do not name any Script Package Resources or Script Resources after HTTP Methods. This will conflict with how
		the Swagger Magic determines when it has found an API Endpoint.
	10.	This implementation of Swagger allows for requests to set the `X-HTTP-Method-Override` Header.
		For example, if a request is sent using the POST method, but defines the `X-HTTP-Method-Override` Header
		as PURGE, then the Swagger Magic will look for an implementation of the PURGE method.




- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

Please follow the guidance below when creating a new API Endpoint.


## 1. Create Script Package Resources for Path.
The path to an Endpoint's logic is determined by a series of Script Package resources. For example, if you were
creating an endpoint for the path `/v1/my/endpoint/thing`, there would exist the following Script Packages:
	-> v1
		|--my
			|--endpoint
				|--thing
					|--__logic__
Underneath the `thing` Script Package, the `__logic__` Script Resource would exist, which will contain all of the
logic that actually does something of value.

#### Path Params
When creating an endpoint that needs validated URL Path Parameters, you will need to define Script Package
Resources that specify what URL Path Params are required. These Script Packages must adhere to the following pattern:
	`[CUSTOM_PREFIX]-[SWAGGER_DATA_TYPE]-[VARIABLE_NAME]
Within the `(root).statics` Script Resource, you will find the variable `IGNITION_SWAGGER_CUSTOM_PREFIX`. This
variable defines the first part of the Script Package's name.
The Swagger Data Type must be one of the following basic data types:
	- string
	- integer
The final part will be the variable's name.
For example, if you required a Path Parameter of type `integer` with the variable name `myIntVar` using the default
custom prefix, the Script Package Resource would be defined with following name:
	`is-x-integer-myIntVar`
Accessing the variable within the Endpoint's logic would be done with the following line:
	`v = wdr['pathParams']['myIntVar']



## 2. Create Script Resource
An Endpoint within this system must contain a Script Resource with the name '__logic__'. This Script Resource
must be named EXACTLY as the string defined in `(root).statics.ENDPOINT_LOGIC_RESOURCE_NAME`, which, by default,
is named '__logic__'.



## 3. Define HTTP Method Class(es)
The '__logic__' resource will need to define a basic Python Class that inherits the __swagger2__.requests.HttpMethod class.
At the top of the Script Resource, define the following imports
	```
	import __swagger2__.requests
	import __swagger2__.responses
	import __swagger2__.globals
	import (root).statics
	```
The Python class must be in all caps, and named after a valid HTTP Method. The HTTP Method can be of any name.
However, be aware of the limited HTTP Methods that are natively supported by Ignition's WebDev Module.

#### Default Supported Ignition HTTP Methods
When creating a WebDev Resource, you will notice that only the following HTTP Methods are supported.
	- GET
	- POST
	- PUT
	- DELETE
	- HEAD
	- OPTIONS
	- TRACE
	- PATCH
Your Endpoints can support any and every HTTP Method, given that the incoming request specifies a value in
the `X-HTTP-Method-Override` Header. For example, if a POST request with the `X-HTTP-Method-Override` header has
the value 'COPY' specified, then the Swagger Magic will attempt to find a Class with the name 'COPY' instead of 'POST'.


## 4. Define logic and Swagger in HTTP Method Class(es)
Each HTTP Method Class will need to define the following:
	- A class variable with the name `SWAGGER`
		This variable will map to a Dictionary that will be structured as a Swagger Endpoint Definition.
		You will be defining a Dictionary with the structure defined in the Swagger Specification.
			https://swagger.io/specification/v2/
	- A static method `__do__`
		This method must have the decorator @staticmethod and the name dictated by the value in
		the variable `(root)statics.ENDPOINT_LOGIC_FUNCTION`.
		By default, the value is '__do__'.
		This function MUST accept the parameters `wdr` and `LOGGER`.
		The variable `wdr` is a WebDevRequest Object, and `LOGGER` is a Logger Object.
	Further below you will find an example endpoint.
	The name of the Endpoint Definition and function can both be changed in `(root).statics`. Take note of
	the `ENDPOINT_LOGIC_FUNCTION` and `ENDPOINT_SWAGGER_VARIABLE` variables.

#### Logger Messages
The Swagger Magic will create a Logger Object based on the Endpoint's path, and will be given to the Endpoint's
`__do__` function in the `LOGGER` parameter.
This Logger can be found in the Gateway with the name "IgnitionSwagger2.requests.Endpoint.[METHOD]__[path]". The slashes
in the Endpoint's path will be replaced with underscores.
For example, a GET Request sent to the Endpoint '/v1/my/endpoint/44', where '44' is a value for an integer Path Parameter
with the name `paramName` will have the following Gateway Logger.
	`IgnitionSwagger2.requests.Endpoint.GET__v1_my_endpoint_is-x-integer-paramName`

#### Authentication
Within the `SWAGGER` variable, the dictionary must define the variable `is-x-auth` (given that `is-x-` is the
defined Custom Prefix), which must map to a List of Dictionaries.
The Dictionaries must define a function as the value for the key 'method'.
the fuctiona must accept a WebDevRequest object as it's parameter.
More parameters can be required. The values for these parameters must be defined in the Dictionary's 'extraArgs'
parameter, which must be dictionary of extra keyword arguments.

For example, the `apiAuth.allowAll` Function accepts the single parameter `wdr` and simply return the necessary
response that will allow any request to access the Endpoint. The 'auth' Dictionary would be defined as such:
	```
	'is-x-auth': [
		{'method': apiAuth.simple.allowAll,},
	],
	```
However, if you wish to use other parameters, you might consider the `apiAuth.allowWithApiKeyHeader`. The 'auth'
Dictionary would then be defined as such
	```
	'is-x-auth': [
		{
			'method': apiAuth.simple.allowWithApiKeyHeader,
			'extraArgs': {
				'headerName': 'IS-API-KEY',
				'keyValue': 'abcd1234',
			},
		},
	],
	```

#### Endpoint that doesn't reqire Validation
If the Endpoint you are creating does not require and validation of the request, do the following:
	- Either do not define the "parameters" key in the `SWAGGER` Dictionary, or define it as an empty List
	- Set the "is-x-validateRequest" key in the `SWAGGER` Dictionary to False
If the Endpoint you are creating does not require and validation of the response, do the following:
	- Either do not define the "responses" key in the `SWAGGER` Dictionary, or define it as an empty Dictionary
	- Set the "is-x-validateResponse" key in the `SWAGGER` Dictionary to False

#### Setting a Header in the Response
...
 Set headers in response requires interfacing with the original Java Servlet Response
wdr.request['servletResponse'].setHeader(STRING, STRING)

#### Generic Responses
...
swagStc.GENERIC_SUCCESS_RESPONSE
swagStc.GENERIC_FAILURE_RESPONSE







- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

## Example Content for `__logic__` resource

from __swagger2__ import requests as swagRq
from __swagger2__ import responses as swagRsp
from (root) import statics as swagStc
PREFIX = swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX


	
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
		#To access URL Parameters, use the following structure
		var = wdr['pathParams']['myPathParamName']
		#To access a URL Query Parameter, use the following structure
		var = wdr['params']['urlQueryParamName']
		#To access a Body Parameter, use the following structure
		var = wdr['data']['bodyObject']['objectVar']
		
		#The return of the functions should be a return that the WebDev Module can use.
		return {'response': '42 is the answer'}
		#There are helper functions that can return a response that follows a specific, standard structure.
		#The JSON response will have the keys 'success' and 'status', which will map to a Boolean and String respectively.
		#Any data provided as a dictionary to the `data` parameter will be merged with the final dictionary.
		#In the example below, there will exist the following keys in the JSON response:
		#	- "success"
		#	- "status"
		#	- "swag"
		return __swagger2__.responses.json(success=True, status='SUCCESS', data={'swag': wdr.swag})
		 #This will return a response with the HTTP status code 404. The response will have the text '404 Not Found'
		return __swagger2__.responses.httpStatus(wdr.request, 404)
		 #This will return a response with the HTTP status code 500, given that the second parameter was the
		 # string 'Internal Server Error'
		return __swagger2__.responses.httpStatus(wdr.request, 'Internal Server Error')
	#END DEF
#END CLASS




- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Basic and Custom Swagger Keys:
...

"""