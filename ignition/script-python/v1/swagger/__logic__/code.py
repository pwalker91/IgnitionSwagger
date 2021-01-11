import apiAuth
from __swagger2__ import requests as swagRq
from __swagger2__ import responses as swagRsp
from __swagger2__ import statics as swagStc
PREFIX = swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX



class GET(swagRq.HttpMethod):
	
	SWAGGER = {
		#Custom Ignition Swagger Keys
		PREFIX+'auth' : [
			{'method': apiAuth.simple.allowAll,},
		],
		PREFIX+'hide': True,
		PREFIX+'validateRequest': False,
		PREFIX+'validateResponse': False,
		PREFIX+'tagGroup': 'Documentation',
		
		#Normal Swagger Keys
		# !NOTE!
		# No normal Swagger keys are needed, since we won't being doing any validation of
		# the request or response.
	}
	
	@staticmethod
	def __do__(wdr, logger):
		if wdr.swag['file-extension'] != 'json':
			return swagRsp.httpStatus(wdr.request, "Not Implemented")
		logger.trace("Getting swagger.json")
		#Explicitly returning the response as a string (while still setting the 'contentType') so that
		# we don't need to return a Dictionary to Ignition. The whole point of generating the Swagger JSON
		# manually is so that the resulting String would have the JSON keys ordered in a specific way.
		return {
			'response': __swagger2__.json.toString( __swagger2__.json.toDict(wdr.request, wdr.session) ),
			'contentType': 'application/json'
		}
	#END DEF

#END CLASS