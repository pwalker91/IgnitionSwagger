'''
	This script contains the logic that translates a request to a WebDev Resource into an execution of a Script Resource.

	The function `processRequest` is what parses the Request and ends up with a reference to a Script Resource to execute.
	Every Script Resource should implement a class, `Endpoint`, which needs to inherit the class `BaseEndpoint`
	defined in this library.
'''

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# IMPORTS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import system
import sys
import types
import re
import copy
import pprint
import textwrap
import inspect
import importlib
import traceback
import java.lang.Exception
import java.lang.Double
import java.util.Date
from com.inductiveautomation.ignition.common.script import ScriptPackage
#Other Ignition Project Script Modules that we will use
import server
from __swagger2__ import responses as swagRsp
from __swagger2__ import globals as swagGl


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# LOGGER and CONSTANTS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
LIBRARY_LOGGER = server.getLogger("IgnitionSwagger2.requests")



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# CUSTOM EXCEPTION CLASSES
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class CustomExceptions:
	class WebDevRequestException(Exception):
		pass
	class InvalidRequestBodyException(WebDevRequestException):
		pass
	class InvalidHTTPMethodException(WebDevRequestException):
		pass
	class InvalidContentTypeException(WebDevRequestException):
		pass
	class HttpDataValidationException(WebDevRequestException):
		pass
	class InvalidWebDevRequestAugmentationException(WebDevRequestException):
		pass
	class EndpointException(Exception):
		pass
	class SwaggerBadReferenceException(EndpointException):
		pass
	class SwaggerParamPropMissingException(EndpointException):
		pass
	class SwaggerParamDefinitionInvalidException(EndpointException):
		pass
	class IgnitionSwaggerPropMissingException(EndpointException):
		pass
	class IgnitionSwaggerPropInvalidException(EndpointException):
		pass
	class EndpointInitializationException(EndpointException):
		pass
	class EndpointExecutionException(EndpointException):
		pass
#END CLASSes



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# WebDev Request WRAPPER AND FIXER
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class WebDevRequest(object):
	'''
	@CLASS	A wrapper around the `request` and `session` that extracts/cleans/fixes the information extracted
			from the HTTP Request. This classes is needed to instantiate a `BaseEndpoint` instance.
	@ATTR	request : WebDev Request Python Dictionary given during initialization
	@ATTR	session : WebDev Session Python Dictionary given during initialization
	@ATTR	swag : Python Dictionary, the cleaned up incoming request
	@ATTR	requestAugmentations : Python Dictionary, the extended attributes that have been added
				to the `request` attribute.
	@ATTR	logger : Gateway Logger object, based on the WebDev Request's URI Path. This variable will be
				initalized during the `processRequest` function.
	'''
	
	#The keys of this dictionary are the allowed "Request Extensions" that can be called, and
	# define the dependencies that they have, if they have any.
	REQUEST_AUGMENTATIONS_DEPENDENCIES = {
		'headers':		[],
		'uri':			[],
		'httpmethod':	['headers'],
		'content':		['headers','httpmethod'],
		'urlparams':	[],
	}
	
	
	def __init__(self, request, session):
		self.request = request
		self.session = session
		self.swag = {}
		self.requestAugmentations = {k:False for k in self.REQUEST_AUGMENTATIONS_DEPENDENCIES.keys()}

		#We will always execute this parsing during initialization, as the information is used later in may other places
		self.augmentRequestHeaders()
		self.augmentRequestHTTPMethod()
	#END DEF
	
	def __repr__(self):
		return "request={!r}\nsession={!r}\naugs={!r}\nswag={!r}".format(
			self.request, self.session, self.requestAugmentations, self.swag
		)
	#END DEF
	def __str__(self):
		return self.__repr__()
	#END DEF
	
	
	def _copyDictWithStringKeys(self, oldDict):
		'''
		@FUNC	Copy the dictionary given, but make sure that the keys are all of type String, not Unicode
		@PARAM	oldDict : Python Dictionary
		@RETURN	Python Dictionary
		'''
		if not isinstance(oldDict, types.DictionaryType):
			return oldDict
		oldCopy = copy.deepcopy(oldDict)
		newDict = {str(k):oldCopy[k] for k in oldCopy}
		for k in newDict:
			if isinstance(newDict[k], types.DictionaryType):
				newDict[k] = self._copyDictWithStringKeys(newDict[k])
			if isinstance(newDict[k], types.ListType):
				newDict[k] = [self._copyDictWithStringKeys(v) for v in newDict[k]]
		return newDict
	#END DEF
	
	def logInitialReceipt(self):
		'''
		@FUNC	Creates a log message containing some basic information about the HTTP request
		'''
		logger = LIBRARY_LOGGER.getSubLogger("WebDevRequest.initialRequestReceipt")
		baseRequestInfo = [
			"Method = {!s}".format(self.swag['original-http-method']),
			"RealMethod = {!s}".format(self.swag['http-method']),
			"SentTo = {!s}".format(system.tag.read("[System]Gateway/SystemName").value),
			"FromIP = {!s}".format(self.swag['headers-lc'].get('x-real-ip', self.request['remoteAddr'])),
			"URI = {!s}".format(self.request['servletRequest'].getRequestURI()),
			"Session = {!s}".format(system.util.jsonEncode(self.session))
		]
		logger.debug("Received an HTTP Request. See details for more info", baseRequestInfo)
		logger.trace("Original Request object. See details for more info", self.request)
		logger.trace("Original Session object. See details for more info", self.session)
	#END DEF
	
	def logIncomingData(self, dataLocation, data, signature):
		'''
		@FUNC	Creates a log message containing the appropriate incoming data (based on the HTTP Method)
				after obscuring the appropriate data.
		'''
		logger = LIBRARY_LOGGER.getSubLogger("WebDevRequest.incomingData")
		logableCopy = obscure(data, signature)
		logger.debug('Request Data (parsed from {!s})'.format(dataLocation), logableCopy)
	#END DEF
	
	def logOutgoingData(self, response, signature=None):
		'''
		@FUNC	Creates a log message containing the HTTP response
		'''
		logger = LIBRARY_LOGGER.getSubLogger("WebDevRequest.outgoingData")
		logableCopy = obscure(response, signature) if signature is not None else response
		logger.debug(
			"Response Code was {!s}. Data included in details".format(self.request['servletResponse'].getStatus()),
			logableCopy
		)
	#END DEF
	
	
	def __validate_augment_request_dependencies(self, aug, raiseExceptionOnInvalid=True):
		'''
		@FUNC	Validates that this instance, before trying to determine the augmented data for the WebDev
				Request Python Dictionary, meets the requirements for the given augmentation.
				eg. the "body" extension requires the "headers" and "httpmethod" augmentations to have been calculated
		@PARAM	aug : String, the augmentation we want to check
		@PARAM	raiseExceptionOnInvalid : Boolean, whether to raise an Exception when a dependency is not met, or
					just return a Boolean value of `False`.
		@RETURN Boolean, whether the dependencies for `aug` have been met.
		@RAISES InvalidWebDevRequestAugmentationException
		'''
		aug = str(aug).lower()
		if aug not in self.REQUEST_AUGMENTATIONS_DEPENDENCIES.keys():
			raise CustomExceptions.InvalidWebDevRequestAugmentationException(
				"Invalid Request Augmentation specified. "+
				"Valid types are {!r}".format(self.REQUEST_AUGMENTATIONS_DEPENDENCIES.keys())
			)
		#END IF
		for augDpd in self.REQUEST_AUGMENTATIONS_DEPENDENCIES[aug]:
			if not self.requestAugmentations[augDpd]:
				if raiseExceptionOnInvalid:
					raise CustomExceptions.InvalidWebDevRequestAugmentationException(
						"Cannot generate Request Augmentation. Dependencies not yet met. "+
						"Requires {!r}".format(self.REQUEST_AUGMENTATIONS_DEPENDENCIES[aug])
					)
				return False
			#END IF
		#END FOR
		return True
	#END DEF
	
	def augmentRequestHeaders(self, forceReCalcAug=False):
		'''
		@FUNC	Extracts more detailed "Header" data, based off what is given in the WebDev Request.
		@PARAM	forceReCalcAug : Boolean. If the augmentation has already be calculated, passing a True
					will tell the function to ignore that and recalc.
		@ADDS	['headers']
				['headers-lc']
		@RETURN	N/A
		'''
		mykey = 'headers'
		self.__validate_augment_request_dependencies(mykey)
		if self.requestAugmentations[mykey] and not forceReCalcAug:
			raise CustomExceptions.WebDevRequestException(
				"You cannot trigger the augmentation of the request {!s} multiple times.".format(mykey)
			)
		else:
			self.requestAugmentations[mykey] = False
			self.swag['headers'] = copy.deepcopy(self.request['headers'])
			self.swag['headers-lc'] = {k.lower():self.swag['headers'][k] for k in self.swag['headers']}
			self.requestAugmentations[mykey] = True
		#END IF/ELSE
		return
	#END DEF
	
	def augmentRequestHTTPMethod(self, forceReCalcAug=False):
		'''
		@FUNC	Extracts more detailed "HTTP Method" data, based off what is given in the WebDev Request.
		@PARAM	forceReCalcAug : Boolean. If the augmentation has already be calculated, passing a True
					will tell the function to ignore that and recalc.
		@ADDS	['original-http-method']
				['http-method']
		@RETURN	N/A
		'''
		mykey = 'httpmethod'
		self.__validate_augment_request_dependencies(mykey)
		if self.requestAugmentations[mykey] and not forceReCalcAug:
			raise CustomExceptions.WebDevRequestException(
				"You cannot trigger the augmentation of the request {!s} multiple times.".format(mykey)
			)
		else:
			self.requestAugmentations[mykey] = False
			originalMethod = self.request['servletRequest'].getMethod().upper()
			self.swag['original-http-method'] = originalMethod
			self.swag['http-method'] = (
					self.swag['headers-lc']['x-http-method-override'].upper()
					if 'x-http-method-override' in self.swag['headers-lc'] and originalMethod == 'POST'
					else originalMethod
				)
			if self.swag['http-method'] not in swagGl.VALID_METHODS.keys():
				raise CustomExceptions.InvalidHTTPMethodException(
					"Method '{!s}' is not valid.".format(self.swag['http-method'])
				)
			self.requestAugmentations[mykey] = True
		#END IF/ELSE
		return
	#END DEF
	
	def augmentRequestURI(self, uriBase="", forceReCalcAug=False):
		'''
		@FUNC	Extracts more detailed "URI" data, based off what is given in the WebDev Request.
		@PARAM	uriBase : String
		@PARAM	forceReCalcAug : Boolean. If the augmentation has already be calculated, passing a True
					will tell the function to ignore that and recalc.
		@ADDS	['uri-base']
				['file-extension']
				['resource-path']
		@RETURN	N/A
		'''
		mykey = 'uri'
		self.__validate_augment_request_dependencies(mykey)
		if self.requestAugmentations[mykey] and not forceReCalcAug:
			raise CustomExceptions.WebDevRequestException(
				"You cannot trigger the augmentation of the request {!s} multiple times.".format(mykey)
			)
		else:
			logger = LIBRARY_LOGGER.getSubLogger('WebDevRequest.augmentRequestURI')
			self.requestAugmentations[mykey] = False
			uri = self.request['servletRequest'].getRequestURI()
			logger.trace("Given URI = {!r}".format(uri))
			logger.trace("Given URI Base = {!r}".format(uriBase))
			logger.trace("Remaining Path = {!r}".format(self.request['remainingPath']))
			self.swag['file-extension'] = None if len(uri.rsplit('.',1)) == 1 else uri.rsplit('.',1)[-1].lower()
			self.swag['uri-base'] = uriBase.split('/')
			self.swag['resource-path'] = (
				uri	.replace(".{}".format(self.swag['file-extension']), '', 1)
					.split('/')[len(self.swag['uri-base']) : ]
			)
			self.requestAugmentations[mykey] = True
			logger.trace(
				"New Value in self.swag = (see details)",
				{k:self.swag[k] for k in ['file-extension','uri-base','resource-path']}
			)
		#END IF/ELSE
		return
	#END DEF
	
	def augmentRequestContent(self, contentType, forceReCalcAug=False):
		'''
		@FUNC	Extracts more detailed "Content" data, based off what is given in the WebDev Request.
		@PARAM	contentType : String
		@PARAM	forceReCalcAug : Boolean. If the augmentation has already be calculated, passing a True
					will tell the function to ignore that and recalc.
		@ADDS	['data']
		@ADDS	['original-data']
		@RETURN	N/A
		'''
		mykey = 'content'
		self.__validate_augment_request_dependencies(mykey)
		if self.requestAugmentations[mykey] and not forceReCalcAug:
			raise CustomExceptions.WebDevRequestException(
				"You cannot trigger the augmentation of the request {!s} multiple times.".format(mykey)
			)
		else:
			logger = LIBRARY_LOGGER.getSubLogger('WebDevRequest.augmentRequestContent')
			self.requestAugmentations[mykey] = False
			self.swag['data'] = self._copyDictWithStringKeys(self.request.get('data',None))
			#
			# make sure set, if ifs false
			#
			requestHTTPMethod = self.swag['http-method']
			requestContentType = self.swag['headers-lc'].get('content-type','UNKNOWN')
			#If the given Content Type is not one of the allowed types for the HTTP Method being called, throw
			# an exception. An HTTP Method that does not have any required Content Types will not be a list.
			if isinstance(swagGl.VALID_METHODS[requestHTTPMethod], types.ListType):
				if all([ctype not in requestContentType for ctype in swagGl.VALID_METHODS[requestHTTPMethod]]):
					raise CustomExceptions.InvalidContentTypeException(
						"Value in 'Content-Type' is not allowed for HTTP Method '{!s}'. ".format(requestHTTPMethod) +
						"Allowed types are '{!s}'.".format(swagGl.VALID_METHODS[requestHTTPMethod])
					)
			#END IF
			logger.trace("Determined Content-Type to be '{!s}'".format(contentType))
			if contentType in swagGl.VALID_CONTENT_TYPES:
				contentTypeParserClass = swagGl.VALID_CONTENT_TYPES[contentType]
				if not contentTypeParserClass.isvalid(self.swag['data']):
					logger.trace("Parsing Body as '{!s}' for HTTP METHOD '{!s}'".format(contentType, requestHTTPMethod))
					#Ideally, this simply updates the value of swag['data'], but other
					# keys could be added if deemed necessary by the contentTypeParserClass
					logger.trace("Un-parsed body = {!r}".format(self.request['data']))
					self.swag.update(
						contentTypeParserClass.parse(self.request)
					)
					logger.trace(
						"Parsing results. data = {!r} , original-data = {!r}".format(
							self.swag['data'], self.swag['original-data']
						)
					)
					if not contentTypeParserClass.isvalid(self.swag['data']):
						raise CustomExceptions.InvalidRequestBodyException(
							"Unable to parse HTTP Request Body as '{!s}'.".format(contentType) +
							"Given Content Type of '{!s}'".format(requestContentType)
						)
				else:
					logger.debug("Given data passed validity test")
				#END IF/ELSE
			else:
				raise CustomExceptions.InvalidContentTypeException(
					"The Content-Type '{!s}' is not a valid type at this time '{!s}'. ".format(contentType) +
					"Allowed types are '{!s}'.".format(swagGl.VALID_CONTENT_TYPES.keys())
				)
			#END IF
			logger.trace("Cleaned up Body, if necessary. Done with augmentation")
			self.requestAugmentations[mykey] = True
		#END IF/ELSE
		return
	#END DEF
