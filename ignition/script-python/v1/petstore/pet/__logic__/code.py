import apiAuth
from __swagger2__ import requests as swagRq
from __swagger2__ import responses as swagRsp
from v1 import statics as swagStc
PREFIX = swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX



class POST(swagRq.HttpMethod):
	SWAGGER = {
		# CUSTOM KEYS FOR IA PURPOSES
		PREFIX+'auth': [
			{'method': apiAuth.simple.allowAll,},
		],
		PREFIX+'hide': False,
		PREFIX+'validateRequest': True,
		PREFIX+'validateResponse': True,
		PREFIX+'tagGroup': 'Pet Store',
		
		 # ACTUAL SWAGGER DEFINITION
		'operationId': 'addPet',
		'summary': 'Add a new pet to the store',
		'description': '',
		'tags': [
			'pet'
		],
		'consumes': [
			'application/json',
			'application/xml',
		],
		'produces': [
			'application/json',
			'application/xml',
		],
		'security': [
			{'petstore_auth': ['write:pets', 'read:pets']},
		],
		'parameters': [
			{
				'in': 'body',
				'description': 'Pet object that needs to be added to the store',
				'schema': {'$ref': '#/definitions/Pet'},
			},
		],
		'responses': {
			'405': {'description': 'Invalid input',},
			'200': swagStc.GENERIC_SUCCESS_RESPONSE,
			'default': swagStc.GENERIC_FAILURE_RESPONSE,
		}
	}
	
	@staticmethod
	def __do__(wdr, logger):
		logger.trace("Doing a post pet thing")
		if wdr.swag['data']['id'] <= 0:
			return swagRsp.httpStatus(wdr.request, 405)
		return swagRsp.json(success=True, status='SUCCESS', data={'description': "successful operation"})
	#END DEF
#END CLASS

class PUT(swagRq.HttpMethod):
	SWAGGER = {
		# CUSTOM KEYS FOR IA PURPOSES
		PREFIX+'auth': [
			{'method': apiAuth.simple.allowAll,},
		],
		PREFIX+'hide': False,
		PREFIX+'validateRequest': True,
		PREFIX+'validateResponse': True,
		PREFIX+'tagGroup': 'Pet Store',
		
		 # ACTUAL SWAGGER DEFINITION
		'operationId': 'updatePet',
		'summary': 'Update an existing pet',
		'description': '',
		'tags': [
			'pet'
		],
		'consumes': [
			'application/json',
			'application/xml',
		],
		'produces': [
			'application/json',
			'application/xml',
		],
		'security': [
			{'petstore_auth': ['write:pets', 'read:pets']}
		],
		'parameters': [
			{
				'in': 'body',
				'description': 'Pet object that needs to be added to the store',
				'schema': {'$ref': '#/definitions/Pet'},
			},
		],
		'responses': {
			'400': {'description': 'Invalid ID supplied',},
			'404': {'description': 'Pet not found',},
			'405': {'description': 'Validation exception',},
			'200': swagStc.GENERIC_SUCCESS_RESPONSE,
			'default': swagStc.GENERIC_FAILURE_RESPONSE,
		}
	}
	
	@staticmethod
	def __do__(wdr, logger):
		logger.trace("Doing a put pet thing")
		if wdr.swag['data']['id'] <= 0:
			return swagRsp.httpStatus(wdr.request, 400)
		elif wdr.swag['data']['id'] == 1:
			return swagRsp.httpStatus(wdr.request, 404)
		elif 2 <= wdr.swag['data']['id'] <= 100:
			return swagRsp.httpStatus(wdr.request, 405)
		return swagRsp.json(success=True, status='SUCCESS', data={'description': "successful operation"})
	#END DEF
#END CLASS