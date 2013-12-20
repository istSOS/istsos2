# -*- coding: utf-8 -*-
# istsos Istituto Scienze della Terra Sensor Observation Service
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

from lib import isodate as iso

def render(GO,sosConfig):
    if GO.filter.responseFormat in ['text/xml;subtype="sensorML/1.0.0"',"text/xml"]:
        return XMLformat(GO)
    elif GO.filter.responseFormat=="text/plain":
        return CSVformat(GO)
#    elif GO.filter.responseFormat=="image/png":
#        return CHARTformat(GO)
    elif GO.filter.responseFormat in ["application/json","text/x-json"]:
        return JSONformat(GO)
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
    
    for ob in GO.obs:
        
        #OBSERVATION OBJ
        r += "<om:member>\n"
        r += "  <om:Observation>\n"
        r += "    <gml:name>" + ob.name + "</gml:name>\n"
        
        #PERIODO DI CAMPIONAMENTO DEI DATI ESTRATTI      
        if ob.samplingTime != None:
            r += "    <om:samplingTime>\n"
            r += "      <gml:TimePeriod>\n"
            r += "        <gml:beginPosition>" + ob.samplingTime[0].astimezone(GO.reqTZ).strftime("%Y-%m-%dT%H:%M:%S.%f%z") + "</gml:beginPosition>\n"
            if ob.samplingTime[1]:
                r += "        <gml:endPosition>" + ob.samplingTime[1].astimezone(GO.reqTZ).strftime("%Y-%m-%dT%H:%M:%S.%f%z") + "</gml:endPosition>\n"
            else:
                r += "        <gml:endPosition>" + ob.samplingTime[0].astimezone(GO.reqTZ).strftime("%Y-%m-%dT%H:%M:%S.%f%z") + "</gml:endPosition>\n"
            if ob.samplingTime[1]:
                r += "        <gml:duration>"  + iso.duration_isoformat(ob.samplingTime[1]-ob.samplingTime[0]) + "</gml:duration>\n"
            r += "      </gml:TimePeriod>\n"
            r += "    </om:samplingTime>\n"
        else:
            r += "    <om:samplingTime/>\n"
        
        #PROCEDURE
        r += "    <om:procedure xlink:href=\"" + ob.procedure + "\"/>\n"                
        
        #PROPRIETA OSSERVATA
        if ob.procedureType == "insitu-fixed-point":
            ii=1
        elif ob.procedureType == "insitu-mobile-point":
            ii=4
        elif ob.procedureType == "virtual":
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
        r += "    <om:featureOfInterest xlink:href=\"" + ob.foi_urn + "\">\n"
        r += "      <gml:FeatureCollection>\n"
        r += "        <gml:location>\n"
        r += "          " + ob.foiGml + "\n"
        r += "        </gml:location>\n"
        r += "      </gml:FeatureCollection>\n"
        r += "    </om:featureOfInterest>"
    
        #SERIE TEMPORALE
        r += "    <om:result>\n"
        
        #ii = 1
        #if ob.procedureType=="insitu-mobile-point":
        #    ii = 4
        
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
        if len(ob.data)>0:
            r += "        <swe:values>"
            data=[]
            for row in range(len(ob.data)):
                #str_data=[ob.data[row][0].astimezone(GO.reqTZ).strftime("%Y-%m-%dT%H:%M:%S.%f%z")]
                str_data=[ob.data[row][0].strftime("%Y-%m-%dT%H:%M:%S.%f%z")]
                for i in range(1,len(ob.data[0])):
                    str_data.append(str(ob.data[row][i]))
                data.append(",".join(str_data))
            r += "@".join(data)
            r += "</swe:values>\n"
        else:
            r += "        <swe:values/>"
        r += "      </swe:DataArray>\n"
        r += "    </om:result>\n"
        r += "  </om:Observation>\n"
        r += "</om:member>\n"
    r += "</om:ObservationCollection>" 
    return r

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
            member["samplingTime"]["beginPosition"] = ob.samplingTime[0].astimezone(GO.reqTZ).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
            if ob.samplingTime[1]:
                member["samplingTime"]["endPosition"] = ob.samplingTime[1].astimezone(GO.reqTZ).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
                member["samplingTime"]["duration"] = iso.duration_isoformat(ob.samplingTime[1]-ob.samplingTime[0])
            else:
                member["samplingTime"]["endPosition"] = ob.samplingTime[0].astimezone(GO.reqTZ).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
                """      
                member["samplingTime"]["timeInterval"] = {
                    "unit": ob.timeResUnit,
                    "value": ob.timeResVal
                }
                """
        if ob.procedureType == "insitu-fixed-point":
            ii=1
        elif ob.procedureType == "insitu-mobile-point":
            ii=4
        elif ob.procedureType == "virtual":
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
        
        member['result']['DataArray']['values'] = []
        for row in range(len(ob.data)):
            #data = [ob.data[row][0].astimezone(GO.reqTZ).strftime("%Y-%m-%dT%H:%M:%S.%f%z")]
            data = [ob.data[row][0].strftime("%Y-%m-%dT%H:%M:%S.%f%z")]
            for i in range(1,len(ob.data[0])):
                data.append(str(ob.data[row][i]))
            member['result']['DataArray']['values'].append(data)
            
        # append member to collection
        oc["ObservationCollection"]["member"].append(member)

    
    
    return json.dumps(oc)
    #return json.dumps(wut.encodeobject(oc))

def CSVformat(GO):
    #create unique columns name
    columns = ["time","procedure"]
    columns_name = [None,"urn:ogc:def:procedure"]
    
    
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
    
    #create rows
    rows = []
    for iob, ob in enumerate(GO.obs):
        #create look-up-table for given observation member
        #associates opr index with row index
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
        #raise Exception( "%s - %s" %(lut,columns))
        #create row
        
        
        #append row
        for vals in ob.data:
            row = [""] * len(columns)
            #row[0] = vals[0].astimezone(GO.reqTZ).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
            row[0] = vals[0].strftime("%Y-%m-%dT%H:%M:%S.%f%z")
            row[1] = ob.procedure.split(":")[-1]
            for i in range(1,len(vals)):
                row[lut[i]] = str(vals[i])
            rows.append(row)
            #raise Exception( "%s - %s -%s" %(lut,columns,rows))
                
    #write results as CSV    
    r  = ",".join(columns_name) + "\n"
    for c in rows:
        r += ",".join(c) + "\n"
    
    return r


    
