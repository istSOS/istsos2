# istSOS Istituto Scienze della Terra Sensor Observation Service
# Copyright (C) 2010 Massimiliano Cannata
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import sosConfig
from istSOS.filters import filter
from istSOS import sosException
import cgi
from cgi import parse_qsl, escape
from urlparse import parse_qs

def sosFactoryFilter(environ):
    #W httpRequest.content_type = "text/xml"
    content_type = environ.get('CONTENT_TYPE', '')
    
    #---- set method, requestObject and sosRequest ----
    #W method=str(httpRequest.method)
    method = str(environ['REQUEST_METHOD']).upper()
    
    if method=="GET":
        # Returns a dictionary containing lists as values.
        rect = parse_qs(environ['QUERY_STRING'])
        requestObject = {}
        for key in rect.keys():
            # requestObject[key.lower()] = rect[key][0]
            requestObject[key] = rect[key][0]

        #raise sosException.SOSException(1,"%s -- %s -- %s" %(environ['QUERY_STRING'],parse_qs(environ['QUERY_STRING']),requestObject))
        
        if requestObject.has_key("request"):
            sosRequest = requestObject["request"].lower()
        else:
            raise sosException.SOSException(1,"Parameter \"request\" is required") 

    elif method=="POST":
        # the environment variable CONTENT_LENGTH may be empty or missing
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0

        # get the request
        #W form = environ['wsgi.input'].read(request_body_size)
        from xml.dom import minidom
        
        #raise sosException.SOSException(1,"%s" % environ.get('wsgi.post_form'))

        content = environ['wsgi.input'].read(request_body_size)
        if content_type.startswith("application/x-www-form-urlencoded"):
            form = cgi.parse_qs(content)
            if form.has_key("request"):
                xmldoc = minidom.parseString(form["request"][0])
                requestObject = xmldoc.firstChild
                sosRequest = requestObject.localName.lower()
            else:
                raise sosException.SOSException(3,"NO request found in mod_python req.form object!")

        else:
            xmldoc = minidom.parseString(content)
            requestObject = xmldoc.firstChild
            sosRequest = requestObject.localName.lower()
        """
        if form.has_key("request"):
            xmldoc = minidom.parseString(environ['wsgi.input'].read(request_body_size))
            requestObject = xmldoc.firstChild
            sosRequest = requestObject.localName.lower()
        else:
            raise sosException.SOSException(3,"NO request found in mod_python req.form object!")
        
        if method in ["GET","POST"]:
            if method == "GET":
                requestObject = httpRequest.form
                if requestObject.has_key("request"):
                    sosRequest = requestObject["request"].lower()
                else:
                    raise sosException.SOSException(1,"Parameter \"request\" is required")
            if method == "POST":
                from xml.dom import minidom
                
                if httpRequest.form.has_key("request"):
                    xmldoc = minidom.parseString(httpRequest.form['request'])
                    requestObject = xmldoc.firstChild
                    sosRequest = requestObject.localName.lower()
                
                else:
                    #xmldoc = minidom.parseString(httpRequest.read_body)
                    #xmldoc = minidom.parseString(httpRequest.form)
                    #requestObject = xmldoc.firstChild
                    #sosRequest = requestObject.localName.lower()  
                    raise sosException.SOSException(3,"NO request found in mod_python req.form object!")          
        """       
    else:
        err_txt = "Allowed \"http request\" are GET and POST: %s" %(method=="GET")
        raise sosException.SOSException(1,err_txt)
        
    #--- if request is allowed instantiate the rigth filter ---
    if sosRequest in sosConfig.parameters["requests"]:
        if sosRequest == "getcapabilities":
            from istSOS.filters import GC_filter
            return GC_filter.sosGCfilter(sosRequest,method,requestObject)
        elif sosRequest == "describesensor":
            from istSOS.filters import DS_filter
            return DS_filter.sosDSfilter(sosRequest,method,requestObject)
        elif sosRequest == "getobservation":
            from istSOS.filters import GO_filter
            return GO_filter.sosGOfilter(sosRequest,method,requestObject)
        elif sosRequest == "getfeatureofinterest":
            from istSOS.filters import GF_filter
            return GF_filter.sosGFfilter(sosRequest,method,requestObject)
        elif sosRequest == "insertobservation":
            from istSOS.filters import IO_filter
            return IO_filter.sosIOfilter(sosRequest,method,requestObject)
        elif sosRequest == "registersensor":
            from istSOS.filters import RS_filter
            return RS_filter.sosRSfilter(sosRequest,method,requestObject)
        elif sosRequest == "updateSensorDescription":
            from istSOS.filters import USD_filter
            return USD_filter.sosUSDfilter(sosRequest,method,requestObject)
    else:
        raise sosException.SOSException(1,"\"request\": %s not supported" %(sosRequest))
    

