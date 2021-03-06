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
		'operationId': 'logoutUser',
		'summary': 'Logs out current logged in user session',
		'description': '',
		'tags': [
			'user'
		],
		'consumes': [],
		'produces': [
			'application/json',
			'application/xml',
		],
		'parameters': [],
		'responses': {
			'default': {'description': "successful operation"},
		}
	}
	
	@staticmethod
	def __do__(wdr, logger):
		logger.trace("Doing a get user/logout thing")
		return swagRsp.json(success=True, status='SUCCESS', data={'description': "successful operation"})
	#END DEF
#END CLASS