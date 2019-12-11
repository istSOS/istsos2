# -*- coding: utf-8 -*-
import requests
import json

def rest_request(url, json_data):

	r = requests.post(url, data=json.dumps(json_data))

	if not r.json()['success']:
		print("problem with ", json_data['system_id'])
		print(r.json())

def insert_procedure(service_url, service):
	t_lugano = {
			"system_id":"T_LUGANO",
			"system":"T_LUGANO",
			"description":"temperature weather station in Lugano",
			"keywords": "weather, meteorological, IST",
			"identification":[
				{
					"name":"uniqueID",
					"definition":"urn:ogc:def:identifier:OGC:uniqueID",
					"value":"urn:ogc:def:procedure:x-istsos:1.0:T_LUGANO"
				}
			],
			"classification":[
				{
					"name":"System Type",
					"definition":"urn:ogc:def:classifier:x-istsos:1.0:systemType",
					"value":"insitu-fixed-point"
				},
				{
					"name":"Sensor Type",
					"definition":"urn:ogc:def:classifier:x-istsos:1.0:sensorType",
					"value":"Davis weather station"
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
					"properties":{"name":"4326"}
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
					"uom":"°C",
					"description":"conversion from resistance to temperature",
					"constraint":{
						"role":"urn:ogc:def:classifiers:x-istsos:1.0:qualityIndex:check:reasonable",
						"interval":["-40","60"]
					}
				}
			],
			"history":[]
		}

	p_lugano = {
			"system_id":"P_LUGANO",
			"system":"P_LUGANO",
			"description":"temperature weather station in Locarno",
			"keywords": "weather, meteorological, IST",
			"identification":[
				{
					"name":"uniqueID",
					"definition":"urn:ogc:def:identifier:OGC:uniqueID",
					"value":"urn:ogc:def:procedure:x-istsos:1.0:P_LUGANO"
				}
			],
			"classification":[
				{
					"name":"System Type",
					"definition":"urn:ogc:def:classifier:x-istsos:1.0:systemType",
					"value":"insitu-fixed-point"
				},
				{
					"name":"Sensor Type",
					"definition":"urn:ogc:def:classifier:x-istsos:1.0:sensorType",
					"value":"Davis weather station"
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
					"properties":{"name":"4326"}
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
					"name":"air-rainfall",
					"definition":"urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall",
					"uom":"mm",
					"description":"-",
					"constraint":{
						"role":"urn:ogc:def:classifiers:x-istsos:1.0:qualityIndex:check:reasonable",
						"interval":["0","500"]
					}
				}
			],
			"history":[]
		}


	locarno = {
			"system_id":"LOCARNO",
			"system":"LOCARNO",
			"description":"temperature weather station in Locarno",
			"keywords": "weather, meteorological, IST",
			"identification":[
				{
					"name":"uniqueID",
					"definition":"urn:ogc:def:identifier:OGC:uniqueID",
					"value":"urn:ogc:def:procedure:x-istsos:1.0:LOCARNO"
				}
			],
			"classification":[
				{
					"name":"System Type",
					"definition":"urn:ogc:def:classifier:x-istsos:1.0:systemType",
					"value":"insitu-fixed-point"
				},
				{
					"name":"Sensor Type",
					"definition":"urn:ogc:def:classifier:x-istsos:1.0:sensorType",
					"value":"Davis weather station"
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
					"coordinates":["8.79212","46.15515","197.8"]
				},
				"crs":{
					"type":"name",
					"properties":{"name":"4326"}
				},
				"properties":{
					"name":"LOCARNO"
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
					"uom":"°C",
					"description":"conversion from resistance to temperature",
					"constraint":{
						"role":"urn:ogc:def:classifiers:x-istsos:1.0:qualityIndex:check:reasonable",
						"interval":["-40","60"]
					}
				},
				{
					"name":"air-rainfall",
					"definition":"urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall",
					"uom":"mm",
					"description":"-",
					"constraint":{
						"role":"urn:ogc:def:classifiers:x-istsos:1.0:qualityIndex:check:reasonable",
						"interval":["0","500"]
					}
				}
			],
			"history":[]
		}

	bellinzona = {
			"system_id":"BELLINZONA",
			"system":"BELLINZONA",
			"description":"Meteo Station in Bellinzona",
			"keywords": "weather, meteorological, IST",
			"identification":[
				{
					"name":"uniqueID",
					"definition":"urn:ogc:def:identifier:OGC:uniqueID",
					"value":"urn:ogc:def:procedure:x-istsos:1.0:BELLINZONA"
				}
			],
			"classification":[
				{
					"name":"System Type",
					"definition":"urn:ogc:def:classifier:x-istsos:1.0:systemType",
					"value":"insitu-fixed-point"
				},
				{
					"name":"Sensor Type",
					"definition":"urn:ogc:def:classifier:x-istsos:1.0:sensorType",
					"value":"Davis weather station"
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
					"coordinates":["9.01976","46.20322","226.3"]
				},
				"crs":{
					"type":"name",
					"properties":{"name":"4326"}
				},
				"properties":{
					"name":"BELLINZONA"
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
					"uom":"°C",
					"description":"conversion from resistance to temperature",
					"constraint":{
						"role":"urn:ogc:def:classifiers:x-istsos:1.0:qualityIndex:check:reasonable",
						"interval":["-40","60"]
					}
				},
				{
					"name":"air-humidity-relative",
					"definition":"urn:ogc:def:parameter:x-istsos:1.0:meteo:air:humidity:relative",
					"uom":"%",
					"description":"-",
					"constraint":{
						"role":"urn:ogc:def:classifiers:x-istsos:1.0:qualityIndex:check:reasonable",
						"interval":["0","100"]
					}
				},
				{
					"name":"air-rainfall",
					"definition":"urn:ogc:def:parameter:x-istsos:1.0:meteo:air:rainfall",
					"uom":"%",
					"description":"-",
					"constraint":{
						"role":"urn:ogc:def:classifiers:x-istsos:1.0:qualityIndex:check:reasonable",
						"interval":["0","500"]
					}
				},
				{
					"name":"air-wind-velocity",
					"definition":"urn:ogc:def:parameter:x-istsos:1.0:meteo:air:wind:velocity",
					"uom":"m/s",
					"description":"-",
					"constraint":{
						"role":"urn:ogc:def:classifiers:x-istsos:1.0:qualityIndex:check:reasonable",
						"interval":["0","200"]
					}
				}
			],
			"history":[]
		}


	gnosca = {
			"system_id":"RH_GNOSCA",
			"system":"RH_GNOSCA",
			"description":"River height River of Gnosca",
			"keywords": "river, water, height, IST",
			"identification":[
				{
					"name":"uniqueID",
					"definition":"urn:ogc:def:identifier:OGC:uniqueID",
					"value":"urn:ogc:def:procedure:x-istsos:1.0:RH_GNOSCA"
				}
			],
			"classification":[
				{
					"name":"System Type",
					"definition":"urn:ogc:def:classifier:x-istsos:1.0:systemType",
					"value":"insitu-fixed-point"
				},
				{
					"name":"Sensor Type",
					"definition":"urn:ogc:def:classifier:x-istsos:1.0:sensorType",
					"value":"Pressure sensor"
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
					"properties":{"name":"4326"}
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
					"name":"water-height",
					"definition":"urn:ogc:def:parameter:x-istsos:1.0:river:water:height",
					"uom":"m",
					"description":"conversion from resistance to temperature",
					"constraint":{
						"role":"urn:ogc:def:classifiers:x-istsos:1.0:qualityIndex:check:reasonable",
						"interval":["0","1.5"]
					}
				}
			],
			"history":[]
		}

	url = service_url + 'wa/istsos/services/' + service + '/procedures'


	print(" Add procedure")
	rest_request(url, t_lugano)
	rest_request(url, p_lugano)
	rest_request(url, locarno)
	rest_request(url, bellinzona)
	rest_request(url, gnosca)


	