#END CLASS



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# HTTP DATA SIGNATURE REPRESENTATION/PARSING (BASED ON A Swagger Definition)
# # For examples of the SWAGGER dictionaries, which are used to generate the "signatures"
#  used in this validation logic, refer to this internal confluence page.
# https://confluence.ia.local:8443/x/vwXCAQ
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class HttpDataSignature(dict):
	'''
	@CLASS	A simple class that acts exactly like a Python Dictionary, just named differently.
	'''
	def __init__(self, *args, **kwargs):
		super(HttpDataSignature, self).__init__(*args, **kwargs)
	def __eq__(self, other):
		return (isinstance(other, HttpDataSignature) and dict.__eq__(self, other))
#END CLASS

def getDataSignatureFromSwagger(swaggerdef, direction, qualifier, swagStc, swagDf):
	'''
	@FUNC	Uses a Swagger 2.0 definition to make a HttpDataSignature object for request/response validation.
			For more info on the structure of the definition, see the Swagger 2.0 specification at
			https://swagger.io/docs/specification/2-0/basic-structure/
			
			While the Swagger definition is quite explicit, request vs. response structure is slightly different, and
			I would like to reuse the validation function for validating both the request and the generated response.
			
			The keys in this dictionary are the possible keys in `data`, and each key in the signature maps to a Python
			Dictionary with the following keys present:
			 * required : Boolean, key must be in the "data"
			 * nullable : Boolean, key's value can be `None`
			 * type : String, the type of value that is expected
			
			Optional keys, some of which will default to a specific value if not present:
			 * signature
			 		- REQUIRED
					- for types [ array | object ]
					Python Dictionary, the signature of the items in the array/object.
					If the type is `array`, the key in the Python Dictionary will be 'item'
			 * format
					- REQUIRED
					- for types [ string | number ]
					String, the format of the data that is required.
					When the type is `number`, format can be `long`, `float`, or `double`.
					When the type is `string`, format can be `byte`, `date`, or `datetime`.
					An Exception will be thrown if no format provided.
			 * pattern
			 		- NOT required
					- for types [ string ]
					String, the regular expression that the string must match.
			 * minLength, maxLength
			 		- NOT required
					- for types [ string ]
					Integers, the min/max length the string must be. Range is inclusive
			 * minimum, maximum
			 		- NOT required
					- for types [ integer | number ]
					Integer/Float, the minimum or maximum number allowed for the parameter
			 * exclusiveMinimum, exclusiveMaximum
					- NOT required
					- for types [ integer | number ]
					Boolean, whether the `minimum` and/or `maximum` restriction is an inclusive or exclusive range
			 * minItems, maxItems
					- NOT required
					- for types [ array ]
					Integer, the minimum or maximum number of items allowed in the array. Range is inclusive
			 * uniqueItems
					- NOT required
					- for types [ array ]
					Boolean, whether every item in the array needs to be unique
			 * collectionFormat
					- NOT required
					- for types [ array ]  !! Only when "in" is not "body"
					String, the format of the incoming array. Supported formats are:
						- "csv" : Comma-separated values
						- "ssv" : Space-separated values
						- "pipes" : Pipe character (ie. "|") separated values
			 * default
			 		- NOT required
					- for ALL types
					Python Object, a default value that should be put in the key if not provided.
						If the key is REQUIRED (ie. "required" = True), the value in the will never become
						the "default" value given.
			 * enum
					- NOT required
					- for ALL type
					PyList of values, the valid values for the key.
			 * swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX + obscure
					- NOT required
					- for ALL types
					Boolean, whether to obscure the data given in the key, if data and signature are passed
						to the `obscure` function
	
	@PARAM	swaggerdef : Python Dictionary
	@PARAM	direction : String, the direction the data is being transferred that will need to be validated
				* ALLOWED VALUES = 'incoming', 'outgoing'
	@PARAM	qualifier : String, the qualifier specific to the direction.
				* eg. direction='incoming', qualifier='query', 'path', etc.
				      direction='outoing', qualifier='200', '404', etc.
	@PARAM	swagStc : Script Module Reference, a ref to the "Swagger Statics" script module for the endpoint.
				This is needed so that the IGNITION_SWAGGER_CUSTOM_PREFIX value can be referenced
	@PARAM	swagDf : Script Module Reference, a ref to the "Swagger Definitions" script module for the endpoint.
	
	@RETURN	HttpDataSignature Object (a glorified Python Dictionary)
	'''
	logger = LIBRARY_LOGGER.getSubLogger('getDataSignatureFromSwagger')
	if not isinstance(swaggerdef, types.DictionaryType):
		raise Exception("Swagger definition must be a Python Dictionary.")
	
	def getRef(ref):
		parts = ref.split('/')
		#tests for bad reference, cannot locate the correct struture.
		if len(parts) != 3 and parts[0] != '#':
			raise CustomExceptions.SwaggerBadReferenceException("Bad reference. Ref String did not start with '#'")
		refTypes = ('definitions','parameters')
		if parts[1] not in refTypes:
			raise CustomExceptions.SwaggerBadReferenceException(
				"Bad reference. Ref String had bad grouping. Acceptable groupings are {!r}".format(refTypes)
			)
		refGrouping = getattr(swagDf, parts[1].upper(), {})
		refDef = refGrouping.get(parts[2], None)
		if refDef is None:
			raise CustomExceptions.SwaggerBadReferenceException(
				"Bad reference. Reference '{!s}' does not exists.".format(ref)
			)
		return refDef
	#END DEF
	
	def extractForSig(paramSwag, dataLocation):
		'''
		@FUNC	Converts the Swagger definition of a parameter into an object that we can properly
				use it in the `validate` function
		@PARAM	paramSwag : Dictionary, the 
		'''
		if not isinstance(paramSwag, types.DictionaryType):
			raise Exception("Swagger Definition must be a Python Dictionary")
		
		#Getting the "actual" parameter definition from our "definitions"
		if '$ref' in paramSwag:
			paramSwag = getRef(paramSwag['$ref'])
		if 'type' not in paramSwag:
			raise CustomExceptions.SwaggerParamPropMissingException("Every Swagger Parameter must have a type.")
		#Only certain types of data types are allowed for locations of data. For example, we can't accept
		# an "object" as a "path" parameter.
		if paramSwag['type'] not in swagGl.VALID_SWAGGER_TYPES[dataLocation]:
			raise CustomExceptions.SwaggerParamDefinitionInvalidException(
				"Parameter of type '{!s}' not allowed as a 'in={!s}' parameter.".format(
					paramSwag['type'], dataLocation
				)
			)
		#The required-ness of a parameter is either defined in the `paramSwag` object (ie. for Query, URL, or
		# Form Data parameters), or is in the parent Dictionary that defines the parameters expected in itself.
		#If the parameter we are processing is expected to be delivered inside an object, then its required-ness
		# will be overwritten later.
		if 'required' in paramSwag and not isinstance(paramSwag['required'], types.ListType):
			if not isinstance(paramSwag['required'], types.BooleanType):
				raise CustomExceptions.SwaggerParamPropMissingException(
					"Query/Form Parameters must defined the `required` property as a Boolean."
				)
		#END IF
		
		#Each HttpDataSignature will always have type, required, and nullable
		sig = HttpDataSignature(
			type = paramSwag['type'],
			required = paramSwag.get('required', False),
			nullable = bool(paramSwag.get('x-nullable',True)),
		)
		
		#These properties have a more optional property that those described in swagGl.BASIC_PARAMETER_FIELDS,
		# so we will process them outside of the more abstract loop used later.
		if 'allowEmptyValue' in paramSwag:
			sig['allowEmptyValue'] = bool(paramSwag['allowEmptyValue'])
		if 'enum' in paramSwag:
			sig['enum'] = paramSwag['enum']
		if 'default' in paramSwag:
			sig['default'] = paramSwag['default']
		if swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX+'obscure' in paramSwag:
			sig['obscure'] = bool(paramSwag[swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX+'obscure'])
		
		#Some of the fields in a Swagger Parameter can be validated more easily, by simply testing if the fields
		# are present and of the correct Python type.
		parameterTypesBasicFields = swagGl.BASIC_PARAMETER_FIELDS.get(paramSwag['type'],{})
		for basicFieldName in parameterTypesBasicFields:
			fieldRules = parameterTypesBasicFields[basicFieldName]
			if fieldRules['required'] and basicFieldName not in paramSwag:
				raise CustomExceptions.SwaggerParamPropMissingException(
						"Parameter of type '{!s}' must have Swagger Key '{!s}' defined.".format(
							paramSwag['type'], basicFieldName
						)
					)
			if basicFieldName in paramSwag:
				logger.trace("Parameter signature has the '{!s}' key.".format(basicFieldName))
				if not isinstance(paramSwag[basicFieldName], fieldRules['valueType']):
					raise CustomExceptions.SwaggerParamDefinitionInvalidException(
							"'{!s}' Swagger Key for parameter of type '{!s}' must be a {!s}".format(
								basicFieldName, paramSwag['type'], fieldRules['valueType']
							)
						)
				if ('allowedValues' in fieldRules and
					paramSwag[basicFieldName] not in fieldRules['allowedValues']
				):
					raise CustomExceptions.SwaggerParamDefinitionInvalidException(
						"'{!s}' Swagger Key for parameter of type '{!s}'".format(basicFieldName, paramSwag['type'])+
						" must be one of the following values: {!r}".format(fieldRules['allowedValues'])
					)
				sig[basicFieldName] = paramSwag[basicFieldName]
			#END IF
		#END FOR
		
		#For some other data types, we need to do some "special" processing of the Swagger Definition to create
		# an HttpDataSignature. Basically, just 'object' and 'array', which are kinda unique
		if paramSwag['type'] == 'object':
			sig['signature'] = HttpDataSignature()
			#We will NOT throw an Exception if the key 'properties' is not in the Swagger definition for an 'object' type
			# parameter. This way, an endpoint can be defined as accepting an object, but not care what kind of data
			# is given.
			if 'properties' in paramSwag:
				for key in paramSwag['properties']:
					sig['signature'][key] = extractForSig(paramSwag['properties'][key], dataLocation)
					#After generating the signature for each parameter in the object, we overwrite its required-ness
					# based on the list of String that define the required parameters in the object.
					sig['signature'][key]['required'] = key in paramSwag.get('required',[])
			#END IF
		elif paramSwag['type'] == 'array':
			sig['signature'] = HttpDataSignature()
			#We will NOT throw an Exception if the key 'items' is not in the Swagger definition for an 'array' type
			# parameter. This way, an endpoint can be defined as accepting an array, but not care what kind of data
			# is given.
			if 'items' in paramSwag:
				if not isinstance(paramSwag['items'], types.DictionaryType):
					raise CustomExceptions.SwaggerParamPropMissingException(
						"A parameter definiton of type 'array' must contain a Python Dictionary in the key 'items', "+
						"the Swagger definition of the values expected."
					)
				sig['signature']['items'] = extractForSig(paramSwag['items'], dataLocation)
			#END IF
			#If this 'array' is not data that is expected in an HTTP Body, then it will need to have a "collection
			# format". We need to verify that the format is one of our expected types
			if dataLocation != 'body':
				if 'collectionFormat' not in paramSwag:
					raise CustomExceptions.SwaggerParamPropMissingException(
						"Parameter of type '{!s}' must have Swagger Key '{!s}' defined.".format(
							paramSwag['type'], 'collectionFormat'
						)
					)
				if not isinstance(paramSwag['collectionFormat'], types.StringTypes):
					raise CustomExceptions.SwaggerParamDefinitionInvalidException(
						"'{!s}' Swagger Key for parameter of type '{!s}' must be a {!s}".format(
							'collectionFormat', paramSwag['type'], types.StringTypes
						)
					)
				if paramSwag['collectionFormat'] not in swagGl.VALID_SWAGGER_ARRAY_COLLECTION_FORMATS.keys():
					raise CustomExceptions.SwaggerParamDefinitionInvalidException(
						"'{!s}' Swagger Key for parameter of type '{!s}'".format(
							'collectionFormat', paramSwag['type']
						)+
						" must be one of the following values: {!r}".format(
							swagGl.VALID_SWAGGER_ARRAY_COLLECTION_FORMATS.keys()
						)
					)
				sig['collectionFormat'] = paramSwag['collectionFormat']
			#END IF
		#END IF/ELIF (special rules per type)
		
		return sig
	#END DEF
	
	# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	#Validating that the callee gave us a valid "direction"
	direction = str(direction)
	acceptableDirections = ['incoming','outgoing']
	if direction not in acceptableDirections:
		raise Exception("The `direction` parameter must be one of the accepted values: {!r}".format(acceptableDirections))
	
	datSig = HttpDataSignature()
	
	#
	# https://swagger.io/docs/specification/2-0/describing-parameters/
	# https://swagger.io/docs/specification/2-0/describing-request-body/
	#
	if direction == 'incoming':
		if qualifier not in swagGl.VALID_SWAGGER_IN.keys():
			raise CustomExceptions.Exception(
				"The incoming response qualifier '{!s}' is not valid. Accepted Values are {!r}.".format(
					qualifier, swagGl.VALID_SWAGGER_IN.keys()
				)
			)
		if swaggerdef.get('parameters',None) is None or not isinstance(swaggerdef.get('parameters',None), types.ListType):
			logger.debug(
				"'parameters' key in Swagger is not a List. No signature to extract for '{!s}'".format(qualifier)
			)
			return datSig
		for param in swaggerdef['parameters']:
			if '$ref' in param:
				param = getRef(param['$ref'])
			if param['in'] != qualifier:
				logger.trace("The parameter we are processing is not expected to come in the '{!s}'".format(qualifier))
				continue
			#At this point, we know that the param's "in" definition matches the qualifier.
			if qualifier == 'body':
				#We expect the 'body' type parameter to have a schema. If the 'schema' key is
				# not found, we will use an empty dictionary as a default
				schema = param.get('schema', {})
				#The signature for an HTTP Body will always be of type 'object'
				schema['type'] = 'object'
				#The 'in:body' type is unique, as it is allowed objects
				logger.trace("Extracting incoming signature for Body")
				datSig.update( extractForSig(schema, qualifier)['signature'] )
				#The requirement of items in an object is defined by the Object, not by the item in the object.
				for key in param['schema'].get('properties',{}):
					datSig[key]['required'] = key in param['schema'].get('required',[])
			else:
				#All other "in"s will use a more simple method for extracting the correct
				# varaible signature. The "in" qualifier is probably among the following:
				# - formData, query, header, path
				if 'name' not in param:
					raise CustomExceptions.SwaggerParamPropMissingException(
						"Every parameter with a definition must have a name. Definition given '{!r}'.".format(param)
					)
				logger.debug(
					"Extracting incoming signature for '{!s}', which is expected to be in '{!s}'".format(
						param['name'], qualifier
					)
				)
				datSig[param['name']] = extractForSig(param, qualifier)
			#END IF/ELSE
		#END FOR
	#
	# https://swagger.io/docs/specification/2-0/describing-responses/
	#
	elif direction == 'outgoing':
		if ('produces' not in swaggerdef or
			not isinstance(swaggerdef.get('produces',None), types.ListType) or
			not filter(lambda v:isinstance(v,types.StringTypes), swaggerdef['produces'])
		):
			raise CustomExceptions.SwaggerParamDefinitionInvalidException(
				"You must specify what kind of data will be returned by the endpoint in the 'produces' "+
				"key of the Swagger. Please provide a list of Strings."
			)
		if 'application/json' not in swaggerdef['produces']:
			#The developer is allowed to define an endpoint that does not return JSON. However, this means
			# that no response validation will be done by the translation process.
			logger.debug('Outgoing data is not JSON. No data that we can validate')
			return datSig
		if (swaggerdef.get('responses',None) is None or
			not isinstance(swaggerdef.get('responses',None), types.DictionaryType)
		):
			logger.debug("No dictionary of possible responses in Swagger definition")
			return datSig
		if qualifier not in swaggerdef['responses']:
			raise Exception(
				"The outgoing response qualifier '{!s}'".format(qualifier) +
				" does not exist in the Swagger's `responses` dictionary."
			)
		if '$ref' in swaggerdef['responses'].get(qualifier, {}).keys():
			schema = getRef(swaggerdef['responses'][qualifier]['$ref']).get('schema',None)
		else:
			schema = swaggerdef['responses'].get(qualifier,{}).get('schema',None)
		if schema is None or not isinstance(schema, types.DictionaryType):
			logger.debug("No schema found for definition of '{!s}' response.".format(qualifier))
			return datSig
		schemaType = schema.get('type',"string")
		if schemaType == 'object':
			#When creating a signature for a response, the "data location" is always the body, since we are only
			# creating response signatures for JSON responses that have a 'schema' defined, similar to how
			# the HTTP Body parameters are defined.
			logger.debug("Extracting outgoing signature for definition of '{!s}' object response".format(qualifier))
			datSig = extractForSig(schema, 'body')['signature']
			for key in schema.get('properties',{}):
				datSig[key]['required'] = key in schema.get('required',[])
		elif schemaType == 'string':
			logger.debug("Outgoing response specified as a type 'string'.")
			pass
			# # # # # # # # # #
			# TODO:
			# The logic here should handle different types of responses more gracefully.
			# This will likely require some more abstraction into how the `Endpoint` class handles
			#  the validation of a generated response.
			# # # # # # # # # #
		else:
			raise Exception("The outgoing response needs to have a valid specified 'type'.")
	#END IF/ELSE
	return datSig
