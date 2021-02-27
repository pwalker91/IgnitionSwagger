import apiAuth
from __swagger2__ import requests as swagRq
from __swagger2__ import responses as swagRsp
from v1 import statics as swagStc
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
		PREFIX+'tagGroup': 'Pet Store',
		
		 # ACTUAL SWAGGER DEFINITION
		'operationId': 'getPetById',
		'summary': 'Find pet by ID',
		'description': 'Returns a single pet',
		'tags': [
			'pet'
		],
		'consumes': [
			'application/x-www-form-urlencoded',
		],
		'produces': [
			'application/json',
			'application/xml',
		],
		"security": [
			{"api_key": []},
		],
		'parameters': [
			#No parameters here, because the Script Package `is-x-integer-petId` supplies the
			# Swagger Magic the necessary rules for validation
		],
		'responses': {
			'200': {
				"description": "successful operation",
				"schema": {
					"$ref": "#/definitions/Pet"
				}
			},
			'400': { "description": "Invalid ID supplied" },
			'404': { "description": "Pet not found" },
			'default': swagStc.GENERIC_FAILURE_RESPONSE,
		}
	}
	
	@staticmethod
	def __do__(wdr, logger):
		logger.trace("Doing a get pet/{petId} thing")
		if wdr.swag['pathParams']['petId'] <= 0:
			return swagRsp.httpStatus(wdr.request, 400)
		elif wdr.swag['pathParams']['petId'] == 1:
			return swagRsp.httpStatus(wdr.request, 404)
		else:
			return swagRsp.json(success=True, status='SUCCESS', data={
					"photoUrls": ["url1"],
					"tags": [
						{"name": "string", "id": 1}
					],
					"name": "saved-doggie",
					"id": 101,
					"category": {"name": "string", "id": 1},
					"status": "available"
				}
			)
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
		PREFIX+'tagGroup': 'Pet Store',
		
		 # ACTUAL SWAGGER DEFINITION
		'operationId': 'updatePetWithForm',
		'summary': 'Updates a pet in the store with form data',
		'description': '',
		'tags': [
			'pet'
		],
		'consumes': [
			'application/x-www-form-urlencoded',
		],
		'produces': [
			'application/json',
			'application/xml',
		],
		"security": [
			{"petstore_auth": ["write:pets", "read:pets"]},
		],
		'parameters': [
			#No parameter for `petId` in the URL here, because the Script Package `is-x-integer-petId`
			# supplies the Swagger Magic the necessary rules for validation
			{
				'in': "formData",
				'name': "name",
				'description': "Updated name of the pet",
				'type': "string",
				'required': False,
			},
			{
				'in': "formData",
				'name': "status",
				'description': "Updated status of the pet",
				'type': "string",
				'required': False,
			},
		],
		'responses': {
			'200': swagStc.GENERIC_SUCCESS_RESPONSE,
			'405': {"description": "Invalid input"},
			'default': swagStc.GENERIC_FAILURE_RESPONSE,
		}
	}
	
	@staticmethod
	def __do__(wdr, logger):
		logger.trace("Doing a post pet/{petId} thing")
		if wdr.swag['pathParams']['petId'] <= 0:
			return swagRsp.httpStatus(wdr.request, 405)
		return swagRsp.json(
			success=True, status='SUCCESS',
			data={
				'petId': wdr.swag['pathParams']['petId'],
				'action': "Would update pet with name='{!s}', status='{!s}'".format(
					wdr.swag['data']['name'],
					wdr.swag['data']['status'],
				)
			}
		)
	#END DEF
#END CLASS

class DELETE(swagRq.HttpMethod):
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
		'operationId': 'deletePet',
		'summary': 'Deletes a pet',
		'description': '',
		'tags': [
			'pet'
		],
		'consumes': [
			'application/x-www-form-urlencoded',
		],
		'produces': [
			'application/json',
			'application/xml',
		],
		"security": [
			{"petstore_auth": ["write:pets", "read:pets"]},
		],
		'parameters': [
			#No parameter for `petId` in the URL here, because the Script Package `is-x-integer-petId`
			# supplies the Swagger Magic the necessary rules for validation
			{
				'in': "header",
				'name': "api_key",
				'type': "string",
				'required': False,
			}
		],
		'responses': {
			'200': swagStc.GENERIC_SUCCESS_RESPONSE,
			'400': {"description": "Invalid ID supplied"},
			'404': {"description": "Pet not found"},
			'default': swagStc.GENERIC_FAILURE_RESPONSE,
		}
	}
	
	@staticmethod
	def __do__(wdr, logger):
		logger.trace("Doing a delete pet/{petId} thing")
		if wdr.swag['pathParams']['petId'] <= 0:
			return swagRsp.httpStatus(wdr.request, 400)
		elif 1 <= wdr.swag['pathParams']['petId'] <= 10:
			return swagRsp.httpStatus(wdr.request, 405)
		return swagRsp.json(success=True, status='SUCCESS', data={'description': "successful operation"})
	#END DEF
#END CLASS