import apiAuth
from __swagger2__ import requests as swagRq
from __swagger2__ import responses as swagRsp
from __swagger2__ import statics as swagStc
PREFIX = swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX



class GET(swagRq.HttpMethod):
	SWAGGER = {
		 # CUSTOM KEYS FOR IA PURPOSES
		PREFIX+'auth': [
			{'method': apiAuth.simple.allowNone,},
		],
		PREFIX+'hide': False,
		PREFIX+'validateRequest': False,
		PREFIX+'validateResponse': False,
		PREFIX+'tagGroup': 'Tests',
		
		 # ACTUAL SWAGGER DEFINITION
		'operationId': 'tests_validation_auth-alwaysfail_get',
		'summary': 'GET Test Always Fail',
		'description': '''This endpoint will always fail the incoming request''',
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
			'200': swagStc.GENERIC_FAILURE_RESPONSE,
			'default': swagStc.GENERIC_FAILURE_RESPONSE,
		}
	}
	
	@staticmethod
	def __do__(wdr, LOGGER):
		return swagRsp.json(success=True, status='SUCCESS', message="I should never get here!")
	#END DEF
#END CLASS

class POST(swagRq.HttpMethod):
	SWAGGER = {
		 # CUSTOM KEYS FOR IA PURPOSES
		PREFIX+'auth': [
			{'method': apiAuth.simple.allowNone,},
		],
		PREFIX+'hide': False,
		PREFIX+'validateRequest': False,
		PREFIX+'validateResponse': False,
		PREFIX+'tagGroup': 'Tests',
		
		 # ACTUAL SWAGGER DEFINITION
		'operationId': 'tests_validation_auth-alwaysfail_post',
		'summary': 'POST Test Always Fail',
		'description': '''This endpoint will always fail the incoming request''',
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
			'200': swagStc.GENERIC_FAILURE_RESPONSE,
			'default': swagStc.GENERIC_FAILURE_RESPONSE,
		}
	}
	
	@staticmethod
	def __do__(wdr, LOGGER):
		return swagRsp.json(success=True, status='SUCCESS', message="I should never get here!")
	#END DEF
#END CLASS