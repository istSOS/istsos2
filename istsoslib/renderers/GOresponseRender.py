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
import isodate as iso
from istsoslib import sosException
from lxml import etree as et
import hashlib
import sys
import datetime

from ..utils import escape

date_handler = lambda obj: (
    obj.isoformat()
    if isinstance(obj, (datetime.datetime, datetime.date))
    else (
        obj
        if isinstance(obj, str)
        else float(obj)
    )
)

to_string_handler = lambda obj: (
    obj.isoformat()
    if isinstance(obj, (datetime.datetime, datetime.date))
    else (
        obj
        if isinstance(obj, str)
        else str(obj)
    )
)

def render(GO,sosConfig):
    if GO.filter.responseFormat in ['text/xml;subtype="om/1.0.0"',"text/xml"]:
        return XMLformat(GO)
    elif GO.filter.responseFormat=="text/plain":
        return CSVformat(GO)
#    elif GO.filter.responseFormat=="image/png":
#        return CHARTformat(GO)
    elif GO.filter.responseFormat in ["application/json","text/x-json"]:
        return JSONformat(GO)
    elif GO.filter.responseFormat in ['text/xml;subtype="om/2.0"']:
        return XMLformat_2_0_0(GO, sosConfig)
    else:
        raise Exception("not supported format: %s, try one of %s" % (GO.filter.responseFormat,"; ".join(sosConfig.parameters["GO_responseFormat"])))

def XMLformat(GO):
    r = """<om:ObservationCollection xmlns:sos="http://www.opengis.net/sos/1.0"
  xmlns:om="http://www.opengis.net/om/1.0" xmlns:swe="http://www.opengis.net/swe/1.0.1"
  xmlns:gml="http://www.opengis.net/gml" xmlns:xlink="http://www.w3.org/1999/xlink"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.opengis.net/om/1.0  http://schemas.opengis.net/om/1.0.0/om.xsd">
"""
    r += "<gml:description>" + GO.offInfo.desc + "</gml:description>\n"    
    r += "<gml:name>" + GO.offInfo.name + "</gml:name>\n"    
    
    if len(GO.obs)==0:
        r += "<om:member/>\n"
        #raise sosException.SOSException("NoApplicableCode",None,"No matching observation was found according the request parameters!")
        
    for ob in GO.obs:
        
        #OBSERVATION OBJ
        r += "<om:member>\n"
        r += "  <om:Observation>\n"
        r += "    <gml:name>" + ob.name + "</gml:name>\n"
        
        #PERIODO DI CAMPIONAMENTO DEI DATI ESTRATTI      
        if ob.samplingTime != None:
            r += "    <om:samplingTime>\n"
            r += "      <gml:TimePeriod>\n"
