# -*- coding: utf-8 -*-
import requests
import json

def rest_request(url, json_data):

	r = requests.post(url, data=json.dumps(json_data))

	if not r.json()['success']:
		print("problem with ", json_data['system_id'])
		print(r.json())

def insert_virtual(service_url, service):

	v_lugano = {
		"system_id":"V_LUGANO",
		"system":"V_LUGANO",
		"description":"Meteo Station in Lugnano",
		"keywords":"weather,meteorological,IST",
		"identification":[
			{
				"definition":"urn:ogc:def:identifier:OGC:uniqueID",
				"name":"uniqueID",
				"value":"urn:ogc:def:procedure:x-istsos:1.0:V_LUGANO"
			}
		],
		"classification":[
			{
				"name":"System Type",
				"definition":"urn:ogc:def:classifier:x-istsos:1.0:systemType",
				"value":"virtual"
			},
			{
				"name":"Sensor Type",
				"definition":"urn:ogc:def:classifier:x-istsos:1.0:sensorType",
				"value":"virtual procedure"
			}
		],
		"characteristics":"",
		"contacts":[],
		"documentation":[],
		"capabilities":[],
		"location":{
			"type":"Feature",
			"geometry":{
				"type":"Point",
				"coordinates":["8.96127","46.02723","344.1"]
			},
			"crs":{
				"type":"name",
				"properties":{
					"name":"4326"
				}
			},
			"properties":{
			"name":"LUGANO"
			}
		},
		"interfaces":"",
		"inputs":[],
		"outputs":[
			{
				"name":"Time",
				"definition":"urn:ogc:def:parameter:x-istsos:1.0:time:iso8601",
				"uom":"iso8601",
				"description":"",
				"constraint":{}
			},
			{
				"name":"air-temperature",
				"definition":"urn:ogc:def:parameter:x-istsos:1.0:meteo:air:temperature",
				"uom":"°F",
				"description":"",
				"constraint":{
					"role":"urn:ogc:def:classifiers:x-istsos:1.0:qualityIndex:check:reasonable",
					"interval":["-40.0","60.0"]
				}
			}
		],
		"history":[]
	}

	v_gnosca = {
		"system_id":"V_GNOSCA",
		"system":"V_GNOSCA",
		"description":"water discharge calculated from RH_GNOSCA",
		"keywords":"water,discharge,IST",
		"identification":[
			{
				"definition":"urn:ogc:def:identifier:OGC:uniqueID",
				"name":"uniqueID",
				"value":"urn:ogc:def:procedure:x-istsos:1.0:V_GNOSCA"
			}
		],
		"classification":[
			{
				"name":"System Type",
				"definition":"urn:ogc:def:classifier:x-istsos:1.0:systemType",
				"value":"virtual"
			},
			{
				"name":"Sensor Type",
				"definition":"urn:ogc:def:classifier:x-istsos:1.0:sensorType",
				"value":"virtual procedure"
			}
		],
		"characteristics":"",
		"contacts":[],
		"documentation":[],
		"capabilities":[],
		"location":{
			"type":"Feature",
			"geometry":{
				"type":"Point",
				"coordinates":["9.01939","46.23339","278.8"]
			},
			"crs":{
				"type":"name",
				"properties":{
					"name":"4326"
				}
			},
			"properties":{
			"name":"GNOSCA"
			}
		},
		"interfaces":"",
		"inputs":[],
		"outputs":[
			{
				"name":"Time",
				"definition":"urn:ogc:def:parameter:x-istsos:1.0:time:iso8601",
				"uom":"iso8601",
				"description":"",
				"constraint":{}
			},
			{
				"name":"river-water-discharge",
				"definition":"urn:ogc:def:parameter:x-istsos:1.0:river:water:discharge",
				"uom":"m3/s",
				"description":"",
				"constraint":{}
			}
		],
		"history":[]
	}

	url = service_url + 'wa/istsos/services/' + service + "/procedures"

	print(" Add virtual procedure")

	rest_request(url, v_lugano)
	rest_request(url, v_gnosca)
	
	print(" Add virtual procedure script")

	# V_LUGANO
	f = open('vp/V_LUGANO.py', 'r')
	code_lugano = f.read()

	code_lugano = {
		"code" : code_lugano
	}

	url = service_url + "wa/istsos/services/" + service + "/virtualprocedures/" + v_lugano['system_id'] + "/code"

	r = requests.post(url, data=json.dumps(code_lugano))
	print(r.text)

	# V_GNOSCA
	gnosca_curve = [
		{
			"from":"2014-05-01T00:00:00+02:00",
			"to":"2014-06-15T00:00:00+02:00",
			"up_val":"2.5",
			"low_val":"0",
			"A":"10.324",
			"B":"0",
			"C":"1.65",
			"K":"0"
		},
		{
			"from":"2014-06-15T00:00:00+02:00",
			"to":"2017-01-31T00:00:00+01:00",
			"up_val":"2.5",
			"low_val":"0",
			"A":"10.425",
			"B":"0",
			"C":"1.556",
			"K":"0"
		}
	]

	url = service_url + "wa/istsos/services/" + service + "/virtualprocedures/" + v_gnosca['system_id'] + "/code"
	f = open('vp/V_GNOSCA.py', 'r')
	code_gnosca = f.read()

	code_gnosca = {
		"code" : code_gnosca
	}

	r = requests.post(url, data=json.dumps(code_gnosca))
	if not r.json()['success']:
		print(r.json())


	url = service_url + "wa/istsos/services/" + service + "/virtualprocedures/" + v_gnosca['system_id'] + "/ratingcurve"

	r = requests.post(url, data=json.dumps(gnosca_curve))
	if not r.json()['success']:
		print(r.json())
