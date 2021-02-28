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
		'operationId': 'uploadFile',
		'summary': 'uploads an image',
		'description': '',
		'tags': [
			'pet'
		],
		'consumes': [
			'multipart/form-data',
		],
		'produces': [
			'application/json',
		],
		'parameters': [
			#No parameters here, because the Script Package `is-x-integer-petId` supplies the
			# Swagger Magic the necessary rules for validation
			{
				"name": "additionalMetadata",
				"in": "formData",
				"description": "Additional data to pass to server",
				"required": False,
				"type": "string"
			},
			{
				"name": "file",
				"in": "formData",
				"description": "file to upload",
				"required": False,
				"type": "file"
			}
		],
		'responses': {
			'200': {
				"description": "successful operation",
				"schema": {
					"$ref": "#/definitions/ApiResponse"
				}
			},
			'default': swagStc.GENERIC_FAILURE_RESPONSE,
		}
	}
	
	@staticmethod
	def __do__(wdr, logger):
		logger.trace("Doing a thing")
		return swagRsp.json(success=True, status='SUCCESS', data={'description': "successful operation"})
	#END DEF
#END CLASS