#END DEF

def obscure(data, sig):
	'''
	@FUNC	Obscures the given dictionary based on the given HTTP Data Signature object
	@PARAM	data : Python Dictionary
	@PARAM	sig : HttpDataSignature Object
	@RETURN	Python Dictionary, the original data with the defined keys obscured (ie. changed to "REDACTED")
	'''
	logger = LIBRARY_LOGGER.getSubLogger('obscure')
	logger.debug("Received data of type {!s}. (see details for signature)".format(type(data)), sig)
	if not isinstance(data, types.DictionaryType):
		raise Exception('Obscuring of data requires a Python Dictionary object for the first parameter.')
	if not isinstance(sig, HttpDataSignature):
		raise Exception('Obscuring of data requires an HttpDataSignature object for the second parameter.')
	logger.trace("Given data and signature are the valid data types.")
	newdata = copy.deepcopy(data)
	for key in sig:
		logger.trace("Processing key '{!s}'".format(key))
		if key not in newdata:
			logger.trace("Key '{!s}' not in data. Skipping...".format(key))
			continue
		#Only obscure data if specified in the Data Signature Dictionary. Note that the Swagger uses the
		# key 'custom prefix'+'obscure', which then becomes the key 'obscure'
		# in the Data Signature Dictionary
		if 'obscure' in sig[key] and bool(sig[key]['obscure']):
			logger.trace("Redacting value for key '{!s}'!".format(key))
			newdata[key] = 'REDACTED'
		elif isinstance(newdata[key], types.DictionaryType):
			logger.trace("Key '{!s}' maps to a dictionary. Making recursive call...".format(key))
			newdata[key] = obscure( newdata[key], sig[key].get('signature',HttpDataSignature()) )
		elif isinstance(newdata[key], types.ListType):
			logger.trace("Key '{!s}' maps to a list. Redacting all data!".format(key))
			newListOfData = []
			for item in newdata[key]:
				arrayItem = {}
				arrayItem['items'] = item
				newListOfData.append(
					obscure(
						arrayItem,
						sig[key].get('signature',HttpDataSignature())
					)['items']
				)
			#END FOR
			newdata[key] = (
				(['REDACTED'] if 'REDACTED' in newListOfData else []) +
				filter(lambda v:v!='REDACTED', newListOfData)
			)
		#END IF/ELIF/ELIF
	#END FOR
	return newdata
#END DEF



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# HTTP REQUEST DATA VALIDATION
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class HttpDataValidation(dict):
	'''
	@CLASS	A simple class that acts exactly like a Python Dictionary, just named differently.
	'''
	BASE_VALIDATION = {
		'valid': False,
		'found': False,
		'type': 'unknown',
		'items': None,
		'message': None
	}
	
	def __init__(self, *args, **kwargs):
		super(HttpDataValidation, self).__init__(*args, **kwargs)
		#A quick reference to whether the Validation object says that things are good or bad. This
		# will be set at the end of `validate`, which takes a given object of "Data" and a "Signature"
		# for that data, and returns an instance of this HttpDataValidation object.
		#`ALL_VALID` will be set in the `validate` function.
		self.ALL_VALID = False
	#END DEF
	
	def __eq__(self, other):
		return (isinstance(other, HttpDataValidation) and dict.__eq__(self, other))
	#END DEF
	
	def addKey(self, key):
		'''
		@FUNC	A simple function to create a new key that refers to a copy of BASE_VALIDATION
		@PARAM	key : String, the new index
		'''
		self[key] = copy.deepcopy(self.BASE_VALIDATION)
	#END DEF
	
	def __getMissingKeys(self, dataParent, parentName):
		'''
		@FUNC	Gathers a list of all of the keys that are missing
		@PARAM	dataParent : Dictionary, the data to process
		@PARAM	parentName : String, the name of the parent, if the data being processed is nested data
		'''
		issues = []
		for key in dataParent:
			if not dataParent[key]['valid'] and not dataParent[key]['found']:
				issues.append(
					"Missing value for '{!s}' in {!s}".format(
						key,
						parentName if parentName is not None else "given data"
					)
				)
			if dataParent[key]['type'] in ('object','array') and dataParent[key]['items'] is not None:
				if dataParent[key]['type'] == 'array':
					for validationObj in dataParent[key]['items']:
						issues.extend(
							self.__getMissingKeys(
								validationObj,
								"Array "+key+('' if parentName is None else " in {!s}".format(parentName))
							)
						)
					#END FOR
				else:
					issues.extend(
						self.__getMissingKeys(
							dataParent[key]['items'],
							"Object "+key+('' if parentName is None else " in {!s}".format(parentName))
						)
					)
				#END IF/ELSE
		#END FOR
		return issues
	#END DEF
	
	def __getDataValidationIssues(self, dataParent, parentName):
		'''
		@FUNC	Gathers a list of all of the data that was not valid.
		@PARAM	dataParent : Dictionary, the data to process
		@PARAM	parentName : String, the name of the parent, if the data being processed is nested data
		'''
		issues = []
		for key in dataParent:
			if not dataParent[key]['valid'] and dataParent[key]['found'] and dataParent[key]['message'] is not None:
				issues.append(
					"'{!s}' in {!s}: {!s}".format(
						key,
						parentName if parentName is not None else "given data",
						dataParent[key]['message']
					)
				)
			if dataParent[key]['type'] in ('object','array') and dataParent[key]['items'] is not None:
				if dataParent[key]['type'] == 'array':
					for validationObj in dataParent[key]['items']:
						issues.extend(
							self.__getDataValidationIssues(
								validationObj,
								"Array '{!s}'".format(key) + ('' if parentName is None else " in {!s}".format(parentName))
							)
						)
					#END FOR
				else:
					issues.extend(
						self.__getDataValidationIssues(
							dataParent[key]['items'],
							"Object '{!s}'".format(key) + ('' if parentName is None else " in {!s}".format(parentName))
						)
					)
				#END IF/ELSE
		#END FOR
		return issues
	#END DEF
	
	def __str__(self):
		'''
		@FUNC	Converts the given object into a more readable string that can be returned to an API consumer.
		'''
		if self.ALL_VALID:
			return "No validation issues."
		allIssuesStr = (
			"The following errors were encountered ||   "+
			"  ||  ".join(
				self.__getMissingKeys(self, None) +
				self.__getDataValidationIssues(self, None)
			)
		)
		return allIssuesStr
	#END DEF
