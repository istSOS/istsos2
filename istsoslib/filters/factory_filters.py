# -*- coding: utf-8 -*-
# ===============================================================================
#
# Authors: Massimiliano Cannata, Milan Antonovic
#
# Copyright (c) 2015 IST-SUPSI (www.supsi.ch/ist)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# ===============================================================================
from istsoslib import sosException
import cgi
from urlparse import parse_qs
import sys

def sosFactoryFilter(environ,sosConfig):
    """Instantiate the correct filter type depending on requests

    Args:
        environ (obj): the mod_wsgi environment object
        sosCOnfig (obj): the service configuration

    Returns:
        filter (obj): the filter subclass which meet the request

    Raises:
        Exception if missing or invalid parameters are used in the request

    """
    content_type = environ.get('CONTENT_TYPE', '')
    
    #---- set method, requestObject and sosRequest ----
    method = str(environ['REQUEST_METHOD']).upper()
    
    if method=="GET":
        # Returns a dictionary containing lists as values.
        rect = parse_qs(environ['QUERY_STRING'])
        requestObject = {}
        for key in rect.keys():
            requestObject[key.lower()] = rect[key][0]

        if requestObject.has_key("request"):
            sosRequest = requestObject["request"].lower()
        else:
            raise sosException.SOSException("MissingParameterValue","request","Parameter \"request\" is mandatory") 

    elif method=="POST":
        # the environment variable CONTENT_LENGTH may be empty or missing
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0

        # get the request
        from xml.dom import minidom
        
        content = environ['wsgi.input'].read(request_body_size)
        print >> sys.stderr, "***************************************************"
        
        print >> sys.stderr, content
        
        if content_type.startswith("application/x-www-form-urlencoded"):
            print >> sys.stderr, "application/x-www-form-urlencoded"
            form = cgi.parse_qs(content)
            if form.has_key("request"):
                xmldoc = minidom.parseString(form["request"][0])
            else:
                raise sosException.SOSException("MissingParameterValue","request","Parameter \"request\" is mandatory")

        else:
            print >> sys.stderr, "body"
            try:
                xmldoc = minidom.parseString(content)
            except:
                raise sosException.SOSException("MissingParameterValue",None,"Unable to parse the request body: validation issue")
            
        requestObject = xmldoc.firstChild
        sosRequest = requestObject.localName.lower()
            
    else:
        err_txt = "Allowed \"http request\" are GET and POST: %s" %(method=="GET")
        raise sosException.SOSException("InvalidRequest",None,err_txt)
        
    #--- if request is allowed instantiate the rigth filter ---
    if sosRequest in sosConfig.parameters["requests"]:
        if sosRequest == "getcapabilities":
            from istsoslib.filters import GC_filter
            return GC_filter.sosGCfilter(sosRequest,method,requestObject,sosConfig)
        elif sosRequest == "describesensor":
            from istsoslib.filters import DS_filter
            return DS_filter.sosDSfilter(sosRequest,method,requestObject,sosConfig)
        elif sosRequest == "getobservation":
            from istsoslib.filters import GO_filter
            return GO_filter.sosGOfilter(sosRequest,method,requestObject,sosConfig)
        elif sosRequest == "getfeatureofinterest":
            from istsoslib.filters import GF_filter
            return GF_filter.sosGFfilter(sosRequest,method,requestObject,sosConfig)
        elif sosRequest == "insertobservation":
            from istsoslib.filters import IO_filter
            return IO_filter.sosIOfilter(sosRequest,method,content,sosConfig)
        elif sosRequest == "registersensor":
            from istsoslib.filters import RS_filter
            return RS_filter.sosRSfilter(sosRequest,method,content,sosConfig)
        elif sosRequest == "updateSensorDescription":
            from istsoslib.filters import USD_filter
            return USD_filter.sosUSDfilter(sosRequest,method,requestObject,sosConfig)
    else:
        raise sosException.SOSException("InvalidParameterValue","request","\"request\": %s not supported" %(sosRequest))
    

