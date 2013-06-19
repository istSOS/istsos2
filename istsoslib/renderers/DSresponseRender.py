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
        import traceback
        print >> sys.stderr, traceback.print_exc()
        raise sosException.SOSException(1,"sensorML description for procedure '%s' not found or corrupted! [%s]"%(DS.smlFile,ex))    
    
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
    #time.attrib["{%s}id" % ns["gml"] ] = str(0) # not valid against schema validation > TOREMOVE
    
    if (not DS.stime == None) and (not DS.etime == None):
        constraint =  et.SubElement(time, "{%s}constraint" % ns['swe'])
        allowedTimes =  et.SubElement(constraint, "{%s}AllowedTimes" % ns['swe'])
        interval = et.SubElement(allowedTimes, "{%s}interval" % ns['swe'])
        interval.text = "%s %s" %(DS.stime.strftime("%Y-%m-%dT%H:%M:%S.%f%z"), DS.etime.strftime("%Y-%m-%dT%H:%M:%S.%f%z"))
    
    #import pprint
    #pp = pprint.PrettyPrinter(indent=2)
    #pp.pprint(sosConfig)
    
    
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
        #quantity.attrib["{%s}id" % ns["gml"] ] = str(index+1) # not valid against schema validation > TOREMOVE
        
        if not (field["name_uom"]=="" or field["name_uom"]==None or field["name_uom"]=="NULL"):
            uom = et.SubElement(quantity,"{%s}uom" % ns["swe"])
            uom.attrib["code"] = field["name_uom"]
        """
        if not (field["desc_opr"]=="" or field["desc_opr"]==None or field["desc_opr"]=="NULL"):
            description = et.SubElement(quantity,"{%s}description" % ns["swe"])
            description.text = field["desc_opr"]
        """    
        if not (field["constr_pro"]=="" or field["constr_pro"]==None  or field["constr_pro"]=="NULL"):
            constraint = et.SubElement(quantity,"{%s}constraint" % ns["swe"])
            constraint.attrib["{%s}role" % ns['xlink']] = "urn:x-ogc:def:classifiers:x-istsos:1.0:qualityIndexCheck:level0"
            AllowedValues = et.SubElement(constraint,"{%s}AllowedValues" % ns["swe"])
            AllowedValuesList = field["constr_pro"].split(":")
            constraintType = et.SubElement( AllowedValues,"{%s}%s" %(ns["swe"],AllowedValuesList[0]) )
            constraintType.text = AllowedValuesList[1]
        
    root = tree.getroot()
    return et.tostring(root)