#END CLASS

class data_validation:
	'''
	@CLASS	Has the generic functions for validating that a Python Dictionary has all of necessary keys with
			values of a specific data types.
	'''
	
	@staticmethod
	def _getTypeErrorMessage(data, key, dataType):
		return "Expected type {!s} (received {!s} instead)".format( dataType, type(data[key]) )
	#END DEF
	
	@staticmethod
	def _validate_string(data, signature, key, **kwargs):
		'''
		Special signature keys:
			- format
			- pattern
			- minLength
			- maxLength
		'''
		logger = LIBRARY_LOGGER.getSubLogger('validate_string')
		logger.trace("For key '{!s}', got data of type {!s}".format(key, type(data[key])))
		
		if ('format' in signature[key] and
			signature[key]['format'] in swagGl.BASIC_PARAMETER_FIELDS['string']['format']['allowedValues']
		):
			if signature[key]['format'] == 'byte':
				data_validation.__validate_string_byte(data, signature, key, **kwargs)
			elif signature[key]['format'] in ['date','datetime']:
				data_validation.__validate_string_date(data, signature, key, **kwargs)
			else:
				raise CustomExceptions.HttpDataValidationException(
					"Somehow tried to process a String format that is invalid. Got '{!s}'".format(
						signature[key]['format']
					)
				)
			#END IF/ELIF/ELSE
		else:
			if not isinstance(data[key], types.StringTypes):
				raise CustomExceptions.HttpDataValidationException(
						data_validation._getTypeErrorMessage(data, key, 'string')
					)
				#Note that we don't attempt any type casting of the value if it is not a String. This is because
				# every object has a string form, and we want this validation to be a little strict.
			#END IF
			if 'pattern' in signature[key]:
				logger.trace("Checking if string matches pattern '{!s}'".format(signature[key]['pattern']))
				if re.match(signature[key]['pattern'], data[key]) is None:
					raise CustomExceptions.HttpDataValidationException(
						"String '{!s}' does not match regex pattern '{!s}'".format(
							data[key], signature[key]['pattern']
						)
					)
			if 'minLength' in signature[key] or 'maxLength' in signature[key]:
				if 'minLength' in signature[key] and 'maxLength' in signature[key]:
					logger.trace(
						"Checking if string is between {!s} and {!s} characters long".format(
							signature[key]['minLength'], signature[key]['maxLength']
						)
					)
					if not (signature[key]['minLength'] <= len(data[key]) <= signature[key]['maxLength']):
						raise CustomExceptions.HttpDataValidationException(
							"Value is not between {!s} and {!s} characters in length".format(
								signature[key]['minLength'], signature[key]['maxLength']
							)
						)
				#END IF
				elif 'minLength' in signature[key]:
					logger.trace(
						"Checking if string is at least {!s} characters long".format(signature[key]['minLength'])
					)
					if len(data[key]) < signature[key]['minLength']:
						raise CustomExceptions.HttpDataValidationException(
							"Value must be greater than or equal to {!s} characters in length".format(
								signature[key]['minLength']
							)
						)
				#END IF
				elif 'maxLength' in signature[key]:
					logger.trace(
						"Checking if string is no more than {!s} characters long".format(signature[key]['maxLength'])
					)
					if len(data[key]) > signature[key]['maxLength']:
						raise CustomExceptions.HttpDataValidationException(
							"Value must be less than or equal to {!s} characters in length".format(
								signature[key]['maxLength']
							)
						)
				#END IF
			#END IF
		#END IF
	#END DEF
	
	@staticmethod
	def __validate_string_date(data, signature, key, **kwargs):
		'''
		No special signature keys.
		'''
		logger = LIBRARY_LOGGER.getSubLogger('validate_string_date')
		dateFormat = swagGl.VALID_SWAGGER_DATE_FORMATS.get(signature[key]['format'])
		#If this data is going back in a response, then we need to make sure that we either have a Date Object
		# (which we can format into the appropriate format) or a Date String in the appropriate format
		if kwargs.get('isForResponse',False):
			logger.trace("Formatting a Date Object into a Date String [format='{!s}']".format(dateFormat))
			if isinstance(data[key], java.util.Date):
				logger.trace("Formatting Date Object in to Date String")
				data[key] = system.date.format(data[key], dateFormat)
			elif isinstance(data[key], types.StringTypes):
				logger.trace(
					"Expected to have a Date Object, but we have a String. Checking if "+
					"the String is in the proper format"
				)
				success = False
				try:
					logger.trace("Attempting to parse Date String")
					system.date.parse(data[key], dateFormat)
					success = True
				except:
					pass
				#END TRY/EXCEPT
				if not success:
					raise CustomExceptions.HttpDataValidationException(
						data_validation._getTypeErrorMessage(
							data, key, "Date string [format '{!s}']".format(dateFormat)
						)
					)
				logger.trace("Date String was in proper format. Leaving value as it was given")
			else:
				raise CustomExceptions.HttpDataValidationException(
					data_validation._getTypeErrorMessage(
						data, key, "Date Object or Date string [format '{!s}']".format(dateFormat)
					)
				)
			#END IF/ELIF/ELSE
		else:
			logger.trace("Parsing a Date String in to a Date Object [format='{!s}']".format(dateFormat))
			if not isinstance(data[key], types.StringTypes):
				raise CustomExceptions.HttpDataValidationException(
						data_validation._getTypeErrorMessage(data, key, 'string')
					)
			#END IF
			if isinstance(data[key], java.util.Date):
				pass
			elif not isinstance(data[key], types.StringTypes):
				raise CustomExceptions.HttpDataValidationException(
					data_validation._getTypeErrorMessage(
						data, key, "Date String"
					)
				)
			else:
				success = False
				try:
					logger.trace("Attempting to parse Date String")
					data[key] = system.date.parse(data[key], dateFormat)
					success = True
				except:
					pass
				#END TRY/EXCEPT
				if not success:
					raise CustomExceptions.HttpDataValidationException(
						data_validation._getTypeErrorMessage(
							data, key, "Date String [format '{!s}']".format(dateFormat)
						)
					)
			#END IF/ELSE
		#END IF/ELSE
	#END DEF
	
	@staticmethod
	def __validate_string_byte(data, signature, key, **kwargs):
		'''
		No special signature keys.
		'''
		logger = LIBRARY_LOGGER.getSubLogger('validate_string_byte')
		pass
		# # # # # #
		# TODO!
		#	process given string
		#	base64 decode
		#	throw error if unable to decode
		# # # # # #
	#END DEF
	
	@staticmethod
	def _validate_boolean(data, signature, key, **kwargs):
		'''
		No special signature keys.
		'''
		logger = LIBRARY_LOGGER.getSubLogger('validate_boolean')
		logger.trace("For key '{!s}', got data of type {!s}".format(key, type(data[key])))
		if not isinstance(data[key], types.BooleanType):
			doTypeCasting = kwargs.get('doTypeCasting', False)
			logger.trace("Type casting variable? {!r}".format(doTypeCasting))
			if not doTypeCasting:
				raise CustomExceptions.HttpDataValidationException(
					data_validation._getTypeErrorMessage(data, key, 'boolean')
				)
			else:
				try:
					data[key] = bool(data[key])
				except:
					raise CustomExceptions.HttpDataValidationException(
						data_validation._getTypeErrorMessage(data, key, 'boolean')
					)
			#END IF/ELSE
		#END IF
	#END DEF
	
	@staticmethod
	def _validate_number(data, signature, key, **kwargs):
		'''
		Special signature keys:
			- format
			- minimum
			- maximum
			- exclusiveMinimum
			- exclusiveMaximum
		'''
		logger = LIBRARY_LOGGER.getSubLogger('validate_number')
		logger.trace("For key '{!s}', got data of type {!s}".format(key, type(data[key])))
		
		numFormat = signature[key].get('format','float')
		formatType = {
			'integer': types.IntType, #this is here so that '_validate_integer' can reuse the logic below
			'float': types.FloatType,
			'double': java.lang.Double,
			'long': types.LongType,
		}.get(numFormat,None)
		logger.trace("Checking if number is of type {!s}".format(numFormat))
		if formatType is None:
			raise CustomExceptions.HttpDataValidationException("Invalid number type '{!s}'".format(numFormat))
		
		if not isinstance(data[key], formatType):
			doTypeCasting = kwargs.get('doTypeCasting', False)
			logger.trace("Type casting variable? {!r}".format(doTypeCasting))
			if not doTypeCasting:
				raise CustomExceptions.HttpDataValidationException(
					data_validation._getTypeErrorMessage(data, key, numFormat)
				)
			else:
				try:
					data[key] = formatType(data[key])
				except:
					raise CustomExceptions.HttpDataValidationException(
						data_validation._getTypeErrorMessage(data, key, numFormat)
					)
			#END IF/ELSE
		#END IF
		
		if 'minimum' in signature[key] or 'maximum' in signature[key]:
			if 'minimum' in signature[key] and 'maximum' in signature[key]:
				logger.trace(
					"Checking if value is between {!s} and {!s}. Exclusive min? {!r}  Exclusive max? {!r}".format(
						signature[key]['minimum'], signature[key]['maximum'],
						signature[key].get('exclusiveMinimum',False),
						signature[key].get('exclusiveMaximum',False)
					)
				)
				_failed = False
				if signature[key].get('exclusiveMinimum',False) and signature[key].get('exclusiveMaximum',False):
					_failed = not (signature[key]['minimum'] < data[key] < signature[key]['maximum'])
				elif signature[key].get('exclusiveMinimum',False):
					_failed = not (signature[key]['minimum'] < data[key] <= signature[key]['maximum'])
				elif signature[key].get('exclusiveMaximum',False):
					_failed = not (signature[key]['minimum'] <= data[key] < signature[key]['maximum'])
				else:
					_failed = not (signature[key]['minimum'] <= data[key] <= signature[key]['maximum'])
				#END IF/ELIF/ELSE
				if _failed:
					raise CustomExceptions.HttpDataValidationException(
						"Value is not in the range {!s}{!s} to {!s}{!s}".format(
							signature[key]['minimum'], signature[key]['maximum'],
							'(exclusively)' if signature[key].get('exclusiveMinimum',False) else '',
							'(exclusively)' if signature[key].get('exclusiveMaximum',False) else '',
						)
					)
			#END IF
			elif 'minimum' in signature[key]:
				logger.trace(
					"Checking if value is more than {!s}. Exclusive min? {!r}".format(
						signature[key]['minimum'], signature[key].get('exclusiveMinimum',False)
					)
				)
				_failed = False
				if signature[key].get('exclusiveMinimum',False):
					_failed = data[key] < signature[key]['minimum']
				else:
					_failed = data[key] <= signature[key]['minimum']
				#END IF/ELSE
				if _failed:
					raise CustomExceptions.HttpDataValidationException(
						"Value must be greater than {!s}{!s}".format(
							'' if signature[key].get('exclusiveMinimum',False) else 'or equal to ',
							signature[key]['minimum'],
						)
					)
			#END IF
			elif 'maximum' in signature[key]:
				logger.trace(
					"Checking if value is less than {!s}. Exclusive max? {!r}".format(
						signature[key]['maximum'], signature[key].get('exclusiveMaximum',False)
					)
				)
				_failed = False
				if signature[key].get('exclusiveMaximum',False):
					_failed = data[key] > signature[key]['maximum']
				else:
					_failed = data[key] >= signature[key]['maximum']
				#END IF/ELSE
				if _failed:
					raise CustomExceptions.HttpDataValidationException(
						"Value must be less than {!s}{!s}".format(
							'' if signature[key].get('exclusiveMaximum',False) else 'or equal to ',
							signature[key]['maximum'],
						)
					)
			#END IF
		#END IF
	#END DEF
	
	@staticmethod
	def _validate_integer(data, signature, key, **kwargs):
		'''
		Special signature keys:
			- minimum
			- maximum
			- exclusiveMinimum
			- exclusiveMaximum
		'''
		logger = LIBRARY_LOGGER.getSubLogger('validate_integer')
		logger.trace("Passing value to '_validate_number'")
		#inserting the key 'format' into the signature so that the '_validate_number' function will use correct data type
		signature[key]['format'] = 'integer'
		data_validation._validate_number(data, signature, key, **kwargs)
	#END DEF
	
	@staticmethod
	def _validate_array(data, signature, key, **kwargs):
		'''
		Special signature keys:
			- collectionFormat
			- minItems
			- maxItems
			- uniqueItems
		'''
		logger = LIBRARY_LOGGER.getSubLogger('validate_array')
		logger.trace("For key '{!s}', got data of type {!s}".format(key, type(data[key])))
		if not isinstance(data[key], types.ListType):
			logger.trace("Not given List Object. Do we have a String and 'collectionFormat'?")
			if isinstance(data[key], types.StringTypes) and 'collectionFormat' in signature[key]:
				logger.trace("We have a String. 'collectionFormat'='{!s}'".format(signature[key]['collectionFormat']))
				data[key] = data[key].split(
					swagGl.VALID_SWAGGER_ARRAY_COLLECTION_FORMATS[signature[key]['collectionFormat']]['delimiter']
				)
			else:
				raise CustomExceptions.HttpDataValidationException(
					data_validation._getTypeErrorMessage(data, key, 'array')
				)
		#END IF

		validationIssues = []
		castData = []
		logger.trace("Validating {!s} items".format(len(data[key])))
		for item in data[key]:
			arrayItem = {}
			arrayItem['items'] = item
			validationIssues.append(
				validate(
					arrayItem,
					signature[key].get('signature',{}),
					hasParent = True,
					doTypeCasting = kwargs.get('doTypeCasting',False),
					isForResponse = kwargs.get('isForResponse',False)
				)
			)
			#Since the dictionary `arrayItem` is what was passed to the `validate` function, we need
			# to extract the now cast value, and append it to the array holding the newly cast data.
			castData.append(arrayItem['items'])
		#END FOR
		data[key] = castData
		if 'uniqueItems' in signature[key] and signature[key]['uniqueItems'] == True:
			logger.trace("Unique items required in Array")
			if len(data[key]) != len(set(data[key])):
				raise CustomExceptions.HttpDataValidationException(
					"Array must have unique elements. Found {!s} elements that were duplicates".format(
						len(data[key]) - len(set(data[key]))
					)
				)
		if 'minItems' in signature[key]:
			logger.trace(
				"Array requires at least {!s} items. Currently have {!s}".format(
					signature[key]['minItems'], len(data[key])
				)
			)
			if len(data[key]) < signature[key]['minItems']:
				raise CustomExceptions.HttpDataValidationException(
					"Array must have at least {!s} elements".format(signature[key]['minItems'])
				)
		if 'maxItems' in signature[key]:
			logger.trace(
				"Array can have at most {!s} items. Currently have {!s}".format(
					signature[key]['maxItems'], len(data[key])
				)
			)
			if len(data[key]) > signature[key]['maxItems']:
				raise CustomExceptions.HttpDataValidationException(
					"Array must have less than {!s} elements".format(signature[key]['maxItems'])
				)
		#END IF
		return validationIssues
	#END DEF
	
	@staticmethod
	def _validate_object(data, signature, key, **kwargs):
		'''
		No special signature keys.
		'''
		logger = LIBRARY_LOGGER.getSubLogger('validate_object')
		logger.trace("For key '{!s}', got data of type {!s}".format(key, type(data[key])))
		if not isinstance(data[key], types.DictionaryType):
			raise CustomExceptions.HttpDataValidationException(
				data_validation._getTypeErrorMessage(data, key, 'object')
			)
		else:
			return validate(
				data[key],
				signature[key].get('signature',{}),
				hasParent = True,
				doTypeCasting = kwargs.get('doTypeCasting',False),
				isForResponse = kwargs.get('isForResponse',False)
			)
	#END DEF
