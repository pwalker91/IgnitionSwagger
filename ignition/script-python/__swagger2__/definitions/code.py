'''
	A series of Swagger references that can be used in other endpoints.
	https://swagger.io/docs/specification/2-0/basic-structure/
	https://swagger.io/docs/specification/data-models/data-types/#numbers
'''

SCHEMES = ['http', 'https']

INFO = {
	"description":
		"This is an Ignition implementation of a sample server Petstore server, plus some added functionality. "+
		"You can find out more about Swagger at [http://swagger.io](http://swagger.io) or on "+
			"[irc.freenode.net, #swagger](http://swagger.io/irc/). "+
		"For this sample, you can use the api key `special-key` to test the authorization filters.",
	"version": "1.0.5",
	"title": "Swagger Petstore",
	"termsOfService": "http://swagger.io/terms/",
	#"contact": {
	#	"email": "apiteam@swagger.io"
	#},
	#"license": {
	#	"name": "Apache 2.0",
	#	"url": "http://www.apache.org/licenses/LICENSE-2.0.html"
	#},
}

DEFINITIONS = {
	#PetStore definitions
	"ApiResponse": {
		"type": "object",
		"properties": {
			"code": {
				"type": "integer",
				"format": "int32"
			},
			"type": {
				"type": "string"
			},
			"message": {
				"type": "string"
			},
		},
	},
	"Category": {
		"type": "object",
		"properties": {
			"id": {
				"type": "integer",
				"format": "int64"
			},
			"name": {
				"type": "string"
			},
		},
		"xml": {
			"name": "Category"
		},
	},
	"Pet": {
		"type": "object",
		"required": ["name", "photoUrls"],
		"properties": {
			"id": {
				"type": "integer",
				"format": "int64"
			},
			"category": {
				"$ref": "#/definitions/Category"
			},
			"name": {
				"type": "string",
				"example": "doggie"
			},
			"photoUrls": {
				"type": "array",
				"xml": {
					"wrapped": True
				},
				"items": {
					"type": "string",
					"xml": {
						"name": "photoUrl"
					},
				},
			},
			"tags": {
				"type": "array",
				"xml": {
					"wrapped": True
				},
				"items": {
					"xml": {
						"name": "tag"
					},
					"$ref": "#/definitions/Tag"
				},
			},
			"status": {
				"type": "string",
				"description": "pet status in the store",
				"enum": ["available", "pending", "sold"]
			},
		},
		"xml": {
			"name": "Pet"
		},
	},
	"Tag": {
		"type": "object",
		"properties": {
			"id": {
				"type": "integer",
				"format": "int64"
			},
			"name": {
				"type": "string"
			},
		},
		"xml": {
			"name": "Tag"
		},
	},
	"Order": {
		"type": "object",
		"properties": {
			"id": {
				"type": "integer",
				"format": "int64"
			},
			"petId": {
				"type": "integer",
				"format": "int64"
			},
			"quantity": {
				"type": "integer",
				"format": "int32"
			},
			"shipDate": {
				"type": "string",
				"format": "date-time"
			},
			"status": {
				"type": "string",
				"description": "Order Status",
				"enum": ["placed", "approved", "delivered"]
			},
			"complete": {
				"type": "boolean"
			},
		},
		"xml": {
			"name": "Order"
		},
	},
	"User": {
		"type": "object",
		"properties": {
			"id": {
				"type": "integer",
				"format": "int64"
			},
			"username": {
				"type": "string"
			},
			"firstName": {
				"type": "string"
			},
			"lastName": {
				"type": "string"
			},
			"email": {
				"type": "string"
			},
			"password": {
				"type": "string"
			},
			"phone": {
				"type": "string"
			},
			"userStatus": {
				"type": "integer",
				"format": "int32",
				"description": "User Status"
			},
		},
		"xml": {
			"name": "User"
		},
	},
}

PARAMETERS = {
	'objs_api_key_header': {
		'description': 'IgnitionSwagger Static API Key in header',
		'in': 'header',
		'name': 'IS-API-Key',
		'type': 'string',
		'required': True,
		'is-x-obscure': True,
		'example': '3C5D3F69EEA6C05B',
	},
}

SECURITY = {
	"api_key": {
		"type": "apiKey",
		"name": "api_key",
		"in": "header"
	},
	"petstore_auth": {
		"type": "oauth2",
		"authorizationUrl": "https://petstore.swagger.io/oauth/authorize",
		"flow": "implicit",
		"scopes": {
			"read:pets": "read your pets",
			"write:pets": "modify pets in your account"
		}
	}
}