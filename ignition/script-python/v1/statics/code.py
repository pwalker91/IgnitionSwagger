'''
	This script module contains static values that the Swagger Magic will use to find endpoint resources
'''

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# STATIC VARIABLES YOU CAN CHANGE
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

#The URL of your site, which will be used in the `swagger.json` file that can be requested at {URL}/swagger.json
HOST_NAME = 'yoursite.here'

#Our Swagger definition can have keys custom to Ignition Swagger. They will all have the following prefix
IGNITION_SWAGGER_CUSTOM_PREFIX = 'is-x-'

#When we are attempting to find a Script Module Resource (which should contain our logic for processing
# a valid HTTP Request), we will be searching through the present Script Package Resources. If a Package
# has a Module with the following name, then we will inspect it and try to find some classes that inherit
# the `HttpMethod` class.
ENDPOINT_LOGIC_RESOURCE_NAME = '__logic__'
#If an 'HttpMethod' class is found, it SHOULD have a function named below, which will contain the actual logic
# for the endpoint, as well as a "Swagger Dictionary" containing the definition and validation rules for the
# endpoint.
ENDPOINT_LOGIC_FUNCTION = '__do__'
ENDPOINT_SWAGGER_VARIABLE = 'SWAGGER'

#These dictionaries can be referenced within an endpoint if the response will use a "generic" format and
# expected set of values.
# These dictionaries can be useful if you are going to be defining a large number of endpoint that simply
# perform an action and do not return any data (or maybe a single piece of primitive data).
GENERIC_SUCCESS_RESPONSE = {
		'description': '**SUCCESS** (returns HTTP Status `OK`)',
		'schema': {
			'type': 'object',
			'properties': {
				'success': {'type': 'boolean', 'enum': [True]},
				'status': {'type': 'string', 'enum': ['SUCCESS']},
				'message': {'type': 'string'},
			},
			'required': ['success','status'],
		},
		'examples': {
			"application/json": {
				'success': True,
				'status': 'SUCCESS',
				'message': '',
			}
		},
	}
GENERIC_FAILURE_RESPONSE = {
		'description': '**FAILURE** (returns HTTP Status `OK`)',
		'schema': {
			'type': 'object',
			'properties': {
				'success': {'type': 'boolean', 'enum': [False]},
				'status': {'type': 'string', 'enum': ['FAILURE']},
				'message': {'type': 'string'},
				'error': {'type': 'object'},
			},
			'required': ['success','status'],
		},
		'examples': {
			"application/json": {
				'success': False,
				'status': 'FAILURE',
				'message': 'Your API Request failed for some reason',
				'error': {
					'code': 42,
					'reason': 'You didn\'t have the secret password',
					'details': [],
				},
			}
		},
	}