#END CLASS

def validate(data, signature, hasParent=False, doTypeCasting=False, isForResponse=False):
	'''
	@FUNC	Validates that the given data contains all of the necessary keys, with values in the correct format. See the
			comment block below this function definition for an example swagger object.
	@PARAM	data : Dictionary, the data we are checking for the valid parameters.
	@PARAM	signature : HttpDataSignature, a "Python Dictionary" built from a Swagger 2.0 definition.
	@PARAM	hasParent : Boolean, whether this data is in a nested object/array and has a parent
	@PARAM	doTypeCasting : Boolean, whether validation of data should just fail after a check, or whether type
				casting should be attempted.
	@PARAM	isForResponse : Boolean, whether the data should be in a state ready to be converted to a JSON string.
				This option is mostly so that the 'date' format can be converted from a Date object into the
				appropriate String for a JSON response, but be converted from a String into a Date object when
				a request is processed.
	@RETURN Python Dictionary. Will mirror the structure of `signature`, but have information about whether
				the item described by the signature is valid. If invalid, a message will be defined that explains why.
	'''
	logger = LIBRARY_LOGGER.getSubLogger('validate')
	if not isinstance(signature, HttpDataSignature):
		raise Exception("Cannot validate data without an HTTP Data Signature.")
	#This Python Dictionary will, in the end, mirror the structure of `signature`, but instead of the keys mapping
	# to dictionaries of data formats and limit specs, the dictionaries will describe the validity of the key.
	dataValidity = HttpDataValidation()
	#If the signature (or sub-signature) is None or an empty dictionary, then no validation needs to be done. Return None
	if not signature:
		dataValidity.ALL_VALID = True
		return dataValidity
	
	for key in signature:
		logger.trace(
			"Validating data for key {!r} (tc-{!r}, fr-{!r}) || Signature (see details)".format(
				key, doTypeCasting, isForResponse, 
			),
			signature[key]
		)
		dataValidity.addKey(key)
		dataValidity[key]['type'] = signature[key]['type'].lower()
		if key not in data:
			if not signature[key]['required']:
				dataValidity[key]['valid'] = True
				if 'default' in signature[key]:
					data[key] = signature[key]['default']
			#END IF
			continue
		#END IF
		
		dataValidity[key]['found'] = True
		
		#If the request gave us a 'None' and that is allowed, then continue to the next key
		if data[key] is None:
			if signature[key]['nullable']:
				dataValidity[key]['valid'] = True
			else:
				dataValidity[key]['message'] = "Value for '{!s}' cannot be null".format(key)
			continue
		#END IF
		
		#Now we can start the actual tests of data-type-correctness
		keyFormat = signature[key]["type"].lower()
		if keyFormat not in swagGl.VALID_SWAGGER_TYPES['body']:
			#This is a `raise` because the issue is with whoever defined Swagger that built the
			# HttpDataSignature, not with the data being validated
			raise CustomExceptions.HttpDataValidationException("Invalid data signature format '{!s}'".format(keyFormat))
		
		#Finding the validation function, and running the data through it for the current key
		valFunc = getattr(data_validation, "_validate_{!s}".format(keyFormat), None)
		if valFunc is None:
			raise CustomExceptions.HttpDataValidationException(
				"Could not find validation function for data type '{!s}'".format(keyFormat)
			)
		try:
			#If the data's type is an Array or Object, then the found issues will be returned. For all other
			# data validation, nothing is returned.
			dataValidity[key]['items'] = valFunc(
				data, signature, key,
				doTypeCasting = doTypeCasting,
				isForResponse = isForResponse
			)
		except CustomExceptions.HttpDataValidationException, e:
			logger.trace("Found issue with data in {!r}. {!s}".format(key, e))
			dataValidity[key]['message'] = str(e)
			continue
		#END TRY/EXCEPT
		
		#If the spec provides a list of specific values that are allowed, we test that the given value is in that list
		if 'enum' in signature[key] and isinstance(signature[key]['enum'], types.ListType):
			if data[key] not in signature[key]['enum']:
				dataValidity[key]['message'] = (
					"Value '{!s}' is not in the list of allowed options {!r}".format(
						data[key], signature[key]['enum']
					)
				)
				continue
		#END IF
		
		dataValidity[key]['valid'] = True
	#END FOR
	
	#Now that the whole of the signature has been processed, let's see if the whole of the data is valid.
	def isValidationAllValid(httpdv):
		for key in httpdv:
			if not httpdv[key]['valid']:
				return False
			if httpdv[key]['items'] is not None:
				if isinstance(httpdv[key]['items'], types.ListType):
					nestedIsValid = all([isValidationAllValid(v) for v in httpdv[key]['items']])
				else:
					nestedIsValid = isValidationAllValid(httpdv[key]['items'])
				if not nestedIsValid:
					return False
		#END FOR
		return True
	#END DEF
	
	dataValidity.ALL_VALID = isValidationAllValid(dataValidity)
	#The `hasParent` parameter will only be set to True when `data_validation._validate_array`
	# or `data_validation._validate_object` recursively called this `validate` function. So by knowing that
	# `hasParent` is False, we know that we are back at the first invocation of the function
	if not hasParent:
		logger.debug("Final Validity: {!s}".format(dataValidity.ALL_VALID), dataValidity)
	
	return dataValidity
#END DEF

def simpleValidate(value, typeString):
	'''
	@FUNC	Using the `validate` function, does a simple validation that the given value is of the given Swagger type.
	@PARAM	value : Object
	@PARAM	typeString : String, a Swagger Value Type
	@RETURN	Object, the value given, but typecast if it was done so while validating.
			Will return None if the given value did not pass the validation test.
	'''
	valFunc = getattr(data_validation, "_validate_{!s}".format(typeString), None)
	if valFunc is None:
		raise Exception("No data validation function of type '{!s}'".format(typeString))
	try:
		data = {'aValue': value}
		valFunc(
			data,
			{'aValue':{}}, #signature
			'aValue', #key
			doTypeCasting=True
		)
		return data['aValue']
	except CustomExceptions.HttpDataValidationException, e:
		return None
	#END TRY/EXCEPT
#END DEF



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# "HTTP Method" AND "Endpoint Logic" CLASSES
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class HttpMethod(object):
	'''
	@CLASS	A Generic HTTP Method Class that should be inheritted by the classes defined in the `BaseEndpoint` class.
			When defining an `HttpMethod` class in the `BaseEndpoint` class, the name of the class should be
			the HTTP Method (eg. GET, POST, PATCH, etc.).
			
			When inheritting this class, your implementation should define a class variable and a static function
			matching the values in the static variables, `ENDPOINT_LOGIC_FUNCTION` and `ENDPOINT_SWAGGER_VARIABLE`.
			The logic function should expect two parameters, a WebDevRequest object and a Logger object.
			
			When creating the actual endpoint, be sure to create the variable SWAGGER with a Swagger configuration,
			following the specification outlined here.
			# https://swagger.io/docs/specification/2-0/basic-structure/
			
			For an example SWAGGER dictionary and logic function, please review the '__README__' script resource
	'''
#END CLASS

