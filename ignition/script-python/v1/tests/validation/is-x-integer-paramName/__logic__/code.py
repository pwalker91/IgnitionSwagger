import apiAuth
from __swagger2__ import requests as swagRq
from __swagger2__ import responses as swagRsp
from __swagger2__ import statics as swagStc
PREFIX = swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX



class GET(swagRq.HttpMethod):
	SWAGGER = {
		 # CUSTOM KEYS FOR IA PURPOSES
		PREFIX+'auth': [
			{'method': apiAuth.simple.allowAll,},
		],
		PREFIX+'hide': False,
		PREFIX+'validateRequest': True,
		PREFIX+'validateResponse': True,
		PREFIX+'tagGroup': 'Tests',
		
		 # ACTUAL SWAGGER DEFINITION
		'operationId': 'tests_validation_{paramName}_get',
		'summary': 'GET Validation Test (1 Path Param)',
		'description': '''Provides the ability to test the data validation portion of the API Endpoints.''',
		
		'tags': [
			'Testing'
		],
		'consumes': [
			'application/x-www-form-urlencoded',
		],
		'produces': [
			'application/json',
		],
		'parameters': [],
		'responses': {
			#Since the logic of this endpoint that returns more useful information is only for internal
			# use, the only "swagger" response we show is the HTTP Status Code 418
			'200': {
				'description': '**SUCCESS** (returns HTTP Status `OK`)',
				'schema': {
					'type': 'object',
					'properties': {
						'success': {'type': 'boolean', 'enum': [True]},
						'status': {'type': 'string', 'enum': ['SUCCESS']},
						'swag': {'type': 'object'},
						'numValidatedPathParams': {'type': 'integer'},
					},
					'required': ['success','status','swag'],
				},
				'examples': {
					"application/json": {
						'success': True,
						'status': 'SUCCESS',
					}
				},
			},
			'default': swagStc.GENERIC_FAILURE_RESPONSE,
		}
	}
	
	@staticmethod
	def __do__(wdr, LOGGER):
		return swagRsp.json(success=True, status='SUCCESS', data={'swag': wdr.swag, 'numValidatedPathParams': 1})
	#END DEF
#END CLASS

class POST(swagRq.HttpMethod):
	SWAGGER = {
		 # CUSTOM KEYS FOR IA PURPOSES
		PREFIX+'auth': [
			{'method': apiAuth.simple.allowAll,},
		],
		PREFIX+'hide': False,
		PREFIX+'validateRequest': True,
		PREFIX+'validateResponse': True,
		PREFIX+'tagGroup': 'Tests',
		
		 # ACTUAL SWAGGER DEFINITION
		'operationId': 'tests_validation_{paramName}_post',
		'summary': 'POST Validation Test (1 Path Param)',
		'description': '''Provides the ability to test the data validation portion of the API Endpoints.''',
		'tags': [
			'Testing'
		],
		'consumes': [
			'application/json',
		],
		'produces': [
			'application/json',
		],
		'parameters': [],
		'responses': {
			#Since the logic of this endpoint that returns more useful information is only for internal
			# use, the only "swagger" response we show is the HTTP Status Code 418
			'200': {
				'description': '**SUCCESS** (returns HTTP Status `OK`)',
				 'schema': {
					'type': 'object',
					'properties': {
						'success': {'type': 'boolean', 'enum': [True]},
						'status': {'type': 'string', 'enum': ['SUCCESS']},
						'swag': {'type': 'object'},
						'numValidatedPathParams': {'type': 'integer'},
					},
					'required': ['success','status','swag'],
				},
				'examples': {
					"application/json": {
						'success': True,
						'status': 'SUCCESS',
					}
				},
			},
			'default': swagStc.GENERIC_FAILURE_RESPONSE,
		}
	}
	
	@staticmethod
	def __do__(wdr, LOGGER):
		return swagRsp.json(success=True, status='SUCCESS', data={'swag': wdr.swag, 'numValidatedPathParams': 1})
	#END DEF
#END CLASS