import apiAuth
from __swagger2__ import requests as swagRq
from __swagger2__ import responses as swagRsp
from v1 import statics as swagStc
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
		if wdr.swag['file-extension'] not in [None, '', 'html']:
			return swagRsp.httpStatus(wdr.request, "Not Implemented")
		#This HTML page uses the ReDoc tool, version 2.x
		#The page also assumes that 'swagger.json' is at the same level as 'docs.html'
		specUrl = (
			wdr.request['servletRequest']
				.getRequestURI()
				.replace(
					"docs{}".format(
						'.'+wdr.swag['file-extension']
						if wdr.swag['file-extension'] not in [None, '']
						else ''
					),
					"swagger.json"
				)
		)
		import textwrap
		HTML = '''
				<!DOCTYPE html>
				<html>
					<head>
						<title>API Docs - Company Name</title>
						<meta charset="utf-8"/>
						<meta name="viewport" content="width=device-width, initial-scale=1">
						<redoc spec-url="{!s}"
								lazy-rendering
								required-props-first
								path-in-middle-panel
								show-extensions>
						</redoc>
						<script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"> </script>
					</body>
				</html>
			'''.format(specUrl)
		return {'html': textwrap.dedent(HTML)}
	#END DEF

#END CLASS