class Endpoint(object):
	'''
	@CLASS	This is a helper class that contains the logic for processing an HTTP Request using the given Script Module.
			This class, once initialized and the `execute` function is called, will:
			 1. Validate that the given Script Module contains an `HttpMethod` class
			 2. Confirm the `HttpMethod` class has all of the necessary attributes
			 3. Confirm the incoming HTTP Request is valid for the endpoint
			 4. Confirm the request is authenticated (if necessary)
			 5. Execute the logic found in the `HttpMethod` class
			 6. Confirm the outgoing data is valid
	@ATTR	wdr : WebDevRequest Object
	@ATTR	swagStc : Reference to a Script Module for the "Swagger Statics"
	@ATTR	swagDf : Reference to a Script Module for the "Swagger Definitions"
	@ATTR	scriptModule : Reference to a Script Module
	@ATTR	httpMethodClass : Reference to `HttpMethod` Class found in the given Script Module
	@ATTR	logger : Gateway Logger object, based on the WebDev Request's URI Path
	@ATTR	response : Object, the response to return to the callee
	@ATTR	completedSuccessfully : Boolean
	'''
	
	def __init__(self, wdr, fullScriptPathString, scriptModule, swagStatics, swagDefinitions, callingLogger = None):
		'''
		@FUNC	Initializes the BaseEndpoint object
		@PARAM	wdr : WebDev Request Dictionary, from the WebDev Resource
		@PARAM	fullScriptPathString : String, the full path to the Script resource that the given request maps to
		@PARAM	scriptModule : Reference to a Script Module that should contain some 'HttpMethod' classes
		@PARAM	swagStatics : Reference to a Script Module for the "Swagger Statics"
		@PARAM	swagDefinitions : Reference to a Script Module for the "Swagger Definitions"
		@PARAM	callingLogger : Logger object, where to put a message of the instance of this class being
					initialized, and with what logger name
		'''
		if not isinstance(wdr, WebDevRequest):
			raise CustomExceptions.EndpointException("Parameter 1 must be a WebDevRequest object.")
		self.wdr = wdr
		self.swagStc = swagStatics
		self.swagDf = swagDefinitions
		#Validating that the WebDevRequest has performed all of the necessary modifications/cleanup of the
		# given data in the HTTP Request
		requiredAugs = ['headers', 'httpmethod', 'uri']
		if not all([self.wdr.requestAugmentations[aug] for aug in requiredAugs]):
			raise CustomExceptions.EndpointException(
					"The given WebDevRequest object must have the following Request Extensions configured: "+
					"{!r}".format(requiredAugs)
				)
		#END IF
		self.logger = self.__getRequestLogger(fullScriptPathString)
		if callingLogger is not None:
			callingLogger.debug(
				"BaseEndpoint initialization validated given WebDevRequest object. "+
				"Further logging available at {!s}".format(self.logger.name)
			)
		#END IF
		self.response = None
		self.scriptModule = scriptModule
	#END DEF
	
	def __getRequestLogger(self, path):
		'''
		@FUNC	Gets a system Logger for the WebDev endpoint called, so that we can easily find the appropriate
				logger in the gateway logs.
		@RETURN	Logger object, which the user can use to log information to the Gateway Logs
		'''
		reformattedPath = path.replace('.','_')
		request_logger = LIBRARY_LOGGER.getSubLogger(
			"Endpoint.{!s}__{!s}".format(self.wdr.swag['http-method'], reformattedPath)
		)
		#Making an initial TRACE log, just so that we can easily see (when testing) that the correct WebDev
		# resource is being called.
		request_logger.trace("Starting logger for '{!s}'".format(reformattedPath))
		return request_logger
	#END DEF
	
	def __validateHttpMethodClass(self, httpMethodClass):
		'''
		@FUNC	Using the WedDevRequest object given during initialization, this will validate the given `HttpMethod`
				class that maps to the HTTP Request's Method.
		@PARAM	httpMethodClass
		@PARAM	swagStc
		@RETURN	N/A
		@RAISES	EndpointInitializationException, if the given ScriptModule is invalid
		@ADDS	self.__httpMethodClass : Class, the HTTP Method Class (with the correct `SWAGGER` and `logic` properties)
				self.__consuming : String, the "Content Type" given
		'''
		#Determining if there is an HTTP Method class defined that has the name of the HTTP Request's Method.
		self.logger.trace(
			"Validating given parameter 'httpMethodClass' is a reference to a correctly configured 'HttpMethod' Class."
		)
		self.__httpMethodClass = httpMethodClass
		
		if not inspect.isclass(self.__httpMethodClass):
			raise CustomExceptions.EndpointInitializationException(
				"Given class '{!r}' was not a class object".format(self.__httpMethodClass)
			)
		#END IF
		if not (
			hasattr(self.__httpMethodClass, self.swagStc.ENDPOINT_LOGIC_FUNCTION) and 
			inspect.isfunction(getattr(self.__httpMethodClass, self.swagStc.ENDPOINT_LOGIC_FUNCTION, None))
		):
			raise CustomExceptions.EndpointInitializationException(
				"Given HTTP Method Class does not have the required Function named '{!s}'".format(
					self.swagStc.ENDPOINT_LOGIC_FUNCTION
				)
			)
		#END IF
		if not (
			hasattr(self.__httpMethodClass, self.swagStc.ENDPOINT_SWAGGER_VARIABLE) and 
			isinstance(getattr(self.__httpMethodClass, self.swagStc.ENDPOINT_SWAGGER_VARIABLE, None), types.DictionaryType)
		):
			raise CustomExceptions.EndpointInitializationException(
				"Given HTTP Method Class does not have the required Dictionary named '{!s}'".format(
					self.swagStc.ENDPOINT_SWAGGER_VARIABLE
				)
			)
		#END IF
		
		self.logger.trace(
			"Given reference to a Class has a Function named '{!s}' and Dictionary named '{!s}'".format(
				self.swagStc.ENDPOINT_LOGIC_FUNCTION, self.swagStc.ENDPOINT_SWAGGER_VARIABLE
			)
		)
		
		if self.wdr.swag['http-method'] == 'GET':
			self.logger.trace("Augmenting WebDevRequest object, parsing URL Query Params")
			self.wdr.augmentRequestContent(contentType = 'application/x-www-form-urlencoded')
		else:
			# # # # # #
			# TODO:
			# * The system should be configurable by the user to allow endpoint to accept request that do NOT define a
			#   'Content-Type' header, and assume a specific type of content to be present
			# * If no actual "content" is given to the endpoint, the user should also have the option to set whether
			#   empty content is allowed or not.
			if 'content-type' not in self.wdr.swag['headers-lc']:
				raise CustomExceptions.EndpointInitializationException(
					"Incoming Request did not define a 'Content-Type' header"
				)
			# # # # # #
			givenType = self.wdr.swag['headers-lc']['content-type']
			self.logger.trace("Given content type. '{!s}'".format(givenType))
			#The "Content-Type" header can be provided with extra information, and is in the form
			# "[CONTENT_TYPE]; [EXTRA_INFO]". So, we split on the semicolon character and get the first element
			self.__consuming = givenType.split(';')[0].lower()
			self.logger.trace("The true given content type. '{!s}'".format(self.__consuming))
			if self.__consuming not in swagGl.VALID_CONTENT_TYPES.keys():
				raise CustomExceptions.EndpointInitializationException(
					"The Content-Type '{!s}' is not supported.".format(self.__consuming)
				)
			#Once we know that a 'Content-Type' was given, we want to make sure that the HTTP Method supports
			# that Content-Type. We need to check the dictionary `swagGl.VALID_METHODS` for that information.
			# The keys in the Dictionary are HTTP Methods, and if the key for the HTTP Method in the Dictionary
			# maps to `None`, then we allow ALL types of content.
			if (swagGl.VALID_METHODS[ self.wdr.swag['http-method'] ] is not None and
				self.__consuming not in swagGl.VALID_METHODS[ self.wdr.swag['http-method'] ]
			):
				raise CustomExceptions.EndpointInitializationException(
					"The Content-Type '{!s}' is not allowed for the HTTP Method {!s}.".format(
						self.__consuming, self.wdr.swag['http-method']
					)
				)
			#Each endpoint can also define what specific format the incoming data needs to be in.
			if (self.__consuming not in 
				getattr(self.__httpMethodClass, self.swagStc.ENDPOINT_SWAGGER_VARIABLE, {}).get('consumes',[])
			):
				raise CustomExceptions.EndpointInitializationException(
					"The Content-Type '{!s}' is not supported by this endpoint.".format(self.__consuming)
				)
			#Un-comment the two lines below if you aren't worried about un-obscured data showing the gateway logs
			##currentBody = self.wdr.request.get('data',None)
			##self.logger.trace("request['data'] = {!s}, repr = {!r}".format(type(currentBody), currentBody))
			self.logger.trace("Augmenting WebDevRequest object, parsing Request as '{!s}'".format(self.__consuming))
			self.wdr.augmentRequestContent(self.__consuming)
		#END IF/ELSE
		
		#Verifying that the Body or URL Params were parsed and can now be referenced in the `swag` Python Dictionary.
		if not self.wdr.requestAugmentations['content']:
			raise CustomExceptions.EndpointInitializationException(
					"Could not successfully augment/clean-up the content in the WebDevRequest object."
				)
		#END IF
		
		return
	#END DEF
	
	def __authenticateRequest(self):
		'''
		@FUNC	Uses the HTTP Method Class's SWAGGER to authenticate that the incoming request is allowed to
				access this endpoint.
		@RETURN	Boolean, whether the incoming HTTP Request is authorized.
		'''
		#Looping through the provided authentication methods that the endpoint wants to use.
		if (self.swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX+'auth' not in self.__endpointSwaggerDef or
			not isinstance(
				self.__endpointSwaggerDef.get(self.swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX+'auth',None),
				types.ListType
			)
		):
			raise CustomExceptions.IgnitionSwaggerPropMissingException(
				"The HTTP Method Class's Swagger Definition must contain a PyList in the custom 'auth' key."
			)
		if (len(self.__endpointSwaggerDef[self.swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX+'auth']) == 0 or
			any([
				not isinstance(authMethod, types.DictionaryType)
				for authMethod in self.__endpointSwaggerDef[self.swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX+'auth']
			])
		):
			raise CustomExceptions.IgnitionSwaggerPropInvalidException(
				"The HTTP Method Class's Swagger Definition dictionary's custom key 'auth' must "+
				"be a non-empty PyList of Python Dictionaries."
			)
		#END IFs
		
		# # # # # #
		#TODO:
		# Figure out how to create a relationship between the information in 'security' in the Swagger dictionary and the
		#  functions needed to verify incoming requests are allowed (ie. the content in PREFIX+'auth')
		# # # # # #
		
		authSuccess = False
		authErrorMessages = []
		self.wdr.swag['auth'] = None
		#We will now loop through all of the specified authentication methods. If any of
		# the methods succeeds, we can break from the loop and continue on toward executing the logic
		for authMethod in self.__endpointSwaggerDef[self.swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX+'auth']:
			#Calling the authentication function with all of the parameters
			if not isinstance(authMethod.get('method',None), types.FunctionType):
				raise CustomExceptions.IgnitionSwaggerPropInvalidException(
					"The 'method' attribute of the dictionaries in the Swagger Definition's "+
					"custom 'auth' key must be functions."
				)
			#Be aware that the '__module__' property used below is not the ENTIRE qualified path of the module
			# that houses the function referenced, but just it's parent module.
			# So while the full path might be 'mypackage.subpackage.mymodule.myfunction', this logger message
			# will only show 'mymodule.myfunction'.
			funcQualName = "{!s}.{!s}".format(authMethod['method'].__module__, authMethod['method'].__name__)
			self.logger.trace("Attempting authentication using function '{!s}'".format(funcQualName))
			
			#Creating a dictionary with the arguments for the authentication function. The Dictionary describing the
			# authentication function can also define some "extra arguments", and we need to include those.
			authKWArgs = {'wdr':self.wdr}
			if isinstance(authMethod.get('extraArgs',None), types.DictionaryType) and len(authMethod['extraArgs']) > 0:
				self.logger.trace(
					"Adding extra authentication args {!r} to execution of '{!s}'".format(
						authMethod['extraArgs'].keys(), funcQualName
					)
				)
				for argName in authMethod['extraArgs']:
					authKWArgs[argName] = authMethod['extraArgs'][argName]
			#END IF

			#Note that this line is not in a try/except. If the developer did not implement the
			# function to accept the proper parameters, then we want the exception to occur.
			#
			authResponse = authMethod['method'](**authKWArgs)
			#
			#If the authentication succeeded, break the loop. Otherwise, record the error message received and continue.
			# There may be MULTIPLE authentication methods that are allowed.
			if authResponse.get('success', False):
				self.logger.trace("Authentication '{!s}' succeeded.".format(authMethod['method'].__name__))
				authSuccess = True
				self.wdr.swag['auth'] = authResponse
				break
			else:
				self.logger.trace("Authentication '{!s}' failed.".format(authMethod['method'].__name__))
				#If the authentication message does not provide a message in the key 'message' for why the authentication
				# failed, we will make sure a default message is generated.
				authErrorMessages.append( authResponse.get('message', "Failure to pass '{!s}'".format(funcQualName)) )
		#END FOR
		if not authSuccess:
			fullAuthErrorMessage = " | ".join( list(set(authErrorMessages)) )
			self.response = swagRsp.json(status='failure', success=False, message=fullAuthErrorMessage)
			self.logger.warn("FAILED TO AUTHENTICATE! (see details for list of issues)", list(set(authErrorMessages)))
			return False
		#END IF
		return True
	#END DEF
	
	def __validateRequest(self):
		'''
		@FUNC	If the SWAGGER defines the endpoint as requiring validating of the incoming data, passes
				the appropriate date (URL Queries or HTTP Body) through the validation function.
		@RETURN	Boolean, whether the incoming HTTP Request is valid.
		'''
		if not self.__endpointSwaggerDef.get(self.swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX+'validateRequest',True):
			self.logger.trace(
				"No request validation. Will validate response? {!r}".format(
					self.__endpointSwaggerDef.get(self.swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX+'validateResponse',True)
				)
			)
		else:
			#Validating that any necessary headers were given.
			sig = self.__dataSignatures['incoming']['header']
			if len(sig) > 0:
				dataLocation = swagGl.VALID_SWAGGER_IN['header']
				data = self.wdr.swag[dataLocation]
				self.logger.trace("Validating incoming data in \"self.wdr.swag['{!s}']\".".format(dataLocation))
				_requestValidation = validate(data, sig, doTypeCasting = True, isForResponse = False)
				#Regardless of whether the request succeeded or not, we log what was received
				self.wdr.logIncomingData(dataLocation, data, sig)
				if not _requestValidation.ALL_VALID:
					self.logger.debug("Request data failed to validate. {!s}".format(_requestValidation))
					self.response = swagRsp.json(
						status='failure', success=False,
						message="Error in Headers. {!s}".format(_requestValidation)
					)
					return False
				#END IF
				#Since we now know that the headers are valid, we need to make sure that the lower-case headers
				# also have the cleaned-up (and potentially type-casted) values
				self.wdr.swag['headers-lc'] = {k.lower(): self.wdr.swag['headers'][k] for k in self.wdr.swag['headers']}
			#END IF
			
			#There is not need to validate Path Params, since we will already have Path Params parsed and validated
			# depending on whether the Script Resource found had such requirements and the incoming HTTP Request was
			# to a matching URI.
			#
			# NOTE! In this implementation of Swagger, it is assumed that every Path Param defined by the path to
			# the Script Module is REQUIRED, and that we cannot determine what the correct order is for non-required
			# Path Params.
			# At least, I haven't yet found a clean and intuitive way to do it.
			# For now, a Resource can be found such that the path (ie. the Script Package names) defined what parts are
			# Path Params. Any remaining content in the HTTP Request's Path is just extra fluff that the endpoint can
			# deal with, if it wants to.
			
			#Validating the actual incoming data. We first need to use the "Content-Type" header to determine what
			# key to look for in the Endpoint's Swagger Definition for the signature.
			if self.wdr.swag['http-method'] == 'GET':
				dataInKey = 'query'
			else:
				dataInKey = swagGl.VALID_CONTENT_TYPES_TO_SWAGGER_IN.get(self.__consuming, 'UNKNOWN')
			#END IF/ELSE
			self.logger.trace("Determined data key to be '{!s}'".format(dataInKey))
			sig = self.__dataSignatures['incoming'][dataInKey]
			if len(sig) > 0:
				dataLocation = swagGl.VALID_SWAGGER_IN[dataInKey]
				data = self.wdr.swag[dataLocation]
				self.logger.trace("Validating incoming data in \"self.wdr.swag['{!s}']\".".format(dataLocation))
				self.logger.trace("all swag", self.wdr.swag)
				_requestValidation = validate(
					data, sig,
					doTypeCasting = (False if dataLocation=='body' else True),
					isForResponse = False
				)
				#Regardless of whether the request succeeded or not, we log what was received
				self.logger.trace("Data was validated. Logging to Gateway Console Log...")
				self.wdr.logIncomingData(dataLocation, data, sig)
				if not _requestValidation.ALL_VALID:
					self.logger.debug("Request data failed to validate. {!s}".format(_requestValidation))
					self.response = swagRsp.json(
						status='failure', success=False,
						message="Error in {!s} area of request. {!s}".format(dataInKey, _requestValidation)
					)
					return False
				#END IF
			#END IF
			
			self.logger.debug("SUCCESSFULLY VALIDATED THE REQUEST!")
		#END IF/ELSE
		return True
	#END DEF
	
	def __executeLogic(self):
		'''
		@FUNC	Executes the actual logic of the endpoint, as defined by the HTTP Method Class.
		@RETURN	Boolean, whether the function was able to execute successfully.
		'''
		self.logger.trace("Finally, FINALLY executing the HttpMethod class's \"logic\" function.")
		#The "logic" function should ALWAYS receive the following parameters:
		#  - `wdr` : WebDevRequest Object
		#  - `logger` : Gateway Logger Object
		self.response = getattr(self.__httpMethodClass, self.swagStc.ENDPOINT_LOGIC_FUNCTION)(self.wdr, self.logger)
		#Expected return:
		#  - Python Dictionary, a WebDev response that a WebDev Resource can return. The valid keys are:
		#	 - 'html' - HTML source as a String.
		#	 - 'json' - A Python Dictionary which will be encoded as 'application/json' data.
		#	 - 'file' - A file path to send as the response.
		#	 - 'bytes' - A byte[] to send back. The mime type will be 'application/octet-stream' if not specified.
		#	 - 'response' - Any type of plain text response.
		#	 - 'contentType' - The mime type. Need only if ambiguous.
		#NOTE!
		# The execution of this function could, potentially, raise an exception. The exception will be caught and
		# logged in the `callWebDevLogic` function.
		self.logger.trace("Logic has been executed!")
		return True
	#END DEF
	
	def __validateResponse(self):
		'''
		@FUNC	If the SWAGGER defines the response as needing validation, passing the appropriate HttpDataSignature
				and the data to be validated to `validate`. This function will throw an Exception if the outgoing
				data is invalid.
		@RETURN	Boolean, when the response is valid.
		@RAISES	Exception if problem finding correct JSON response signature for HTTP Status Code response
		@RAISES	Exception if JSON response is not in correct format
		'''
		if (self.response is not None and
			self.__endpointSwaggerDef.get(self.swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX+'validateResponse',True) and
			'json' in self.response
		):
			self.logger.trace("Potentially validating the JSON response.")
			responseHTTPCode = str(self.wdr.request['servletResponse'].getStatus())
			if (responseHTTPCode not in self.__dataSignatures['outgoing'] or
				(	responseHTTPCode in ('200', '201', '202', '203') and
					self.response['json'].get('success',False) == False )
			):
				responseHTTPCode = 'default'
			self.logger.trace(
				"Validating response using definition for the '{!s}' status in the SWAGGER.".format(responseHTTPCode)
			)
			if responseHTTPCode not in self.__dataSignatures['outgoing']:
				raise CustomExceptions.EndpointExecutionException(	
						"Cannot validate response for status '{!s}'".format(responseHTTPCode)
					)
			else:
				_responseValidation = validate(
						self.response['json'],
						self.__dataSignatures['outgoing'][responseHTTPCode],
						doTypeCasting = True,
						isForResponse = True
					)
				if not _responseValidation.ALL_VALID:
					raise CustomExceptions.EndpointExecutionException(
							"Response Validation ERROR \"{!s}\"".format(_responseValidation)
						)
			#END IF
			self.logger.debug("SUCCESSFULLY VALIDATED THE RESPONSE!")
		else:
			self.logger.trace(
					"No response validation. "+
					("Response is JSON. " if 'json' in (self.response or {}) else "Response is not JSON. ")+
					("Special 'validateResponse' key = {!r}".format(
							self.__endpointSwaggerDef.get(self.swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX+'validateResponse',True)
						)
					)
				)
		#END IF/ELSE
		return True
	#END DEF
	
	def execute(self):
		'''
		@FUNC	Using self's WebDevRequest object, attempts to execute the ACTUAL endpoint logic defined
				for the HTTP Method called.
				Special Swagger keys (which must have the appropriate prefix) that are used:
					- includeHeaders
					- auth
					- validateRequest
					- validateResponse
		
		@USES	self.response : Dictionary
		@USES	self.scriptModule : Reference to Script Module object
		@USES	self.wdr : WebDevRequest object
		@USES	self.__httpMethodClass : reference to Class object
		
		@ADDS	self.completedSuccessfully : Boolean
		@ADDS	self.__endpointSwaggerDef : Dictionary, the Swagger Definition for the endpoint being called.
		@ADDS	self.__dataSignatures : Dictionary, the `HttpDataSignature` objects used by the private functions
					'__validateRequest' and '__validateResponse'.
		
		@RETURN	Dictionary, the response to be returned to the original WebDev Request.
		'''
		if self.wdr.swag['http-method'] not in self.scriptModule.__dict__:
			return swagRsp.httpStatus(self.wdr.request, "Not Implemented")
		
		self.__validateHttpMethodClass( self.scriptModule.__dict__[self.wdr.swag['http-method']] )
		#Saving this for later, for easier reference by later blocks and other functions
		self.__endpointSwaggerDef = getattr(self.__httpMethodClass, self.swagStc.ENDPOINT_SWAGGER_VARIABLE)
		
		self.logger.trace("Generating incoming and outgoing data signatures based on found Swagger.")
		self.logger.trace("Possible incoming data locations to check: {!r}".format(swagGl.VALID_SWAGGER_IN.keys()))
		self.logger.trace(
			"Possible outgoing signature to check: {!r}".format(self.__endpointSwaggerDef.get('responses',{}).keys())
		)
		self.__dataSignatures = {
			'incoming': {
				dataLocation : getDataSignatureFromSwagger(
						self.__endpointSwaggerDef,
						'incoming', dataLocation,
						self.swagStc, self.swagDf
					)
					for dataLocation in
					swagGl.VALID_SWAGGER_IN.keys()

			},
			'outgoing': {
				httpStatusCode : getDataSignatureFromSwagger(
						self.__endpointSwaggerDef,
						'outgoing', httpStatusCode,
						self.swagStc, self.swagDf
					)
					for httpStatusCode in
					self.__endpointSwaggerDef.get('responses',{}).keys()
			}
		}
		self.logger.trace("Incoming and Outgoing data signatures generated (see details)", self.__dataSignatures)
		
		# CUSTOM RESPONSE HEADERS
		#This SWAGGER config option was added because Authentication happens here, in `callWebDevLogic`, before the
		# methodClass's `logic` function has a chance to run. There are cases, like with the GMail integration, where
		# we want to include headers in the response regardless of whether the Authentication validation succeeded or not.
		#And so, the definer can use a Python Dictionary in the key 'custom prefix'+'includeHeaders' to have some headers
		# included by default. The keys in the dictionary should map to Strings.
		if (self.swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX+'includeHeaders' in self.__endpointSwaggerDef and
			isinstance(
				self.__endpointSwaggerDef.get(self.swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX+'includeHeaders',None),
				types.DictionaryType
			)
		):
			self.logger.trace(
				"Including headers: {!r}".format(
					self.__endpointSwaggerDef[self.swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX+'includeHeaders'].keys()
				)
			)
			for key in self.__endpointSwaggerDef[self.swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX+'includeHeaders']:
				self.wdr.request['servletResponse'].setHeader(
					key, str(self.__endpointSwaggerDef[self.swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX+'includeHeaders'][key])
				)
		#END IF
		
		self.completedSuccessfully = False
		#In the conditional block below, the incoming request will be validated, logic executed, and the response
		# validated. The attribute `response` will have the final value to return to the callee
		if (self.response is None and
			self.__authenticateRequest() and
			self.__validateRequest() and
			self.__executeLogic() and
			self.__validateResponse()
		):
			self.completedSuccessfully = True
		#END IF
		return self.response
	#END DEF
