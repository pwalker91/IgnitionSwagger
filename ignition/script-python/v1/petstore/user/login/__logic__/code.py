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
		PREFIX+'validateRequest': False,
		PREFIX+'validateResponse': False,
		PREFIX+'tagGroup': 'Pet Store',
		
		 # ACTUAL SWAGGER DEFINITION
		'operationId': 'loginUser',
		'summary': 'Logs user into the system',
		'description': '',
		'tags': [
			'user'
		],
		'consumes': [],
		'produces': [
			'application/json',
			'application/xml',
		],
		'parameters': [
			{
				'name': "username",
				'in': "query",
				'description': "The user name for login",
				'required': True,
				'type': "string",
			},
			{
				'name': "password",
				'in': "query",
				'description': "The password for login in clear text",
				'required': True,
				'type': "string",
			}
		],
		'responses': {
			'200': {
				"description": "successful operation",
				"headers": {
					"X-Expires-After": {
						"type": "string",
						"format": "date-time",
						"description": "date in UTC when token expires"
					},
					"X-Rate-Limit": {
						"type": "integer",
						"format": "int32",
						"description": "calls per hour allowed by the user"
					}
				},
				"schema": {
					"type": "string"
				}
			},
			'400': { "description": "Invalid username/password supplied" },
			'default': swagStc.GENERIC_FAILURE_RESPONSE,
		}
	}
	
	@staticmethod
	def __do__(wdr, logger):
		logger.trace("Doing a get user/login thing")
		#logger.trace("{!r}".format(wdr))
		if 'user' in wdr.swag['data']['username']:
			return swagRsp.httpStatus(wdr.request, 400)
		swagRsp.setHeader(wdr.request, "X-Expires-After", "2099-01-01T00:00:00 +00:00")
		swagRsp.setHeader(wdr.request, "X-Rate-Limit", "500")
		return swagRsp.json(success=True, status='SUCCESS', data={'description': "I would do a thing"})
	#END DEF
#END CLASS