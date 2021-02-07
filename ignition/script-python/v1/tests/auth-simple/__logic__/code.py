import apiAuth
from __swagger2__ import requests as swagRq
from __swagger2__ import responses as swagRsp
from v1 import statics as swagStc
PREFIX = swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX



class GET(swagRq.HttpMethod):
	SWAGGER = {
		 # CUSTOM KEYS FOR IA PURPOSES
		PREFIX+'auth': [
			{
				'method': apiAuth.simple.allowWithApiKeyHeader,
				'extraArgs': {
					'headerName': 'IS-API-KEY',
					'keyValue': 'abcd1234',
				},
			},
		],
		PREFIX+'hide': False,
		PREFIX+'validateRequest': False,
		PREFIX+'validateResponse': False,
		PREFIX+'tagGroup': 'Tests',
		
		 # ACTUAL SWAGGER DEFINITION
		'operationId': 'tests_validation_auth-simple_get',
		'summary': 'GET Test Simple Auth',
		'description': '''Provides the ability to test a simple endpoint with "authentication" required.
				Provide the value `abcd1234` in the Header `IS-API-KEY`.
			''',
		'security': [
			{'api_key': []},
		],
		'tags': [
			'Testing'
		],
		'consumes': [
			'application/x-www-form-urlencoded',
		],
		'produces': [
			'application/json',
		],
		'parameters': [
			{'$ref': '#/parameters/objs_api_key_header'},
		],
		'responses': {
			'200': swagStc.GENERIC_SUCCESS_RESPONSE,
			'default': swagStc.GENERIC_FAILURE_RESPONSE,
		}
	}
	
	@staticmethod
	def __do__(wdr, LOGGER):
		return swagRsp.json(success=True, status='SUCCESS', data={'auth': wdr.swag['auth']})
	#END DEF
#END CLASS

class POST(swagRq.HttpMethod):
	SWAGGER = {
		 # CUSTOM KEYS FOR IA PURPOSES
		PREFIX+'auth': [
			{
				'method': apiAuth.simple.allowWithApiKeyHeader,
				'extraArgs': {
					'headerName': 'IS-API-KEY',
					'keyValue': 'qwerty123456',
				},
			},
		],
		PREFIX+'hide': False,
		PREFIX+'validateRequest': False,
		PREFIX+'validateResponse': False,
		PREFIX+'tagGroup': 'Tests',
		
		 # ACTUAL SWAGGER DEFINITION
		'operationId': 'tests_validation_auth-simple_post',
		'summary': 'POST Test Simple Auth',
		'description': '''Provides the ability to test a simple endpoint with "authentication" required.
				Provide the value `qwerty123456` in the Header `IS-API-KEY`.
			''',
		'security': [
			{'api_key': []},
		],
		'tags': [
			'Testing'
		],
		'consumes': [
			'application/json',
		],
		'produces': [
			'application/json',
		],
		'parameters': [
			{'$ref': '#/parameters/objs_api_key_header'},
		],
		'responses': {
			'200': swagStc.GENERIC_SUCCESS_RESPONSE,
			'default': swagStc.GENERIC_FAILURE_RESPONSE,
		}
	}
	
	@staticmethod
	def __do__(wdr, LOGGER):
		return swagRsp.json(success=True, status='SUCCESS', data={'auth': wdr.swag['auth']})
	#END DEF
#END CLASS