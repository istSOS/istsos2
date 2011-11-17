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

import isodate as iso
import datetime

def render(GO):
    if GO.filter.responseFormat in ["text/xml;subtype='sensorML/1.0.0'","text/xml"]:
        return XMLformat(GO)
    elif GO.filter.responseFormat=="text/plain":
        return CSVformat(GO)
    elif GO.filter.responseFormat=="image/png":
        return CHARTformat(GO)
    elif GO.filter.responseFormat in ["application/json","text/x-json"]:
        return JSONformat(GO)
    else:
        raise Exception("not supported format: %s, try one of text/xml;subtype='sensorML/1.0.0' - text/csv - image/png")

def XMLformat(GO):
    r = """<om:ObservationCollection xmlns:sos="http://www.opengis.net/sos/1.0"
  xmlns:om="http://www.opengis.net/om/1.0" xmlns:swe="http://www.opengis.net/swe/1.0.1"
  xmlns:gml="http://www.opengis.net/gml" xmlns:xlink="http://www.w3.org/1999/xlink"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.opengis.net/om/1.0  http://schemas.opengis.net/om/1.0.0/om.xsd">
"""
    r += "<gml:name>" + GO.offInfo.name + "</gml:name>\n"
    r += "<gml:description>" + GO.offInfo.desc + "</gml:description>\n"
    
    for ob in GO.obs:
    
        #OBSERVATION OBJ
        r += "<om:member>\n"
        r += "  <om:Observation>\n"
        r += "    <om:procedure xlink:href=\"" + ob.procedure + "\"/>\n"
    
        #PERIODO DI CAMPIONAMENTO DEI DATI ESTRATTI      
        if ob.samplingTime != None:
            r += "    <om:samplingTime>\n"
            r += "      <gml:TimePeriod>\n"
            r += "        <gml:beginPosition>" + iso.datetime_isoformat(ob.samplingTime[0].astimezone(GO.reqTZ)) + "</gml:beginPosition>\n"
            if ob.samplingTime[1]:
                r += "        <gml:endPosition>" + iso.datetime_isoformat(ob.samplingTime[1].astimezone(GO.reqTZ)) + "</gml:endPosition>\n"
            else:
                r += "        <gml:endPosition>" + iso.datetime_isoformat(ob.samplingTime[0].astimezone(GO.reqTZ)) + "</gml:endPosition>\n"
            r += "        <gml:TimeLength>\n"
            if ob.samplingTime[1]:
                r += "          <gml:duration>"  + iso.duration_isoformat(ob.samplingTime[1]-ob.samplingTime[0]) + "</gml:duration>\n"
            #r += "          <gml:timeInterval unit=\"" + str(ob.timeResUnit) + "\" radix=\"" + str(ob.timeResVal) + "\" factor=\"1\" />\n"
            r += "          <gml:timeInterval unit=\"" + str(ob.timeResUnit) + "\">" + str(ob.timeResVal) + "</gml:timeInterval>\n"            
            r += "        </gml:TimeLength>\n"
            r += "      </gml:TimePeriod>\n"
            r += "    </om:samplingTime>\n"
        else:
            r += "    <om:samplingTime/>\n"

    
        #PROPRIETA OSSERVATA
        if ob.procedureType == "fixpoint":
            ii=1
        elif ob.procedureType == "mobilepoint":
            ii=4
        elif ob.procedureType == "virtual":
            ii=1
            
        r += "    <om:observedProperty>\n"
        r += "      <swe:CompositePhenomenon id=\"comp_" + str(ob.id_prc) + "\" dimension=\"" + str(len(ob.opr_urn)+ii) + "\">\n"
        r += "        <swe:component xlink:href=\"" + ob.timedef + "\"/>"
            
        if ob.procedureType=="mobilepoint":
            #r += "        <swe:component xlink:href=\"" + ob.timedef + "\"/>"            
            r += "        <swe:component xlink:href=\"" + GO.refsys + ":x-position\"/>"
            r += "        <swe:component xlink:href=\"" + GO.refsys + ":y-position\"/>"
            r += "        <swe:component xlink:href=\"" + GO.refsys + ":z-position\"/>"

        for urn in ob.opr_urn:    
            r += "        <swe:component xlink:href=\"" + urn + "\"/>"
        r += "      </swe:CompositePhenomenon>\n"
        r += "    </om:observedProperty>\n"      
    
        #FEATURE OF INTEREST
        r += "    <om:featureOfInterest xlink:href=\"" + ob.foi_urn + "\">\n"
        r += ob.foiGml
        r += "    </om:featureOfInterest>"
    
        #SERIE TEMPORALE
        r += "    <om:result>\n"
        
        #ii = 1
        #if ob.procedureType=="mobilepoint":
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
        
        if ob.procedureType=="mobilepoint":
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
                    try:
                        r += "            <swe:field name=\"%s-%s\">\n" % (ob.observedProperty[idx].split(":")[-2],ob.observedProperty[idx].split(":")[-1])
                    except:
                        r += "            <swe:field name=\"%s\">\n" % (ob.observedProperty[idx].split(":")[-1])
                    r += "              <swe:Quantity definition=\"%s\">\n" % (ob.observedProperty[idx])
                else:
                    r += "            <swe:field name=\"%s-%s\">\n" % (ob.observedProperty[idx].split(":")[-1],ob.aggregate_function)
                    r += "              <swe:Quantity definition=\"%s:%s\">\n" % (ob.observedProperty[idx],ob.aggregate_function)
                if ob.aggregate_function.upper()=="COUNT":
                    r += "                <swe:uom code=\"None\"/>\n"
                else:
                    r += "                <swe:uom code=\"" + ob.uom[idx] + "\"/>\n"
            else:
                try:
                    r += "            <swe:field name=\"%s-%s\">\n" % (ob.observedProperty[idx].split(":")[-2],ob.observedProperty[idx].split(":")[-1])
                except:
                    r += "            <swe:field name=\"%s\">\n" % (ob.observedProperty[idx].split(":")[-1])
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
                #str_data=[iso.datetime_isoformat(ob.data[row][0].astimezone(GO.reqTZ))]
                str_data=[ob.data[row][0].astimezone(GO.reqTZ).strftime("%Y-%m-%dT%H:%M:%S.%f%z")]
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
    r  = ""
    r += "{"
    r += "\"ObservationCollection\": {"
    r +=      "  \"name\": \"%s\"" % GO.offInfo.name
    r +=      ", \"description\": \"%s\"" % GO.offInfo.desc
    r +=      ", \"member\": [ "
    
    for iob, ob in enumerate(GO.obs):
        if iob == 0:
            r +=    "  {"
        else:
            r +=    ", {"
        r +=        "  \"procedure\" : \"%s\"" % ob.procedure
        r +=        ", \"samplingTime\" : {"
        r +=            "  \"beginPosition\" : \"%s\"" % iso.datetime_isoformat(ob.samplingTime[0].astimezone(GO.reqTZ))
        if ob.samplingTime[1]:
            r +=        ", \"endPosition\" : \"%s\"" % iso.datetime_isoformat(ob.samplingTime[1].astimezone(GO.reqTZ))
            r +=        ", \"duration\" : \"%s\"" % iso.duration_isoformat(ob.samplingTime[1]-ob.samplingTime[0])
        else:
            r +=        ", \"endPosition\" : \"%s\"" % iso.datetime_isoformat(ob.samplingTime[0].astimezone(GO.reqTZ))
        r +=            ", \"timeInterval\" : { \"unit\" : \"%s\", \"value\" : \"%s\"}" %(str(ob.timeResUnit),str(ob.timeResVal))
        r +=            "}"
        
        #PROPRIETA OSSERVATA
        if ob.procedureType == "fixpoint":
            ii=1
        elif ob.procedureType == "mobilepoint":
            ii=4
        elif ob.procedureType == "virtual":
            ii=1
        
        r +=        ", \"observedProperty\" : {"
        r +=            "  \"CompositePhenomenon\" : {"
        r +=                    "  \"id\" : \"comp_%s\"" % str(ob.id_prc)
        r +=                    ", \" dimension\" : \"%s\" }" % str(len(ob.opr_urn)+ii)
        r +=                    ", \" component\" : ["
        r +=                    "  \"%s\"" % ob.timedef
            
        if ii==4:
            #r +=                    "  \"%s\"" % ob.timedef            
            r +=                    ", \"%s:x-position\"" % GO.refsys
            r +=                    ", \"%s:y-position\"" % GO.refsys
            r +=                    ", \"%s:z-position\"" % GO.refsys
        
        for urn in ob.opr_urn:
            r +=                    ", \"%s\"" % urn
        
        r +=                "]"
        #r +=            "}"
        r +=        "}"
        
        r +=        ", \"featureOfInterest\" : {"
        r +=            "  \"name\" : \"%s\"" % ob.foi_urn
        r +=            ", \"geom\" : \"%s\"" % ob.foiGml.replace("\"","'")
        r +=        "}"
        
        r +=        ", \"result\" : {"
        r +=            "  \"DataArray\" : {"
        r +=                    "  \"elementCount\" : \"%s\"" % str(len(ob.observedProperty)+ii)
        r +=                    ", \"field\" : ["
        r +=                            "   { \"name\" : \"Time\""
        r +=                            "  , \"definition\" : \"%s\"}" % ob.timedef
        if ii==4:
            r +=                        ",  { \"name\" : \"x-position\"" 
            r +=                        "  , \"definition\" : \"%s\"}" % GO.refsys
            r +=                        ",  { \"name\" : \"y-position\"" 
            r +=                        "  , \"definition\" : \"%s\"}" % GO.refsys
            r +=                        ",  { \"name\" : \"z-position\"" 
            r +=                        "  , \"definition\" : \"%s\"}" % GO.refsys
       
       
        for idx in range(len(ob.observedProperty)):
            try:
                r +=                        ",  { \"name\" : \"%s-%s\"" % (ob.observedProperty[idx].split(":")[-2],ob.observedProperty[idx].split(":")[-1])
            except:
                r +=                        ",  { \"name\" : \"-%s\"" % (ob.observedProperty[idx].split(":")[-1])
            r +=                        "  , \"definition\" : \"%s\"" % ob.opr_urn[idx]
            r +=                        "  , \"uom\" : \"%s\"}" % ob.uom[idx]  
        r +=                    " ]"        
        r +=                    ", \"values\" : ["
        data=[]
        for row in range(len(ob.data)):
            #str_data=["\"" + iso.datetime_isoformat(ob.data[row][0].astimezone(GO.reqTZ)) + "\""]
            str_data=["\"" + ob.data[row][0].astimezone(GO.reqTZ).strftime("%Y-%m-%dT%H:%M:%S.%f%z") + "\""]            

            for i in range(1,len(ob.data[0])):
                str_data.append("\"" + str(ob.data[row][i]) + "\"")
            data.append("[" + ",".join(str_data) + "]")
        r += ",".join(data)
        r += "]"
        r +=            "  }"
        r +=        "}" 
        
        #close member element
        r +=    "}"
    #close member list
    r +=      "]"
    #close ObservationCollection
    r += "}"
    #close json
    r += "}"
    
    return r

def CSVformat(GO):
    #create unique columns name
    columns = ["time","procedure"]
    columns_name = ["time","procedure"]
    
    for iob, ob in enumerate(GO.obs):
        if ob.procedureType == "mobilepoint":
            columns += ["x-position","y-position","z-position"]
        for idx,opr in enumerate(ob.observedProperty):
            if not opr in columns:
                columns += [opr]
                try:
                    columns_name += ["%s-%s" %(ob.observedProperty[idx].split(":")[-2],ob.observedProperty[idx].split(":")[-1])]
                except:
                    columns_name += ["%s" %(ob.observedProperty[idx].split(":")[-1])]
            
    #create rows
    rows = []
    for iob, ob in enumerate(GO.obs):
        #create look-up-table for given observation member
        #associates opr index with row index
        lut = { 0 : 0}
        i=0
        if ob.procedureType == "mobilepoint":
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
            #row[0] = iso.datetime_isoformat(vals[0].astimezone(GO.reqTZ))
            row[0] = vals[0].astimezone(GO.reqTZ).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
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


    