#END CLASS



def findBestScriptResourceFromPath(possiblePath, swagStc):
	'''
	@FUNC	Attempts to use the List of Strings to find a Script Resource
	@PARAM	possiblePath : List of Strings
	@PARAM	swagStc : Reference to a Script Module for the "Swagger Statics"
	@RETURN	Dictionary, containing data about the Script Modules found that matched the path given.
			Dictionary will contain the following keys:
			 - fullName : String
			 - scriptModule : Script Module Object
			 - pathParams : Dictionary, mapping a Path Parameter to the value given
			 - remainingPath : List of Strings
			None will be returned if no Script Module is found
	'''
	logger = LIBRARY_LOGGER.getSubLogger('findBestScriptResourceFromPath')
	logger.trace("Given Path = {!r}".format(possiblePath))
	if not all([isinstance(_,types.StringTypes) for _ in possiblePath]):
		raise Exception("Was not given a List of Strings.")
	
	cleanPath = filter(lambda v:v.strip() != '', possiblePath)
	logger.debug("Cleaned Path = {!r}".format(cleanPath))
	
	#It is assumed that the first item in the list is the "base path", which will map to a Script Package
	# in this project. Therefore, we can always start looking in the package for the correct endpoint logic
	endpointBase = sys.modules.get(cleanPath[0], None)
	if endpointBase is None:
		raise Exception("Missing Base for API. Please consult README")
	
	def findPossibleScriptPackages(thisPackage, remainingPath, foundPathParams={}, fullParentName=None):
		'''
		@FUNC	Recursive function for finding all possible Script Packages maybe with endpoint logic
		@PARAM	thisPackage : Script Package object
		@PARAM	remainingPath : List of Strings
		@PARAM	foundPathParams : Dictionary, containing the param->value mappings already found for the original path
		@PARAM	fullParentName : String/None
		@RETURN	List of Dictionaries.
					The Dictionaries will contain the following keys:
					 - fullName : String (eg. 'v1.petstore.pet.findByStatus')
					 - scriptModule : Script Module object
					 - pathParams : Dictionary (KEY=ParamName, VALUE=Object)
					 - remainingPath : List of Strings
		'''
		possiblePackages = []
		fullName = (fullParentName+'.' if fullParentName is not None else '') + thisPackage.__name__
		logger.trace("{!s} - {!r}".format(fullName, thisPackage.__dict__))
		
		#If this Script Package contains a resource that is a "ScriptPackge", and it has the name defined
		# in our static key 'ENDPOINT_LOGIC_RESOURCE_NAME', then this possible is the Endpoint Logic we
		# are looking for.
		if swagStc.ENDPOINT_LOGIC_RESOURCE_NAME in thisPackage.__dict__:
			logger.debug("Found possible Endpoint Logic at '{!s}'".format(fullName))
			possiblePackages.append({
				'fullName': fullName,
				'scriptModule': thisPackage.__dict__[swagStc.ENDPOINT_LOGIC_RESOURCE_NAME],
				'pathParams': copy.deepcopy(foundPathParams),
				'remainingPath': remainingPath,
			})
		else:
			logger.debug("Package '{!s}' does not have Endpoint Logic".format(fullName))
		#END IF/ELSE
		
		#If we didn't find a possible Script Resource named after 'swagStc.ENDPOINT_LOGIC_RESOURCE_NAME' and there are
		# no value remaining on the path, then we can assume that we won't find anything else and can return
		if len(remainingPath) == 0:
			return possiblePackages
		
		#Now we need to check to see if we can find a sub-package with the exact name of the next part of the
		# URL's path. Essentially, do we have to go "deeper" into the API resource structure?
		newRemainingPath = remainingPath[1:]
		nextPart = remainingPath[0]
		if (nextPart in thisPackage.__dict__ and isinstance(thisPackage.__dict__[nextPart], ScriptPackage)):
			logger.debug(
				"Looking deeper. Potential Endpoint Logic to be found in '{!s}' under '{!s}'".format(nextPart, fullName)
			)
			possiblePackages = (
				possiblePackages +
				findPossibleScriptPackages(
					thisPackage = thisPackage.__dict__[nextPart],
					remainingPath = newRemainingPath,
					foundPathParams = copy.deepcopy(foundPathParams),
					fullParentName = fullName,
				)
			)
		else:
			logger.debug("Did not find sub-package with name '{!s}'".format(nextPart))
		#END IF/ELSE
		
		#Since part of the URL could be parameters, we need to also check if this package has sub-packages
		# that are placeholders for Path Parameters.
		for allowPathParamType in swagGl.VALID_SWAGGER_TYPES['path']:
			packageNameRegex = '^{}{}\-(.*)'.format(re.escape(swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX), allowPathParamType)
			logger.trace(
				"Looking for sub-packages in '{!s}' with name matching regex '{!s}'".format(fullName, packageNameRegex)
			)
			for subPackName in thisPackage.__dict__.keys():
				#If the regex does not find a match, then we can safely skip
				reMatchObj = re.match(packageNameRegex, subPackName)
				if reMatchObj is None:
					continue
				
				logger.debug(
					"Potential Endpoint Logic to be found in '{!s}' under '{!s}',".format(subPackName, fullName)+
					" if remaining path '{!s}' is valid.".format(nextPart)
				)
				validatedValue = simpleValidate(nextPart, allowPathParamType)
				if validatedValue is None:
					logger.trace(
						"Path Part '{!s}' did not pass validation requirements for a value of type {!s}.".format(
							nextPart, allowPathParamType
						)
					)
					continue
				#END IF
				#If we made it past the IF, then we know that the data in the URL passed the basic validation
				logger.debug(
					"Path Part '{!s}' passed validation for possible sub-package '{!s}'".format(nextPart, subPackName)
				)
				
				#The regex above encapsulated all of the remaining Package Name into a group, which will become our
				# Path Param's name, mapping to the value that has been validated.
				foundPathParams[reMatchObj.group(1)] = validatedValue
				possiblePackages = (
					possiblePackages +
					findPossibleScriptPackages(
						thisPackage = thisPackage.__dict__[subPackName],
						remainingPath = newRemainingPath,
						#We are making a copy, so that the original dictionary given is not appended to
						# by later recursive calls.
						foundPathParams = copy.deepcopy(foundPathParams),
						fullParentName = fullName,
					)
				)
			#END FOR
		#END FOR
		return possiblePackages
	#END DEF
	foundPackages = findPossibleScriptPackages(endpointBase, cleanPath[1:])
	logger.debug(
		"Possible Endpoint Logic found. {!s} packages found (see log details)".format(len(foundPackages)),
		foundPackages
	)
	
	if len(foundPackages) == 0:
		logger.trace("No packages found. Returning None...")
		return None
	elif len(foundPackages) == 1:
		logger.trace("Found exactly one package. Returning...")
		return foundPackages[-1]
	else:
		logger.trace("Found mor than one package. Determining best match...")
		#To find the best match, we are going to start by finding the packages that have the shortest
		# number of "remaining path" items left. We are going to process the items in reverse order, since
		# the end of the list of Script Packages should have the shortest remaining path.
		minRemainingPath = -1
		for pckg in foundPackages:
			if minRemainingPath == -1 or len(pckg['remainingPath']) < minRemainingPath:
				minRemainingPath = len(pckg['remainingPath'])
		#END FOR
		logger.trace("Best matches will have a remaining path of {!s} elements".format(minRemainingPath))
		if minRemainingPath == -1:
			raise CustomExceptions.EndpointException(
				"Unable to determine Script Packages with shortest remaining path."
			)
		#Now we see how many packages had that smallest remaining path
		packagesWithShortestRemaining = []
		for pckg in foundPackages:
			if len(pckg['remainingPath']) == minRemainingPath:
				packagesWithShortestRemaining.append(pckg)
		#END FOR
		logger.debug(
			"Filtered found Packages to {!s} elements (see log details)".format(
				len(packagesWithShortestRemaining)
			),
			packagesWithShortestRemaining
		)
		if len(packagesWithShortestRemaining) == 1:
			return packagesWithShortestRemaining[-1]
		
		#If we got to here, it means that we have multiple Script Packages that matched. We are going to first
		# see if we have a Script Package that matches exactly. If not, then we see if an endpoint has an
		# integer variable. And finally, if all else fails, we select the endpoint with a string variable.
		#If during any of these tests we find multiple matching, we raise an Exception.
		logger.trace("Sorting packages to those that had the final part of that path as a variable and those that didn't.")
		packagesWithVariable = []
		packagesWithoutVariable = []
		for pckg in packagesWithShortestRemaining:
			lastPart = pckg['fullName'].split('.')[-1]
			if swagStc.IGNITION_SWAGGER_CUSTOM_PREFIX in lastPart:
				packagesWithVariable.append(pckg)
			else:
				packagesWithoutVariable.append(pckg)
		#END FOR
		
		if len(packagesWithoutVariable) > 0:
			logger.trace(
				"There were {!s} packages with a final path part as a static value.".format(len(packagesWithoutVariable))
			)
			if len(packagesWithoutVariable) > 1:
				raise CustomExceptions.EndpointException(
					"Found multiple Packages with a static path end. Cannot chose which one to use."
				)
			return packagesWithoutVariable[-1]
		#END IF
		if len(packagesWithVariable) == 0:
			raise CustomExceptions.EndpointException(
				"Somehow we have no packages with or without a variable."
			)
		#END IF
		logger.trace("No packages with a static final path part. Choosing best with variable...")
		variableTypeSearchOrder = ['integer','string']
		for vt in variableTypeSearchOrder:
			packagesWithMatchingVariableType = []
			for pckg in packagesWithVariable:
				if vt in pckg['fullName'].split('.')[-1]:
					packagesWithMatchingVariableType.append(pckg)
			#END FOR
			if len(packagesWithMatchingVariableType) == 0:
				continue
			elif len(packagesWithMatchingVariableType) == 1:
				return packagesWithMatchingVariableType[-1]
			else:
				raise CustomExceptions.EndpointException(
					"Found multiple Packages with a variable path end of type '{!s}'.".format(vt) +
					"Cannot chose which one to use."
				)
		#END FOR
		return None
	#END IF/ELIF/ELSE
	raise CustomExceptions.EndpointException(
		"Did not find any package to return. This should not have happened."
	)
