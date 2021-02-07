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
				'method': apiAuth.simple.allowAll,
				'extraArgs': {
					'aKey': 'I dont do anything'
				},
			},
		],
		PREFIX+'hide': False,
		PREFIX+'validateRequest': True,
		PREFIX+'validateResponse': True,
		PREFIX+'tagGroup': 'Tests',
		
		 # ACTUAL SWAGGER DEFINITION
		'operationId': 'tests_validation_get',
		'summary': 'GET Validation Test',
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
		'parameters': [
			{
				'description': 'URL Query Integer argument',
				'in': 'query',
				'name': 'arg1',
				'type': 'integer',
				'required': True,
				'example': 42,
				PREFIX+'obscure': True,
			},
			{
				'description': 'URL Query String argument',
				'in': 'query',
				'name': 'arg2',
				'type': 'string',
				'required': False,
				'default': 'hello world',
				'example': 'hello world',
			},
			{
				'description': 'URL Query String argument',
				'in': 'query',
				'name': 'arg3',
				'type': 'array',
				'collectionFormat': 'csv',
				'minItems': 3,
				'items': {
					'type':'integer'
				},
				'required': False,
				'default': [1,2,3],
				'example': '1,2,3',
			},
		],
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
			'default': swagStc.GENERIC_FAILURE_RESPONSE,
		}
	}
	
	@staticmethod
	def __do__(wdr, LOGGER):
		LOGGER.debug("I'm in the endpoint logic!")
		if wdr.swag['params']['arg1'] == 0:
			raise Exception("I'm failing.")
		if wdr.swag['params']['arg1'] == 42:
			return swagRsp.json(
						success=False, status='FAILURE',
						message='You gave a bad number. Try a different one.'
					)
		return swagRsp.json(success=True, status='SUCCESS', data={'swag': wdr.swag})
	#END DEF
#END CLASS



class POST(swagRq.HttpMethod):
	SWAGGER = {
		 # CUSTOM KEYS FOR IA PURPOSES
		PREFIX+'auth': [
			{
				'method': apiAuth.simple.allowAll,
				'extraArgs': {
					'aKey': 'I dont do anything'
				},
			},
		],
		PREFIX+'hide': False,
		PREFIX+'validateRequest': True,
		PREFIX+'validateResponse': True,
		PREFIX+'tagGroup': 'Tests',
		
		 # ACTUAL SWAGGER DEFINITION
		'operationId': 'tests_validation_post',
		'summary': 'POST Validation Test',
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
		'parameters': [
			{
				'in': 'body',
				'schema': {
					'type': 'object',
					'properties': {
						'arg_string': {'type': 'string'},
						'arg_boolean': {'type': 'boolean'},
						'arg_date': {'type': 'string', 'format': 'datetime', 'example': '2019-01-01T00:00:00 -08:00'},
						'arg_date2': {'type': 'string', 'format': 'date', 'x-nullable': True, 'example': '2019-01-01'},
						'arg_int': {'type': 'integer', 'x-nullable': True, 'maximum': 100, 'minimum': 0},
						'arg_float': {'type': 'number', 'format': 'float', 'maximum': 9002, 'minimum':9000},
						'arg_array': {
							'type': 'array',
							'items': {
								'type': 'integer',
								'title': 'Numbers',
							},
						},
						'arg_object': {
							'type': 'object',
							'title': 'Simple Object',
							'properties': {
								'arg_string': {'type': 'string'},
								'arg_int': {'type':'integer'},
								'arg_array': {
									'type':'array',
									'x-nullable': True,
									'items': {
										'type': 'object',
										'title': 'Nested Object',
										'x-nullable': True,
										'properties': {
											'arg_string': {'type': 'string', 'x-nullable': True},
											'arg_float': {'type': 'number', 'format': 'float', 'maximum': 10, 'minimum':1},
										},
										'required': [
											'arg_string', 'arg_float'
										],
										PREFIX+'obscure': True,
									},
								},
							},
							'required': [
								'arg_string', 'arg_int', 'arg_array'
							],
						},
					},
					'required': [
						'arg_string','arg_boolean','arg_int','arg_float','arg_date'
					],
				},
			},
		],
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
						'arg_string': {'type': 'string',},
						'arg_boolean': {'type': 'boolean',},
						'arg_date': {'type': 'string', 'format': 'datetime', 'example': '2019-01-01T00:00:00 -08:00'},
						'arg_date2': {'type': 'string', 'format': 'date', 'x-nullable': True, 'example': '2019-01-01'},
						'arg_int': {'type': 'integer', 'x-nullable': True, 'minimum': 10},
						'arg_float': {'type': 'number', 'format': 'float', 'maximum': 9002, 'minimum': 9000},
						'arg_array': {
							'type': 'array',
							'items': {
								'type': 'integer',
								'title': 'Numbers',
							},
						},
						'arg_object': {
							'type': 'object',
							'title': 'Simple Object',
							'properties': {
								'arg_string': {'type': 'string'},
								'arg_int': {'type':'integer'},
								'arg_array': {
									'type':'array',
									'x-nullable': True,
									'items': {
										'type': 'object',
										'title': 'Nested Object',
										'x-nullable': True,
										'properties': {
											'arg_string': {'type': 'string', 'x-nullable': True},
											'arg_float': {'type': 'number', 'format': 'float', 'maximum': 10, 'minimum':1},
										},
										'required': [
											'arg_string', 'arg_float'
										],
									},
								},
							},
							'required': [
								'arg_string', 'arg_int', 'arg_array'
							],
						},
					},
					'required': [
						'success','status','arg_string','arg_boolean','arg_int'
					],
				},
				'examples': {
					"application/json": {
						'success': True,
						'status': 'SUCCESS',
						'arg_string': 'hello wrld',
						'arg_boolean': False,
						'arg_date': '2019-01-01 00:00:00',
						'arg_date2': '2019-01-01',
						'arg_int': 42,
						'arg_float': 16.6,
						'arg_array': [1,2,3,4],
						'arg_object': {
							'arg_string': 'hello again',
							'arg_int': 42,
							'arg_array': [
								{
									'arg_string': "hello a third time",
									'arg_float': 4.2,
								}
							],
						},
					}
				},
			},
			'default': swagStc.GENERIC_FAILURE_RESPONSE,
		}
	}
	
	@staticmethod
	def __do__(wdr, LOGGER):
		LOGGER.debug("I'm in the endpoint logic!")
		if wdr.swag['data']['arg_int'] == 42:
			return swagRsp.json(
						success=False, status='FAILURE',
						message='You gave a bad number. Try a different one.'
					)
		return swagRsp.json(success=True, status='SUCCESS', data=wdr.swag['data'])
	#END DEF
#END CLASS