#            r += "        <gml:beginPosition>" + ob.samplingTime[0].astimezone(GO.reqTZ).strftime("%Y-%m-%dT%H:%M:%S.%f%z") + "</gml:beginPosition>\n"
            
            r += "        <gml:beginPosition>" + ob.samplingTime[0].astimezone(GO.reqTZ).isoformat() + "</gml:beginPosition>\n"
            
            if ob.samplingTime[1]:
                r += "        <gml:endPosition>" + ob.samplingTime[1].astimezone(GO.reqTZ).isoformat() + "</gml:endPosition>\n"
            else:
                r += "        <gml:endPosition>" + ob.samplingTime[0].astimezone(GO.reqTZ).isoformat() + "</gml:endPosition>\n"
                
            if ob.samplingTime[1]:
                r += "        <gml:duration>"  + iso.duration_isoformat(ob.samplingTime[1]-ob.samplingTime[0]) + "</gml:duration>\n"
            r += "      </gml:TimePeriod>\n"
            r += "    </om:samplingTime>\n"
        else:
            r += "    <om:samplingTime/>\n"
        
        #PROCEDURE
        r += "    <om:procedure xlink:href=\"" + escape(ob.procedure) + "\"/>\n"
        
        #PROPRIETA OSSERVATA
        if ob.procedureType == "insitu-mobile-point":
            ii=4
        else:
            ii=1
        
        #OBSERVED PROPERTIES
        r += "    <om:observedProperty>\n"
        r += "      <swe:CompositePhenomenon gml:id=\"comp_" + str(ob.id_prc) + "\" dimension=\"" + str(len(ob.opr_urn)+ii) + "\">\n"
        r += "        <gml:name>timeSeriesOfObservations</gml:name>\n"
        r += "        <swe:component xlink:href=\"" + ob.timedef + "\"/>\n"
        
        if ob.procedureType=="insitu-mobile-point":
            r += "        <swe:component xlink:href=\"" + GO.refsys + ":x-position\"/>\n"
            r += "        <swe:component xlink:href=\"" + GO.refsys + ":y-position\"/>\n"
            r += "        <swe:component xlink:href=\"" + GO.refsys + ":z-position\"/>\n"

        for urn in ob.opr_urn:    
            r += "        <swe:component xlink:href=\"" + urn + "\"/>\n"
        r += "      </swe:CompositePhenomenon>\n"
        r += "    </om:observedProperty>\n"      
    
        #FEATURE OF INTEREST
        r += "    <om:featureOfInterest xlink:href=\"" + escape(ob.foi_urn) + "\">\n"
        r += "      <gml:FeatureCollection>\n"
        r += "        <gml:location>\n"
        r += "          " + ob.foiGml + "\n"
        r += "        </gml:location>\n"
        r += "      </gml:FeatureCollection>\n"
        r += "    </om:featureOfInterest>"
    
        #SERIE TEMPORALE
        r += "    <om:result>\n"
        
        #DESCRIZIONE DEI DATI ESTRATTI: VARIA A SECONDA DEL TIPO DI PROCEDURA
        
        #-- CASO GENERALE
        r += "      <swe:DataArray>\n"
        r += "        <swe:elementCount>\n"
        r += "          <swe:Count>\n"
        r += "            <swe:value>" + str(len(ob.observedProperty)+ii) + "</swe:value>\n"
        r += "          </swe:Count>\n"
        r += "        </swe:elementCount>\n"
        r += "        <swe:elementType name=\"SimpleDataArray\">\n"
        r += "          <swe:DataRecord>\n"
        r += "            <swe:field name=\"Time\">\n"
        r += "              <swe:Time definition=\"" + ob.timedef + "\"/>\n"
        r += "            </swe:field>\n"
        
        if ob.procedureType=="insitu-mobile-point":
            r += "            <swe:field name=\"x-position\">\n"
            r += "              <swe:Quantity definition=\"" + GO.refsys + ":x-position\"/>\n"
            r += "            </swe:field>\n"
            r += "            <swe:field name=\"y-position\">\n"
            r += "              <swe:Quantity definition=\"" + GO.refsys + ":y-position\"/>\n"
            r += "            </swe:field>\n"
            r += "            <swe:field name=\"z-position\">\n"
            r += "              <swe:Quantity definition=\"" + GO.refsys + ":z-position\"/>\n"
            r += "            </swe:field>\n"
            if ob.qualityIndex:
                r += "            <swe:field name=\"position-qualityIndex\">\n"
                r += "              <swe:Quantity definition=\"" + GO.refsys + ":position:qualityIndex\"/>\n"
                r += "            </swe:field>\n"

        for idx in range(len(ob.observedProperty)):
            if ob.aggregate_function:
                if ob.observedProperty[idx].split(":")[-1] == "qualityIndex":
                    r += "            <swe:field name=\"%s\">\n" % (ob.observedPropertyName[idx])
                    r += "              <swe:Quantity definition=\"%s\">\n" % (ob.observedProperty[idx])
                else:
                    r += "            <swe:field name=\"%s:%s\">\n" % (ob.observedPropertyName[idx],ob.aggregate_function)
                    r += "              <swe:Quantity definition=\"%s:%s\">\n" % (ob.observedProperty[idx],ob.aggregate_function)
                if ob.aggregate_function.upper()=="COUNT":
                    r += "                <swe:uom code=\"None\"/>\n"
                else:
                    r += "                <swe:uom code=\"" + ob.uom[idx] + "\"/>\n"
            else:
                r += "            <swe:field name=\"%s\">\n" % (ob.observedPropertyName[idx])
                r += "              <swe:Quantity definition=\"" + ob.observedProperty[idx] + "\">\n"
                r += "                <swe:uom code=\"" + ob.uom[idx] + "\"/>\n"
            r += "              </swe:Quantity>\n"
            r += "            </swe:field>\n"
            
        r += "          </swe:DataRecord>\n"
        r += "        </swe:elementType>\n"
        r += "        <swe:encoding>\n"
        r += "          <swe:TextBlock tokenSeparator=\",\" blockSeparator=\"@\" decimalSeparator=\".\"/>\n"
        r += "        </swe:encoding>\n"

        if ob.csv:
            values = ''
            for row in ob.csv.split('@'):
                val = row.split(',')
                values += f'           <swe:value dateTime="{val[0]}">{val[1]}</swe:value>\n'
            r += "        <swe:values>\n"
            r += values
            r += "        </swe:values>\n"

        elif len(ob.data) > 0:
            data=[]
            r += "<swe:values>"
            for row in range(len(ob.data)):
                r+=','.join(
                    list(map(
                        lambda x: to_string_handler(x), ob.data[row]
                    ))
                )
            r += "</swe:values>\n"

        else:
            r += "        <swe:values/>"

        r += "      </swe:DataArray>\n"
        r += "    </om:result>\n"
        r += "  </om:Observation>\n"
        r += "</om:member>\n"
    r += "</om:ObservationCollection>" 
    return r.encode()

