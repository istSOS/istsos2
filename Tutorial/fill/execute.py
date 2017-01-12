# -*- coding: utf-8 -*-
import requests
import json
import procedure
import virtual
import os
service_url = "http://localhost/istsos/"

service = {
	"service": "demo"
}

url = service_url + "wa/istsos/services"

print " Create new service"
# create service
r = requests.post(url, data=json.dumps(service))
print r.text

procedure.insert_procedure(service_url, service['service'])
virtual.insert_virtual(service_url, service['service'])

# missing
# load data to db

# cp FAO56 script to virtual folder
#os.system("sudo cp ../vp/")

print " Terminated :)"
