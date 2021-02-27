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
		'operationId': 'findPetsByStatus',
		'summary': 'Finds Pets by status',
		'description': 'Multiple status values can be provided with comma separated strings',
		'tags': [
			'pet'
		],
		'consumes': [
			'application/json',
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
				'in': 'query',
				'name': 'status',
				'description': 'Status values that need to be considered for filter',
				'required': True,
				'type': 'array',
				'items': {
					'type': 'string',
					'enum': ['available', 'pending', 'sold'],
					'default': 'available'
				},
				'collectionFormat': 'csv',
				'example': 'available,pending',
			}
		],
		'responses': {
			'200': {
				"description": "successful operation",
				"schema": {
					"type": "object",
					"properties": {
						"pets": {
							"type": "array",
							"items": {
								"$ref": "#/definitions/Pet"
							},
						},
					},
					"required": ["pets"],
				},
			},
			'400': {"description": "Invalid status value"},
			'default': swagStc.GENERIC_FAILURE_RESPONSE,
		}
	}
	
	@staticmethod
	def __do__(wdr, logger):
		logger.trace("Doing a get findByStatus thing")
		if any([
			(v not in GET.SWAGGER['parameters'][0]['items']['enum'])
			for v in wdr.swag['data']['status']
		]):
			return swagRsp.httpStatus(wdr.request, 400)
		return swagRsp.json(success=True, status='SUCCESS', data={
				"pets": [
					{
						"photoUrls": ["url1"],
						"tags": [
							{"name": "string", "id": 1}
						],
						"name": "saved-doggie",
						"id": 101,
						"category": {"name": "string", "id": 1},
						"status": "available"
					},
				],
			}
		)
	#END DEF
#END CLASS