def JSONformat(GO):
    import json

    oc = {
        "ObservationCollection": {
            "description": GO.offInfo.desc,
            "name": GO.offInfo.name,            
            "member": []
        }
    }
    for iob, ob in enumerate(GO.obs):
        member = {
            "name": ob.name,
            "samplingTime": {},
            "procedure": ob.procedure
        }
        
        if ob.samplingTime != None:
            member["samplingTime"]["beginPosition"] = ob.samplingTime[0].astimezone(GO.reqTZ).isoformat()
            if ob.samplingTime[1]:
                member["samplingTime"]["endPosition"] = ob.samplingTime[1].astimezone(GO.reqTZ).isoformat()
                member["samplingTime"]["duration"] = iso.duration_isoformat(ob.samplingTime[1]-ob.samplingTime[0])
                
            else:
                member["samplingTime"]["endPosition"] = ob.samplingTime[0].astimezone(GO.reqTZ).isoformat()
        
        if ob.procedureType == "insitu-mobile-point":
            ii=4
        else:
            ii=1
            
        member['observedProperty'] = {
            "CompositePhenomenon": {
                "id": "comp_%s" % str(ob.id_prc),
                "dimension": str(len(ob.opr_urn)+ii),
                "name": "timeSeriesOfObservations"
            }
        }
        
        member['observedProperty']["component"] = [ob.timedef]
        
        if ii==4:
            member['observedProperty']["component"] += [
                ("%s:x-position" % GO.refsys), 
                ("%s:y-position" % GO.refsys), 
                ("%s:z-position" % GO.refsys)
            ]
            
        member['observedProperty']["component"] += ob.opr_urn
        
        member['featureOfInterest'] = {
            "name": ob.foi_urn,
            "geom": ob.foiGml.replace("\"","'")
        }
        
        member['result'] = {
            "DataArray": {
                "elementCount": str(len(ob.observedProperty)+ii),
                "field": [
                    {
                        "name": "Time",
                        "definition": ob.timedef
                    }
                ]
            }
        }
        if ii==4:
            member['result']['DataArray']['field'] += [
                {
                    "name": "x-position",
                    "definition": "%s:x-position" % GO.refsys
                },
                {
                    "name": "y-position",
                    "definition": "%s:y-position" % GO.refsys
                },
                {
                    "name": "z-position",
                    "definition": "%s:z-position" % GO.refsys
                }
            ]
        for idx in range(len(ob.observedProperty)):
            member['result']['DataArray']['field'] += [
                {
                    "name": ob.observedPropertyName[idx],
                    "definition": ob.observedProperty[idx],
                    "uom": ob.uom[idx]  
                }
            ]
        
        member['result']['DataArray']['values'] = ob.data

        # append member to collection
        oc["ObservationCollection"]["member"].append(member)

    return json.dumps(oc, default=date_handler).encode()

