import apiAuth
from __swagger2__ import requests as swagRq
from __swagger2__ import responses as swagRsp
from __swagger2__ import statics as swagStc
PREFIX = swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX



class POST(swagRq.HttpMethod):
	SWAGGER = {
		# CUSTOM KEYS FOR IA PURPOSES
		PREFIX+'auth': [
			{'method': apiAuth.simple.allowAll,},
		],
		PREFIX+'hide': False,
		PREFIX+'validateRequest': False,
		PREFIX+'validateResponse': False,
		PREFIX+'tagGroup': 'Pet Store',
		
		 # ACTUAL SWAGGER DEFINITION
		'operationId': 'createUser',
		'summary': 'Create user',
		'description': '''This can only be done by the logged in user.''',
		'tags': [
			'user'
		],
		'consumes': [
			'application/json',
		],
		'produces': [
			'application/json',
			'application/xml',
		],
		'parameters': [
			{
				'in': 'body',
				'name': 'body',
				'description': "Created user object",
				'schema': {'$ref': "#/definitions/User"},
			}
		],
		'responses': {
			'default': {'description': "successful operation"},
		}
	}
	
	@staticmethod
	def __do__(wdr, logger):
		logger.trace("Doing a thing")
		return swagRsp.json(success=True, status='SUCCESS', data={'description': "successful operation"})
	#END DEF
#END CLASS