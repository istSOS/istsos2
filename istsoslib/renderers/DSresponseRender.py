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

from istsoslib import sosException
import sys   
from lib.etree import et
import json

reurl = r'(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?'

def parse_and_get_ns(filename):
    events = "start", "start-ns"

    root = None
    ns = {}
    f = open(filename)
    for event, elem in et.iterparse(f, events):
        if event == "start-ns":
            if elem[0] in ns and ns[elem[0]] != elem[1]:
                # NOTE: It is perfectly valid to have the same prefix refer
                #   to different URI namespaces in different parts of the
                #   document. This exception serves as a reminder that this
                #   solution is not robust.  Use at your own peril.
                raise KeyError("Duplicate prefix with different URI found.")
            ns[elem[0]] = "%s" % elem[1]
        elif event == "start":
            if root is None:
                root = elem 
    f.close()
    return et.ElementTree(root), ns

     
def render(DS,sosConfig):
    # Returning content of the SensorML
    
    try:
        #---parse xml
        tree, ns = parse_and_get_ns(DS.smlFile)
    except Exception as ex:
        raise Exception("sensorML description for procedure '%s' not found or corrupted! [%s]"%(DS.smlFile,ex))    
    
    #---map namespaces---
    try:
        register_namespace = et.register_namespace
        for key in ns:
            register_namespace(key,ns[key])
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
                    print >> sys.stderr, ("Failed to import ElementTree from any known place")
            for key in ns:
                _namespace_map[ns[key]] = key
        
    mns = {
            'xsi': "http://www.w3.org/2001/XMLSchema-instance" ,
            'sml': "http://www.opengis.net/sensorML/1.0.1", 
            'swe': "http://www.opengis.net/swe/1.0.1", 
            'xlink': "http://www.w3.org/1999/xlink", 
            'gml': 'http://www.opengis.net/gml'            
        }
    
    for n in mns.keys():
        try:
            ns[n]
        except:
            ns[n] = mns[n]
    
    
    #--- CREEATE FIELDS ACCORDING TO DATABASE OBSERVED_PROPERTIES 
    datarecord = tree.find("{%s}member/{%s}System/{%s}outputs/{%s}OutputList/{%s}output/{%s}DataRecord"
                        %(ns['sml'],ns['sml'],ns['sml'],ns['sml'],ns['sml'],ns['swe']) )
    
    
    datarecord.clear()
    datarecord.attrib["definition"] = "%stimeSeries" % (sosConfig.urn['dataType'])
    fieldT = et.SubElement(datarecord,"{%s}field" % ns["swe"])
    fieldT.attrib["name"] = "Time"
    time = et.SubElement(fieldT,"{%s}Time" % ns["swe"])
    time.attrib["definition"] = sosConfig.urn["time"]
    
    # Adding constraint for current allowed times
    if (not DS.stime == None) and (not DS.etime == None):
        constraint =  et.SubElement(time, "{%s}constraint" % ns['swe'])
        allowedTimes =  et.SubElement(constraint, "{%s}AllowedTimes" % ns['swe'])
        interval = et.SubElement(allowedTimes, "{%s}interval" % ns['swe'])
        interval.text = "%s %s" %(DS.stime.strftime("%Y-%m-%dT%H:%M:%S.%fZ"), DS.etime.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
    
    if DS.procedureType=="insitu-mobile-point": # Adding 3d coordinates observation
        
        cord = et.SubElement(datarecord,"{%s}field" % ns["swe"])
        cord.attrib["name"] = "x"
        quantity = et.SubElement(cord,"{%s}Quantity" % ns["swe"])
        quantity.attrib["definition"] = sosConfig.urn["refsystem"] + sosConfig.istsosepsg + ":x-position"
        
        cord = et.SubElement(datarecord,"{%s}field" % ns["swe"])
        cord.attrib["name"] = "y"
        quantity = et.SubElement(cord,"{%s}Quantity" % ns["swe"])
        quantity.attrib["definition"] = sosConfig.urn["refsystem"] + sosConfig.istsosepsg + ":y-position"
        
        cord = et.SubElement(datarecord,"{%s}field" % ns["swe"])
        cord.attrib["name"] = "z"
        quantity = et.SubElement(cord,"{%s}Quantity" % ns["swe"])
        quantity.attrib["definition"] = sosConfig.urn["refsystem"] + sosConfig.istsosepsg + ":z-position"
        
        
    for index,field in enumerate(DS.observedProperties):
        
        fieldQ = et.SubElement(datarecord,"{%s}field" % ns["swe"])
        fieldQ.attrib["name"] = field["name_opr"]
        quantity = et.SubElement(fieldQ,"{%s}Quantity" % ns["swe"])
        quantity.attrib["definition"] = field["def_opr"]
        
        if not (field["name_uom"]=="" or field["name_uom"]==None or field["name_uom"]=="NULL"):
            uom = et.SubElement(quantity,"{%s}uom" % ns["swe"])
            uom.attrib["code"] = field["name_uom"]
        """
        if not (field["desc_opr"]=="" or field["desc_opr"]==None or field["desc_opr"]=="NULL"):
            description = et.SubElement(quantity,"{%s}description" % ns["swe"])
            description.text = field["desc_opr"]
        """
        
        """
        # Handling constraint
        Permitted conigurations:
            {"role":"urn:x-ogc:def:classifiers:x-istsos:1.0:qualityIndexCheck:level0","min":"10"}
            {"role":"urn:x-ogc:def:classifiers:x-istsos:1.0:qualityIndexCheck:level0","max":"10"}
            {"role":"urn:x-ogc:def:classifiers:x-istsos:1.0:qualityIndexCheck:level0","interval":["-10","10"]}
            {"role":"urn:x-ogc:def:classifiers:x-istsos:1.0:qualityIndexCheck:level0","valueList":["1","2","3","4","5","6"]}
        """
        if not (field["constr_pro"]=="" or field["constr_pro"]==None):
            try:
                constraintObj = json.loads(field["constr_pro"])
                
                constraint = et.SubElement(quantity,"{%s}constraint" % ns["swe"])
                
                # Role attribute is not mandatory
                if "role" in constraintObj and constraintObj["role"]!="" and constraintObj["role"]!=None:
                    constraint.attrib[ "{%s}role" % ns['xlink'] ]= constraintObj["role"]
                    
                AllowedValues = et.SubElement(constraint, "{%s}AllowedValues" % ns['swe'])
                
                # Factory on constraint min/max/interval/valuelist
                if "interval" in constraintObj:
                    interval = et.SubElement(AllowedValues, "{%s}interval" % ns['swe'])
                    #interval.text = " ".join([ str(a) for a in constraintObj["interval"] ])
                    interval.text = constraintObj["interval"]
                    
                elif "valueList" in constraintObj:#.has_key("valueList"):
                    valueList = et.SubElement(AllowedValues, "{%s}valueList" % ns['swe'])
                    #valueList.text = ", ".join([ str(a) for a in constraintObj["valueList"] ])
                    valueList.text = constraintObj["valueList"]
                    
                elif "min" in constraintObj:#.has_key("min"):
                    amin = et.SubElement(AllowedValues, "{%s}min" % ns['swe'])
                    amin.text = constraintObj["min"]
                    
                elif "max" in constraintObj:#.has_key("max"):
                    amax = et.SubElement(AllowedValues, "{%s}max" % ns['swe'])
                    amax.text = constraintObj["max"]
                
            except Exception:
                raise Exception("Constraint definition invalid in the database for %s" % field["def_opr"])
    
    #verify that gml_id does not contain blanks 
    #(workaround to be corrected in future name sensor registration)
#    ------------------------------------------
#    NCName stands for "non-colonized name". 
#    NCName can be defined as an XML Schema regular expression [\i-[:]][\c-[:]]*
#    
#    So in plain English it would mean "any initial character, but not :". 
#    The whole regular expression reads as "One initial XML name character, 
#    but not a colon, followed by zero or more XML name characters, but not a colon."
#    
#    The practical restrictions of NCName are that it cannot contain several symbol characters
#    ------------------------------------------
    
    not_allowed_NCName = [' ', '!','"', '#', '$', '%', '&', '\'', 
                          '(', ')', '*', '+', ',', '/', ':', ';', 
                          '<', '=', '>', '?', '@', '[', '\\', ']', 
                          '^', '`', '{', '|', '}', '~']
                          
    location = tree.find("{%s}member/{%s}System/{%s}location"
                        %(ns['sml'],ns['sml'],ns['sml']) )
    for feature in location:
        for ch in not_allowed_NCName:
            if ch in feature.attrib['{%s}id' %ns['gml']]:
                feature.attrib['{%s}id' %ns['gml']] = feature.attrib['{%s}id' %ns['gml']].replace(ch,"_")

    # The unique identifier in the response document matches the procedure specified in the request
    system = tree.find("{%s}member/{%s}System" %(ns['sml'],ns['sml']))
    identification = tree.find("{%s}member/{%s}System/{%s}identification" %(ns['sml'],ns['sml'],ns['sml']))
    
    if not identification:
        identification = et.Element("{%s}identification" % ns["sml"])
        identifierList = et.SubElement(identification,"{%s}IdentifierList" % ns["sml"])
        identifier = et.SubElement(identifierList,"{%s}identifier" % ns["sml"])
        term = et.SubElement(identifier,"{%s}Term" % ns["sml"])
        term.attrib['definition'] = "urn:ogc:def:identifier:OGC:uniqueID"
        value = et.SubElement(term,"{%s}value" % ns["sml"])
        value.text = sosConfig.urn["procedure"]+system.attrib['{%s}id' %ns['gml']]
        system.insert(1,identification)
    else:
        identifierList = identification.find("{%s}IdentifierList" % ns["sml"])
        if not identifierList:
            identifierList = et.SubElement(identification,"{%s}IdentifierList" % ns["sml"])
            identifier = et.SubElement(identifierList,"{%s}identifier" % ns["sml"])
            term = et.SubElement(identifier,"{%s}Term" % ns["sml"])
            term.attrib['definition'] = "urn:ogc:def:identifier:OGC:uniqueID"
            value = et.SubElement(term,"{%s}value" % ns["sml"])
            value.text = sosConfig.urn["procedure"]+system.attrib['{%s}id' %ns['gml']]
#            system.insert(1,identification)
        else:
            identifiers = identifierList.findall("{%s}identifier" % ns["sml"])
            unique = False
            for identifier in identifiers:
                if identifier.find("{%s}Term" % ns["sml"]).attrib['definition'] == "urn:ogc:def:identifier:OGC:uniqueID":
                    unique = True
                    break
            if not unique:
                identifier = et.SubElement(identifierList,"{%s}identifier" % ns["sml"])
                term = et.SubElement(identifier,"{%s}Term" % ns["sml"])
                term.attrib['definition'] = "urn:ogc:def:identifier:OGC:uniqueID"
                value = et.SubElement(term,"{%s}value" % ns["sml"])
                value.text = sosConfig.urn["procedure"]+system.attrib['{%s}id' %ns['gml']]
#                system.insert(1,identification)
    
            
    
    
    root = tree.getroot()
    root.attrib["xmlns"]="http://www.opengis.net/sensorML/1.0.1"
    return """<?xml version="1.0" encoding="UTF-8"?>\n%s""" % et.tostring(root)