def CSVformat(GO):
    #create unique columns name
    columns = ["time","procedure"]
    columns_name = [None,"urn:ogc:def:procedure"]
    uoms = []
    
    for iob, ob in enumerate(GO.obs):
        if columns_name[0]==None:
            columns_name[0] = ob.timedef
        if ob.procedureType == "insitu-mobile-point":
            columns += ["x-position","y-position","z-position"]
            columns_name += ["%s:x-position" % GO.refsys,"%s:y-position" % GO.refsys,"%s:z-position" % GO.refsys]
        for idx,opr in enumerate(ob.observedProperty):
            if not opr in columns:
                columns += [opr]
                columns_name += ["%s" %(opr)]
                uoms.append(ob.uom[idx])
            elif ob.uom[idx] not in uoms:
                columns += [opr]
                columns_name += ["%s" %(opr)]
                uoms.append(ob.uom[idx])
            elif opr == f'{columns[-1]}:qualityIndex':
                columns += [opr]
                columns_name += ["%s" %(opr)]
    

    r  = ",".join(columns_name)

    #create rows
    rows = []
    csv_rows = ""
    for iob, ob in enumerate(GO.obs):

        if ob.csv:
            r += "\n%s" % ob.csv

        else:
            lut = { 0 : 0}
            i=0

            if ob.procedureType == "insitu-mobile-point":
                lut[1] = columns.index("x-position")
                lut[2] = columns.index("y-position")
                lut[3] = columns.index("z-position")
                i=3

            for opr in ob.observedProperty:
                i += 1
                try:
                    lut[i] = columns.index(opr)
                except:
                    raise Exception("%s - %s" %(lut,columns))

            for vals in ob.data:
                row = [""] * len(columns)
                row[0] = vals[0].isoformat()
                row[1] = ob.procedure.split(":")[-1]
                for i in range(1,len(vals)):
                    row[lut[i]] = str(vals[i])

                r += "\n%s" % (
                    ','.join(
                        map(
                            lambda x: to_string_handler(x), row
                        )
                    )
                )

    return r.encode("utf-8")