#END DEF

def processRequest(request, session):
	'''
	@FUNC	After doing some reconfiguring and cleanup of the request object given by the WebDev Module to a
			WebDev Resource, finds the appropriate Project Script Resource with the Endpoint class defined, and
			asks the HttpMethod class to execute its logic for the given request.and calls it with the given data.
	@PARAM	request : WebDev Request Python Dictionary
	@PARAM	session : WebDev Session Python Dictionary
	@RETURN	Python Dictionary, a WebDev Response that a WebDev Resource can return. The valid keys are:
			 - 'html' - HTML source as a String.
			 - 'json' - A Python Dictionary which will be encoded as 'application/json' data.
			 - 'file' - A file path to send as the response.
			 - 'bytes' - A byte[] to send back. The content type will be 'application/octet-stream' if not specified.
			 - 'response' - Any type of plain text response.
			 - 'contentType' - The mime type. Need only if ambiguous.
	'''
	logger = LIBRARY_LOGGER.getSubLogger('processRequest')
	
	logger.trace("Calculating URI Base...")
	uriBase = swagGl.getUriBase(request)
	
	logger.trace("Determining root Script Package for request, and by extension, the Swagger Statics and Definitions modules")
	rootPackage = swagGl.getRootPackage(request)
	swagStc = swagGl.getNamedModuleFromRoot(rootPackage, 'statics')
	swagDf = swagGl.getNamedModuleFromRoot(rootPackage, 'definitions')
	
	#Doing the necessary extension of the WebDev Request Python Dictionary, since the WebDev Module doesn't
	# do everything we had hoped that it would.
	logger.trace("Initializing WebDevRequest instance.")
	wdr = WebDevRequest(request, session)
	wdr.logInitialReceipt()
	try:
		logger.trace("Augmenting URI information using URI Base of '{!s}'".format(uriBase))
		wdr.augmentRequestURI(uriBase = uriBase)
	except (Exception, java.lang.Exception), e:
		etype, evalue, tb = sys.exc_info() if isinstance(e, Exception) else (type(e), e, None)
		logger.error(
			"Internal Server Error (WebDevRequest initialization). '{!s}'".format(e.message),
			server.castToJavaException(e, tb)
		)
		logger.trace("Generating Internal Server Error response (Augmenting WebDevRequest)")
		response = swagRsp.httpStatus(wdr.request, "Internal Server Error")
		wdr.logOutgoingData(response)
		return response
	#END TRY/EXCEPT
	
	#Attempting to find the project script that defines the endpoint the request came to.
	logger.trace("Will try finding a Script Module at path {!r}".format(wdr.swag['resource-path']))
	try:
		foundPackage = findBestScriptResourceFromPath(wdr.swag['resource-path'], swagStc)
	except (Exception, java.lang.Exception), e:
		etype, evalue, tb = sys.exc_info() if isinstance(e, Exception) else (type(e), e, None)
		logger.error(
			"Internal Server Error (WebDevRequest initialization). '{!s}'".format(e.message),
			server.castToJavaException(e, tb)
		)
		logger.trace("Generating Internal Server Error response (Finding Script Resource)")
		response = swagRsp.httpStatus(wdr.request, "Internal Server Error")
		wdr.logOutgoingData(response)
		return response
	#END TRY/EXCEPT
	if foundPackage is None:
		response = swagRsp.httpStatus(wdr.request, "Not Found")
		wdr.logOutgoingData(response)
		return response
	#END IF
	#Adding the "remaining path" to the WebDevRequest object. This needs to be done here because the WebDevRequest
	# object does not know what the actual base URI is when initializing. We have to wait until we can call
	# `findBestScriptResourceFromPath` to determine what is actually left over
	wdr.swag['remainingPath'] = foundPackage['remainingPath']
	#Also adding the Path Parameters found.
	wdr.swag['pathParams'] = foundPackage['pathParams']
	
	#After finding the necessary project script, we intialize an "Endpoint" instance with the WebDevRequest instance,
	# which will allow us to execute all of the validation and authentication, and then we return the response
	try:
		endpointObj = Endpoint(
			wdr,
			foundPackage['fullName'],
			foundPackage['scriptModule'],
			swagStc, swagDf,
			logger
		)
	except (Exception, java.lang.Exception), e:
		etype, evalue, tb = sys.exc_info() if isinstance(e, Exception) else (type(e), e, None)
		logger.error(
			"Internal Server Error (Endpoint class initialization). '{!s}'".format(e.message),
			server.castToJavaException(e, tb)
		)
		logger.trace("Generating Internal Server Error response (Endpoint Creation)")
		response = swagRsp.httpStatus(wdr.request, "Internal Server Error")
		wdr.logOutgoingData(response)
		return response
	#END TRY/EXCEPT
	response = None
	try:
		logger.trace("Executing Endpoint")
		response = endpointObj.execute()
	except (Exception, java.lang.Exception), e:
		etype, evalue, tb = sys.exc_info() if isinstance(e, Exception) else (type(e), e, None)
		logger.error(
				"Internal Server Error (BaseEndpoint class execution). '{!s}'".format(e.message),
				server.castToJavaException(e, tb)
			)
		logger.trace("Generating Internal Server Error response (Endpoint Execution)")
		response = swagRsp.httpStatus(wdr.request, "Internal Server Error")
	finally:
		wdr.logOutgoingData(response)
		return response
	#END TRY/EXCEPT/FINALLY
##END DEF