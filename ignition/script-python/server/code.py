'''
	This script contains functions that allow WebDev scripts, Gateway Timer scripts, and other areas of the system
	to know which server they are executing on, and which database to get information from
'''

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# IMPORTS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import system
import time
import types
import pprint
import java.lang.Exception
import java.lang.StackTraceElement
import java.lang.String
import traceback



def timeInMilli():
	'''
	@FUNC	Gets the number of milliseconds since epoch
			https://stackoverflow/a/5998359
	'''
	return int(round(time.time()) * 1000)
#END DEF

class Logger(object):
	'''
	This is our custom Logger class, whose functions simply use the built in system logging, but offers some
	  improved granularity of how the message is show in Development vs. Production.
	'''
	
	_acceptedLevels = ['trace', 'debug', 'info', 'warn', 'error', 'fatal']
	
	def __init__(self, name):
		if not isinstance(name, types.StringTypes):
			name = 'GenericLogger'
		self.name = name.strip()
		self.starttime = None
		self.logger = system.util.getLogger(self.name)
	#END DEF
	
	def getSubLogger(self, subname):
		if not isinstance(subname, types.StringTypes):
			subname = 'SubLogger'
		newName = self.logger.getName()+"."+subname.strip()
		newLogger = Logger(newName)
		return newLogger
	#END DEF
	
	def startTimer():
		self.starttime = timeInMilli()
	#END DEF
	
	def stopTimer():
		self.starttime = None
	#END DEF
	
	def log(self, message, extraInfo=None, level='info'):
		'''
		@FUNC	Logs a message at the specified Level, based on which server this code is running on.
		@PARAM	message : String
		@PARAM	extraInfo : Object, which will be converted into a Java Exception
		@PARAM	level : String, the function name that will log a message at a specific logger level
		@RETURN	N/A
		'''
		level = str(level).lower()
		if level not in self._acceptedLevels:
			raise Exception(
				"Log Level {!s} is invalid. Log Level must be one of the following options: {!r}".format(
					level, self._acceptedLevels
				)
			)
		fullMessage = str(message)
		if self.starttime is not None:
			fullMessage = "{!s} - {!s}".format((timeInMilli() - self.starttime), fullMessage)
		f = getattr(self.logger, level)
		if not isinstance(f, types.MethodType):
			raise Exception("Found property '{!s}', but it is not a valid method.".format(level))
		if extraInfo is not None:
			if isinstance(extraInfo, (Exception, java.lang.Exception)):
				f(fullMessage, castToJavaException(extraInfo))
			else:
				f(fullMessage, specialCastToJavaException(extraInfo))
		else:
			f(fullMessage)
	#END DEF
	
	def __getattr__(self, attr):
		'''
		@FUNC	Overriding the default method that gets attributes so that we can catch calls to the
				functions that come in the system Logger (eg. debug, trace, info, etc.)
		'''
		if attr.lower() in self._acceptedLevels:
			def _callLog(message='', extraInfo=None, level=attr):
				self.log(message=message, extraInfo=extraInfo, level=level)
			return _callLog
		else:
			try:
				return object.__getattribute__(self, attr)
			except KeyError:
				raise AttributeError(attr)
		#END IF/ELSE
	#END DEF
#END CLASS

def getLogger(name):
	return Logger(name)
#END DEF



def getExceptionStackTrace(e):
	'''
	Given an exception, converts the object into a String message of what the error 
	'''
	def _getJavaException(e):
		err = "-- JAVA EXCEPTION STACK TRACE --\n"
		try:
			err += "MESSAGE: "+e.getMessage().replace("\t","").replace("\n", " ")
		except:
			err += "MESSAGE: Could not nicely parse Exception Message: ({!s})".format(e.getMessage())
		err += "\n"
		try:
			err += "CAUSE: "+e.getCause().getMessage().replace("\t","").replace("\n"," ")
		except:
			err += "CAUSE: Could not nicely parse Exception Cause: ({!s})".format(e.getCause())
		err += "\n"
		for traceElem in e.getStackTrace():
			err += "  File \"{!s}\", line {!s}, in {!s}->{!s}\n".format(
					traceElem.getFileName(),
					traceElem.getLineNumber(),
					traceElem.getClassName(), traceElem.getMethodName()
				)
		#END FOR
		err += "\n-- END JAVA EXCEPTION STACK TRACE --"
		return err
	#END DEF
	def _getPythonException(e):
		err = "-- PYTHON EXCEPTION STACK TRACE --\n"
		err += traceback.format_exc()
		err += "\n-- END PYTHON EXCEPTION STACK TRACE --"
		return err
	#END DEF
	if isinstance(e, java.lang.Exception):
		tracebackMsg = _getJavaException(e)
	else:
		tracebackMsg = _getPythonException(e)
	return tracebackMsg