def XMLformat_2_0_0(GO, sosConfig):
    
    res = et.XML("""<sos:GetObservationResponse 
            xmlns:sos="http://www.opengis.net/sos/2.0" 
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
            xmlns:om="http://www.opengis.net/om/2.0" 
            xmlns:gml="http://www.opengis.net/gml/3.2" 
            xmlns:xlink="http://www.w3.org/1999/xlink" 
            xsi:schemaLocation="http://www.opengis.net/sos/2.0 http://schemas.opengis.net/sos/2.0/sosGetObservation.xsd http://www.opengis.net/gml/3.2 http://schemas.opengis.net/gml/3.2.1/gml.xsd http://www.opengis.net/om/2.0 http://schemas.opengis.net/om/2.0/observation.xsd">
        </sos:GetObservationResponse>""")
        
    ns = {
        'xsi': "http://www.w3.org/2001/XMLSchema-instance" ,
        'sos': "http://www.opengis.net/sos/2.0" ,
        'om': "http://www.opengis.net/om/2.0", 
        'gml':'http://www.opengis.net/gml/3.2',
        'xlink': "http://www.w3.org/1999/xlink"
    }
    
    # map namespaces
    try:
        register_namespace = et.register_namespace
        for key in ns:
            register_namespace(key, ns[key])
    except AttributeError:
        try:
            et._namespace_map.update(ns)
            for key in ns:
                et._namespace_map[ns[key]] = key
        except AttributeError:
            try:
                from xml.etree.ElementTree import _namespace_map
            except ImportError:
                try:
                    from elementtree.ElementTree import _namespace_map
                except ImportError:
                    print(("Failed to import ElementTree from any known place"), file=sys.stderr)
            for key in ns:
                _namespace_map[ns[key]] = key
        
    if len(GO.obs)>0:    
        data = et.SubElement(res, '{%s}observationData' % ns['sos'])
        for observation in GO.obs:
            cnt = 1
            idx = 0
            while idx < len(observation.observedProperty):
                
                observedProperty = observation.observedProperty[idx]
                observedPropertyId = observation.observedPropertyId[idx]
                uom = observation.uom[idx]
                
                for result in observation.data:
                    
                    uid = "%s_%s_%s" % (
                        observation.id_prc, result[0].strftime("%s"), observedPropertyId)
                    
                    # Creating om:OM_Observation
                    omobservation = et.SubElement(data, '{%s}OM_Observation' % ns['om'])
                    
                    omobservation.set("{%s}id" % ns['gml'], "o_%s" % hashlib.md5(uid).hexdigest())
                    
                    # Adding om:type with attribute
                    et.SubElement(omobservation, '{%s}type' % ns['om']).set(
                        "{%s}href" % ns['xlink'], 
                        'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement'
                    )
                    
                    # Adding om:phenomenonTime 
                    phenomenonTime = et.SubElement(omobservation, '{%s}phenomenonTime' % ns['om'])
                    
                    # Generating TimeInstant id shared that will be linked from the phenomenonTime 
                    timeInstantId = "p_%s" % hashlib.md5(uid).hexdigest()
                    
                    # Adding gml:TimeInstant
                    timeInstant = et.SubElement(phenomenonTime, '{%s}TimeInstant' % ns['gml'])
                    timeInstant.set("{%s}id" % ns['gml'], timeInstantId)
                    
                    # Adding gml:timePosition ad date value as string (iso format)
                    et.SubElement(timeInstant, '{%s}timePosition' % ns['gml']).text = result[0].isoformat()
                    
                    # Adding om:phenomenonTime 
                    et.SubElement(omobservation, '{%s}resultTime' % ns['om']).set(
                        "{%s}href" % ns['xlink'], '#%s' % timeInstantId
                    )
                    
                    # Adding om:procedure
                    et.SubElement(omobservation, '{%s}procedure' % ns['om']).set(
                        "{%s}href" % ns['xlink'], "%s%s" % (sosConfig.urn["procedure"], observation.name)
                    )
                    
                    # Add quality index as parameter
                    if observation.qualityIndex:
                        
                        parameter = et.SubElement(omobservation, '{%s}parameter' % ns['om'])
                        namedValue = et.SubElement(parameter, '{%s}NamedValue' % ns['om'])
                        name = et.SubElement(namedValue, '{%s}name' % ns['om'])
                        name.set("{%s}href" % ns['xlink'], observation.observedProperty[idx+1])
                        value = et.SubElement(namedValue, '{%s}value' % ns['om'])                        
                        value.text = str(result[cnt+1])
                    
                    # Adding om:observedProperty
                    et.SubElement(omobservation, '{%s}observedProperty' % ns['om']).set(
                        "{%s}href" % ns['xlink'], observedProperty
                    )
                    
                    # Adding om:featureOfInterest
                    et.SubElement(omobservation, '{%s}featureOfInterest' % ns['om']).set(
                        "{%s}href" % ns['xlink'], observation.foi_urn
                    )
                    
                    # Adding om:result
                    omresult = et.SubElement(omobservation, '{%s}result' % ns['om'])
                    omresult.set("uom", uom)
                    omresult.set("{%s}type" % ns['xsi'], "gml:MeasureType")
                    omresult.text = str(result[cnt])
                    
                if observation.qualityIndex:
                    idx += 2
                    cnt += 2
                else:
                    idx += 1
                    cnt += 1
                    
                
    """
    http://sensorweb.demo.52north.org/sensorwebtestbed/client
    
    Examples: 
    http://sensorweb.demo.52north.org/sensorwebtestbed/service?service=SOS&request=GetCapabilities&crs=4258
    http://sensorweb.demo.52north.org/sensorwebtestbed/service?service=SOS&version=2.0.0&request=GetObservation&procedure=ws2500&temporalFilter=om:phenomenonTime,2016-02-24T00:00:00.000Z/2016-02-24T13:00:00.000Z
    http://sensorweb.demo.52north.org/sensorwebtestbed/service?service=SOS&version=2.0.0&request=GetObservation&procedure=ws2500&temporalFilter=om:phenomenonTime,2016-02-24T00:00:00.000Z/2016-02-24T13:00:00.000Z&MergeObservationsIntoDataArray=true
    
    """
    
    return b'<?xml version="1.0" encoding="UTF-8"?>\n%s' % et.tostring(res)
    
