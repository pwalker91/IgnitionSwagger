'''
	This module has a few functions that are used to generate the Swagger JSON string.
'''

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# IMPORTS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import copy
import types
import re
from collections import OrderedDict
import textwrap
import pprint
import inspect
import sys
from com.inductiveautomation.ignition.common.script import ScriptPackage
#Other Ignition Project Script Modules that we will use
import server
from __swagger2__ import requests as swagRq
from __swagger2__ import globals as swagGl



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# LOGGER and CONSTANTS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
LIBRARY_LOGGER = server.getLogger("IgnitionSwagger2.json")



def getEndpoints(swagStc, parentPackage, endpointBase=''):
	'''
	@FUNC	Searches the given Ignition Script Package Resource for all Script Resources that have an Endpoint class.
	@PARAM	swagStc : Object, a Script Module containing the "Swagger Statics" for the API service
	@PARAM	parentPackage : Object, the Ignition Script Package Resource
	@PARAM	endpointBase : String, the base string for the Endpoints found in the Script Resources
	@RETURN	PyDictionary, where the key is the endpoint path, and the value is the Endpoint class.
	'''
	logger = LIBRARY_LOGGER.getSubLogger("getEndpoints")
	foundEndpoints = OrderedDict()
	
	swagPackageName = parentPackage.name
	if swagPackageName[:len(swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX)] == swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX:
		swagPackageName = "{{{!s}}}".format(parentPackage.name)
	fullPackageName = endpointBase+'/'+swagPackageName
	
	pModules = parentPackage.__dict__
	logger.debug("Processing {!s}".format(fullPackageName))
	logger.trace("Items to check = {!r}".format(pModules.keys()))
	for m in sorted(pModules.keys()):
		if m == '__swagger__':
			logger.debug("Skipping Ignition Script Package that has all the magic")
			continue
		if isinstance(pModules[m], ScriptPackage):
			logger.debug("Found a sub-package, '{!s}'".format(m))
			foundEndpoints.update( getEndpoints(swagStc, pModules[m], fullPackageName) )
		#I had issues using 'isinstance' to reliably test if the object `m` was a Script Module Resource, so
		# I'm just going to assume that if it's NOT a Script Package Resource and has the appropriate name, then
		# it probably is a Script Module Resource.
		elif m == swagStc.ENDPOINT_LOGIC_RESOURCE_NAME:
			logger.debug(
				"Found an item named '{!s}'. ".format(swagStc.ENDPOINT_LOGIC_RESOURCE_NAME) +
				"It should have some HTTP Methods. Adding to `foundEndpoints`"
			)
			foundEndpoints[fullPackageName] = pModules[m]
	#END FOR
	return foundEndpoints
#END DEF

def cleanSwagger(obj, swagStc):
	'''
	@FUNC	Parses a dictionary and removes all of the Ignition Swagger specific keys.
	@PARAM	obj : Dictionary, the dictionary to clean
	@PARAM	swagStc : Object, a Script Module containing the "Swagger Statics" for the API service
	'''
	newobj = {}
	for key in obj.keys():
		if key[:len(swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX)] == swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX:
			continue
		#Anything that isn't a dictionary won't have keys, so no "special keys" to clean out
		if isinstance(obj[key], types.DictionaryType):
			newobj[key] = cleanSwagger(obj[key], swagStc)
		else:
			newobj[key] = copy.deepcopy(obj[key])
	#END FOR
	return newobj
#END DEF

