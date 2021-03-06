# # # # # # # #
# TODO:
#  Implement some logic that will pretend to a Pet Store
# # # # # # # #

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
		PREFIX+'validateRequest': False,
		PREFIX+'validateResponse': False,
		PREFIX+'tagGroup': 'Pet Store',
		
		 # ACTUAL SWAGGER DEFINITION
		'operationId': '',
		'summary': '',
		'description': '',
		'tags': [
			'user'
		],
		'consumes': [
			'application/json',
			'application/x-www-form-urlencoded',
		],
		'produces': [
			'application/json',
			'application/xml',
		],
		'parameters': [
			#
		],
		'responses': {
			#
			'default': swagStc.GENERIC_FAILURE_RESPONSE,
		}
	}
	
	@staticmethod
	def __do__(wdr, logger):
		logger.trace("Doing a thing")
		return swagRsp.json(success=True, status='SUCCESS', data={'description': "successful operation"})
	#END DEF
#END CLASS