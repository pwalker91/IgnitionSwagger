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
		'deprecated': True,
		'operationId': 'findPetsByTags',
		'summary': 'Finds Pets by tags',
		'description': 'Multiple tags can be provided with comma separated strings. Use tag1, tag2, tag3 for testing.',
		'tags': [
			'pet'
		],
		'consumes': [
			'application/json',
			'application/x-www-form-urlencoded',
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
				'name': 'tags',
				'description': 'Tags to filter by',
				'required': True,
				'type': 'array',
				'items': {
					'type': 'string'
				},
				'collectionFormat': 'csv',
				'example': 'tag1,tag2',
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
			'400': {"description": "Invalid tag value"},
			'default': swagStc.GENERIC_FAILURE_RESPONSE,
		}
	}
	
	@staticmethod
	def __do__(wdr, logger):
		logger.trace("Doing a get findByTags thing")
		if any([
			("invalid" in v.lower())
			for v in wdr.swag['data']['tags']
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