def toDict(request, session):
	'''
	@FUNC	Gathers all of the different Swagger definitions for the different endpoints.
	@PARAM	request : WebDev Request object
	@PARAM	session : WebDev Session object
	@RETURN	OrderedDict, the full Swagger definition for the API service.
	'''
	logger = LIBRARY_LOGGER.getSubLogger("toDict")
	tagGroups = {
		# "<NAME>" : ["<TAG1>", "<TAG2>", ...]
		# The key/value mapping here will later be turned in to what ReDoc expects, which is
		# a list of dictionaries with the keys 'name' and 'tags', which map to the key and value
		# of this dictionary.
	}
	validEndpoints = OrderedDict()
	rootPackage = swagGl.getRootPackage(request)
	swagStc = swagGl.getNamedModuleFromRoot(rootPackage, 'statics')
	swagDf = swagGl.getNamedModuleFromRoot(rootPackage, 'definitions')
	validEndpoints.update( getEndpoints(swagStc, rootPackage) )
	
	pathSwag = OrderedDict()
	for path in sorted(validEndpoints.keys()):
		logger.trace("Processing {!s}".format(path))
		for httpMethod in swagGl.VALID_METHODS.keys():
			logger.trace("Looking for class named '{!s}'".format(httpMethod))
			#No class for the HTTP method? skip
			if (httpMethod not in validEndpoints[path].__dict__ or
				not issubclass(validEndpoints[path].__dict__[httpMethod], swagRq.HttpMethod)
			):
				logger.trace("Did not find {!s}".format(httpMethod))
				continue
			#END IF
			methodClass = getattr(validEndpoints[path], httpMethod)
			#If the class doesn't have a `SWAGGER` attribute, skip
			if (not hasattr(methodClass, swagStc.ENDPOINT_SWAGGER_VARIABLE) or
				not isinstance(getattr(methodClass, swagStc.ENDPOINT_SWAGGER_VARIABLE, None), types.DictionaryType)
			):
				logger.trace(
					"Found class '{!s}' did not have the property '{!s}'".format(
						httpMethod, swagStc.ENDPOINT_SWAGGER_VARIABLE
					)
				)
				continue
			#END IF
			#If the Ignition Swagger attribute 'hide' is set to True, skip
			if (
				getattr(methodClass, swagStc.ENDPOINT_SWAGGER_VARIABLE, {})
					.get(swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX+'hide', False)
			):
				logger.trace(
					(	"Class '{!s}' has '{!s}' attribute, but dictionary has custom "+
						"'hide' property set to True. Skipping"
					).format(
						httpMethod, swagStc.ENDPOINT_SWAGGER_VARIABLE
					)
				)
				continue
			#END IF
			endpointMethodSwagger = getattr(methodClass, swagStc.ENDPOINT_SWAGGER_VARIABLE, {})
			
			#Replacing the extra content that had to be added to the Script Package's name, so that we could
			# correctly identify it as being a Path Parameter. For example, this will replace '{is-x-integer-pathParam}'
			# with the string '{pathParam}'
			pathParamRegex = (
				'\{' +
				'{}'.format(re.escape(swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX)) +
				'(?P<pathParamType>[a-z]+)\-'+
				'(?P<pathParamName>[a-zA-Z0-9_\-]*)'+
				'\}'
			)
			#We will need both the match object and the substitution string, since the substitution string is easier
			# to build starting from the original string. The match object will allow us to build the Swagger
			# definition for the path parameter.
			cleanPath = re.sub(pathParamRegex, '{\g<pathParamName>}', path)
			logger.trace("Original path={!r} | clean path={!r}".format(path, cleanPath))
			
			#Using the regex above, we need to create items in the Swagger's "parameter" key if the path
			# defines some Path Parameters.
			for mObj in re.finditer(pathParamRegex, path):
				if 'parameters' not in endpointMethodSwagger:
					endpointMethodSwagger['parameters'] = []
				mGroups = mObj.groupdict()
				logger.trace("Adding '{!s}' as Path Parameter to Swagger".format(mGroups['pathParamName']))
				endpointMethodSwagger['parameters'].append({
					'in': 'path',
					'name': mGroups['pathParamName'],
					'type': mGroups['pathParamType'],
					'required': True,
				})
			#END IF
			
			logger.trace("Getting 'clean' Swagger for method '{!s}' on path '{!s}'".format(httpMethod, path))
			if cleanPath not in pathSwag:
				pathSwag[cleanPath] = OrderedDict()
			pathSwag[cleanPath][httpMethod.lower()] = cleanSwagger(endpointMethodSwagger, swagStc)
			
			#The Swagger in the HTTP Method class should also define the Tags and Tag Group the endpoint
			# belongs under in the rendered documentation
			tagGroupName = endpointMethodSwagger.get(swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX+'tagGroup', 'Unknown')
			logger.trace("Found tag group {!r}".format(tagGroupName))
			if tagGroupName not in tagGroups:
				tagGroups[tagGroupName] = set()
			swaggerTags = endpointMethodSwagger.get('tags',[])
			if isinstance(swaggerTags, types.ListType):
				#Using set unioning to combine the given tags, and the already extracted tags
				tagGroups[tagGroupName] = tagGroups[tagGroupName] | set(swaggerTags)
			logger.trace("Current Tag Groups: {!r}".format(tagGroups))
		#END FOR
	#END FOR
	#If we didn't find any Endpoints that don't have a "Tag Group", then we can remove the key from the dictionary
	if 'Unknown' in tagGroups and len(tagGroups['Unknown']) == 0:
		tagGroups.pop('Unknown')
	logger.trace("Done processing all paths")
	
	swagDef = OrderedDict([
		('swagger', '2.0'),
		('host', swagStc.HOST_NAME),
		('basePath', '/'),
		('schemes', swagDf.SCHEMES),
		('info', swagDf.INFO),
		('securityDefinitions', swagDf.SECURITY),
		('definitions', swagDf.DEFINITIONS),
		('parameters', swagDf.PARAMETERS),
		('paths', pathSwag),
		('x-tagGroups', [{'name':name, 'tags':list(tagGroups[name])} for name in tagGroups]),
	])
	return swagDef
#END DEF

def toString(swagDef):
	'''
	@FUNC	Expecting an OrderDict, converts it into JSON manually, given that the system.util.jsonEncode
			function does not expect an OrderedDict
	@PARAM	swagDef : Ordered Dictionary, to become the Swagger JSON string
	@RETURN	String, the JSON that is our Swagger Definition
	'''
	swaggerString = "{"
	swaggerItems = []
	def itemToString(item):
		if isinstance(item, types.NoneType):
			return 'null'
		else:
			return system.util.jsonEncode(item)
	#END DEF
	for key in swagDef.keys():
		if isinstance(swagDef[key], types.DictionaryType):
			swaggerItems.append( '"{}":{}'.format(key, toString(swagDef[key])) )
		elif isinstance(swagDef[key], types.ListType):
			listString = '"{}":'.format(key)
			listItems = []
			for listItem in swagDef[key]:
				if isinstance(listItem, types.DictionaryType):
					listItems.append(toString(listItem))
				else:
					listItems.append(itemToString(listItem))
			#END FOR
			listString += '[{}]'.format(','.join(listItems))
			swaggerItems.append( listString )
		else:
			swaggerItems.append( ('"{}":'.format(key)) + itemToString(swagDef[key]) )
	#END FOR
	swaggerString += ','.join(swaggerItems)
	swaggerString += "}"
	return swaggerString
#END DEF