#END DEF

def castToJavaException(pe, tb=None):
	'''
	@FUNC	Casts the given Python Exception to a Java Exception
	@PARAM	pe : Python Exception
	@PARAM	tb : Traceback object, the "actual" traceback
	@RETURN	java.lang.Exception object
	'''
	if isinstance(pe, java.lang.Exception):
		return pe
	#This is creating a new "type", giving the type's name as the name of the Java Exception...
	# - type(je.__class__.__name__,
	#... telling it to inherit from the Exception class...
	# - (Exception,),
	#... and initializing the __dict__ property with whatever we want.
	# - {})
	# Then, we create an instance of the type, passing it the original Java Exception's message
	# - (je.getMessage())
	newE = type(pe.__class__.__name__, (java.lang.Exception,), {})(pe.message)
	#Because Python 2.7 is finnicky, we will only get the actual stack trace if this function
	# is being called from within an EXCEPT block. This is because the traceback is tied to the current
	# execution space, and will only have references to the linking traceback objects while in the block.
	# https://stackoverflow.com/questions/11414894/extract-traceback-info-from-an-exception-object
	# https://stackoverflow.com/a/11415140
	#So, we will just cross our fingers that the call below will give us a traceback object
	if tb is not None:
		pyTB = traceback.extract_tb(tb)
	else:
		pyTB = traceback.extract_stack()
	newE.setStackTrace(
		[
			java.lang.StackTraceElement(
				# https://docs.python.org/2/library/traceback.html#traceback.extract_tb
				# https://docs.oracle.com/javase/7/docs/api/java/lang/StackTraceElement.html
				## TUPLE VALUE DESC --> JAVA CLASS CONSTRUCTOR ARG
				tbElem[0].replace('<','[').replace('>',']'),  #file name --> declaringClass
				tbElem[2],  #function name --> methodName
				"line",  #file name --> fileName
				tbElem[1]  #line number --> lineNumber
				# tbElem[3] is the python tracback text, which java doesn't have a place for
			)
			for tbElem in pyTB[::-1]
		]
	)
	return newE
#END DEF

def castToPythonException(je):
	'''
	@FUNC	Casts the given Java Exception to a Python Exception. Unfortunately, we can't create a traceback from
			the StackTrace in the Java Exception. We will just have to suffice with the exception message
	@PARAM	je : Java Exception
	@RETURN	a Python Exception object
	'''
	if isinstance(je, Exception):
		return je
	#This is creating a new "type", giving the type's name as the name of the Java Exception...
	# - type(je.__class__.__name__,
	#... telling it to inherit from the Exception class...
	# - (Exception,),
	#... and initializing the __dict__ property with whatever we want.
	# - {})
	# Then, we create an instance of the type, passing it the original Java Exception's message
	# - (je.getMessage())
	newE = type(je.__class__.__name__, (Exception,), {})(je.getMessage())
	#Because of the way Python's traceback stuff works in Python 2.7, we cannot create a traceback
	# from the Java Stack Trace.
	# See the explanation in `castToJavaException`
	return newE
#END DEF

def specialCastToJavaException(specialData, message=None):
	'''
	@FUNC	Takes a Python Dictionary and converts it into a "Java Exception" so that we can print out the
			Dictionary in Ignition's Gateway Log Console in an easier-to-read format that doesn't clog up the output
	@PARAM	specialData : Object, whatever this function can currently "smartly" turn into a Java Exception
	@PARAM	message : String, the message to put into the Java Exception, which is what will be the immediately
				visible message in the Gateway Log Console
	@RETURN	Java Exception
	'''
	if not isinstance(message, types.StringTypes):
		message = "Converted some special data ({!s}) into a Java Exception".format(type(specialData))
	validTypes = (types.DictionaryType, types.ListType)
	if isinstance(specialData, validTypes):
		dataAsListOfStrings = pprint.pformat(specialData, width=120, indent=2).split("\n")
		fakeE = java.lang.Exception(message)
		fakeE.setStackTrace(
			[
				java.lang.StackTraceElement('','','--- START OF OBJECT ---',0)
			] +
			[
				java.lang.StackTraceElement('','', "{:<130}".format(dataAsListOfStrings[lineNum]) ,0)
				for lineNum in range(len(dataAsListOfStrings))
			] +
			[
				java.lang.StackTraceElement('','','--- END OF OBJECT ---',0)
			]
		)
		return fakeE
	else:
		raise Exception("Given value for 'specialData' must be one of the possible types: {!r}".format(validTypes))
#END DEF