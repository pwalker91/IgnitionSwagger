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
		'operationId': 'getUserByName',
		'summary': 'Get user by user name',
		'description': 'Use `user1` for testing',
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
			#No path parameters here, because the Script Package `is-x-string-username` supplies the
			# Swagger Magic the necessary rules for validation
		],
		'responses': {
			'200': {
				"description": "successful operation",
				"schema": {
					"$ref": "#/definitions/User"
				}
			},
			'400': { "description": "Invalid username supplied" },
			'404': { "description": "User not found" },
			'default': swagStc.GENERIC_FAILURE_RESPONSE,
		}
	}
	
	@staticmethod
	def __do__(wdr, logger):
		logger.trace("Doing a get user/{username} thing")
		if 'user' not in wdr.swag['pathParams']['username']:
			return swagRsp.httpStatus(wdr.request, 400)
		elif wdr.swag['pathParams']['username'] != 'user1':
			return swagRsp.httpStatus(wdr.request, 404)
		return swagRsp.json(success=True, status='SUCCESS', data={
			'id': 1,
			'username': "user1",
			'firstName': "I am",
			'lastName': "Groot",
			'email': "iamgroot@yggdrasil.com",
			'password': "1amGROOT!",
			'phone': "+1 555-123-4567",
			'userStatus': 1,
		})
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
		'operationId': 'updateUser',
		'summary': 'Updated user',
		'description': 'This can only be done by the logged in user.',
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
			#No path parameters here, because the Script Package `is-x-string-username` supplies the
			# Swagger Magic the necessary rules for validation
			{
				'in': "body",
				'name': "body",
				'description': "Updated user object",
				'required': True,
				'schema': {
					"$ref": "#/definitions/User"
				}
			}
		],
		'responses': {
			'200': swagStc.GENERIC_SUCCESS_RESPONSE,
			'400': { "description": "Invalid user supplied" },
			'404': { "description": "User not found" },
			'default': swagStc.GENERIC_FAILURE_RESPONSE,
		}
	}
	
	@staticmethod
	def __do__(wdr, logger):
		logger.trace("Doing a put user/{username} thing")
		if 'user' not in wdr.swag['pathParams']['username']:
			return swagRsp.httpStatus(wdr.request, 400)
		elif wdr.swag['pathParams']['username'] != 'user1':
			return swagRsp.httpStatus(wdr.request, 404)
		logger.trace("Got new content for a User.", wdr.swag['data'])
		return swagRsp.json(success=True, status='SUCCESS', data={'description': "successful operation"})
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
		'operationId': 'deleteUser',
		'summary': 'Delete user',
		'description': 'This can only be done by the logged in user.',
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
			#No path parameters here, because the Script Package `is-x-string-username` supplies the
			# Swagger Magic the necessary rules for validation
		],
		'responses': {
			'200': swagStc.GENERIC_SUCCESS_RESPONSE,
			'400': { "description": "Invalid username supplied" },
			'404': { "description": "User not found" },
			'default': swagStc.GENERIC_FAILURE_RESPONSE,
		}
	}
	
	@staticmethod
	def __do__(wdr, logger):
		logger.trace("Doing a delete user/{username} thing")
		if 'user' not in wdr.swag['pathParams']['username']:
			return swagRsp.httpStatus(wdr.request, 400)
		elif wdr.swag['pathParams']['username'] != 'user1':
			return swagRsp.httpStatus(wdr.request, 404)
		return swagRsp.json(success=True, status='SUCCESS', data={'description': "successful operation"})
	#END DEF
#END CLASS